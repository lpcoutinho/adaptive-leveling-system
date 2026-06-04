"""Serviço de gerenciamento de quiz e correção de respostas."""

from uuid import UUID

from backend.domain.models.quiz import QuizAnswer, QuizSession, SessionStatus
from backend.infrastructure.repository.assessment_repository import get_assessment_by_id
from backend.infrastructure.repository.student_repository import save_quiz_session
from backend.infrastructure.student_cache import get_session, save_session
from backend.llm.evaluators.answer_evaluator import AnswerEvaluator


async def start_quiz(assessment_id: UUID, student_id: str = "anonymous") -> QuizSession:
    """Inicia uma nova sessão de quiz."""
    assessment = await get_assessment_by_id(assessment_id)
    if not assessment:
        raise ValueError(f"Avaliação {assessment_id} não encontrada.")
    if not assessment.questions:
        raise ValueError("A avaliação não possui questões.")

    session = QuizSession(
        assessment_id=str(assessment_id),
        student_id=student_id,
        max_score=float(len(assessment.questions) * 100),
    )
    await save_session(session)
    return session


async def get_next_question(session_id: UUID) -> dict | None:
    """Retorna a próxima questão não respondida."""
    session = await get_session(session_id)
    if not session or session.status != SessionStatus.IN_PROGRESS:
        return None

    assessment = await get_assessment_by_id(UUID(session.assessment_id))
    if not assessment:
        return None

    answered_ids = {a.question_id for a in session.answers}
    for q in assessment.questions:
        if str(q.id) not in answered_ids:
            return q.model_dump(mode="json")

    return None


async def submit_answer(
    session_id: UUID,
    question_id: str,
    student_answer: str,
) -> tuple[QuizSession, QuizAnswer | None]:
    """Submete uma única resposta (opcional, usado para auto-save)."""
    session = await get_session(session_id)
    if not session or session.status != SessionStatus.IN_PROGRESS:
        raise ValueError("Sessão inválida ou já finalizada.")

    assessment = await get_assessment_by_id(UUID(session.assessment_id))
    if not assessment:
        raise ValueError("Avaliação não encontrada.")

    question = next((q for q in assessment.questions if str(q.id) == question_id), None)
    if not question:
        raise ValueError(f"Questão {question_id} não encontrada.")

    # Correção imediata apenas para MCQ
    if question.type.value == "multiple_choice":
        eval_result = AnswerEvaluator.evaluate_mcq(student_answer, question.correct_answer)
        score = eval_result.score
        justification = eval_result.justification
    else:
        score = 0.0
        justification = "Pendente de avaliação pela IA."

    answer = QuizAnswer(
        question_id=question_id,
        question_type=question.type.value,
        student_answer=student_answer,
        correct_answer=question.correct_answer,
        score=score,
        justification=justification,
    )

    session.answers = [a for a in session.answers if a.question_id != question_id]
    session.answers.append(answer)
    session.total_score = sum(a.score for a in session.answers)
    await save_session(session)

    return session, answer


async def evaluate_pending_answers(
    session_id: UUID,
    all_submitted_answers: list[tuple[str, str]],
) -> dict[str, dict]:
    """Avalia todas as respostas da sessão em lote e persiste no cache."""
    session = await get_session(session_id)
    if not session or session.status != SessionStatus.IN_PROGRESS:
        raise ValueError("Sessão inválida ou já finalizada.")

    assessment = await get_assessment_by_id(UUID(session.assessment_id))
    if not assessment:
        raise ValueError("Avaliação não encontrada.")

    final_answers: list[QuizAnswer] = []
    discursive_to_evaluate = []

    # 1. Processa cada resposta submetida
    for qid, student_answer in all_submitted_answers:
        question = next((q for q in assessment.questions if str(q.id) == qid), None)
        if not question:
            continue

        if question.type.value == "multiple_choice":
            # Avaliação MCQ é rápida e local
            res = AnswerEvaluator.evaluate_mcq(student_answer, question.correct_answer)
            final_answers.append(
                QuizAnswer(
                    question_id=qid,
                    question_type=question.type.value,
                    student_answer=student_answer,
                    correct_answer=question.correct_answer,
                    score=res.score,
                    justification=res.justification,
                )
            )
        else:
            # Prepara para enviar ao LLM em lote
            discursive_to_evaluate.append(
                {
                    "question_id": qid,
                    "question_text": question.text,
                    "question_type": question.type.value,
                    "expected_answer": question.correct_answer,
                    "student_answer": student_answer,
                }
            )

    # 2. Chama o LLM para as discursivas se houver
    if discursive_to_evaluate:
        evaluator = AnswerEvaluator()
        batch_result = await evaluator.evaluate_batch(discursive_to_evaluate)

        results_map = {res.question_id: res for res in batch_result.results}

        for item in discursive_to_evaluate:
            qid = item["question_id"]
            eval_item = results_map.get(qid)
            final_answers.append(
                QuizAnswer(
                    question_id=qid,
                    question_type=item["question_type"],
                    student_answer=item["student_answer"],
                    correct_answer=item["expected_answer"],
                    score=eval_item.score if eval_item else 0.0,
                    justification=eval_item.justification if eval_item else "Erro na avaliação.",
                )
            )

    # 3. Atualiza a sessão com TODAS as respostas processadas
    session.answers = final_answers
    session.total_score = sum(a.score for a in session.answers)
    await save_session(session)

    return {
        a.question_id: {"score": a.score, "justification": a.justification} for a in session.answers
    }


async def finish_quiz(session_id: UUID) -> QuizSession:
    """Finaliza o quiz e persiste definitivamente no PostgreSQL."""
    session = await get_session(session_id)
    if not session:
        # Se não está no cache, tenta no banco (pode já estar finalizada)
        from backend.infrastructure.repository.student_repository import get_quiz_session

        db_session = await get_quiz_session(session_id)
        if db_session:
            return db_session
        raise ValueError("Sessão não encontrada.")

    session.status = SessionStatus.COMPLETED
    # Recalcula score final por segurança
    session.total_score = sum(a.score for a in session.answers)

    # Salva no PostgreSQL
    persisted = await save_quiz_session(session)

    # Limpa cache após persistência
    from backend.infrastructure.student_cache import delete_session

    await delete_session(session_id)

    return persisted
