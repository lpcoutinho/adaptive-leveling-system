"""Serviço de gerenciamento de quiz e correção de respostas."""

from uuid import UUID

from loguru import logger

from backend.domain.models.quiz import QuizAnswer, QuizSession, SessionStatus
from backend.infrastructure.repository.assessment_repository import get_assessment_by_id
from backend.infrastructure.repository.student_repository import save_quiz_session
from backend.infrastructure.student_cache import get_session, save_session
from backend.llm.evaluators.answer_evaluator import AnswerEvaluator


async def start_quiz(assessment_id: UUID, student_id: str = "anonymous") -> QuizSession:
    """Inicia uma nova sessão de quiz."""
    logger.info(f"Iniciando quiz para avaliação {assessment_id} (aluno: {student_id})...")
    assessment = await get_assessment_by_id(assessment_id)
    if not assessment:
        logger.error(f"Avaliação {assessment_id} não encontrada.")
        raise ValueError(f"Avaliação {assessment_id} não encontrada.")
    if not assessment.questions:
        logger.error(f"Avaliação {assessment_id} não possui questões.")
        raise ValueError("A avaliação não possui questões.")

    session = QuizSession(
        assessment_id=str(assessment_id),
        student_id=student_id,
        max_score=float(len(assessment.questions) * 100),
    )
    await save_session(session)
    logger.success(f"Quiz iniciado: sessão {session.id}.")
    return session


async def get_next_question(session_id: UUID) -> dict | None:
    """Retorna a próxima questão não respondida."""
    logger.info(f"Buscando próxima questão da sessão {session_id}...")
    session = await get_session(session_id)
    if not session or session.status != SessionStatus.IN_PROGRESS:
        logger.info(f"Sessão {session_id} inválida ou já finalizada. Retornando None.")
        return None

    assessment = await get_assessment_by_id(UUID(session.assessment_id))
    if not assessment:
        logger.error(f"Avaliação associada à sessão {session_id} não encontrada.")
        return None

    answered_ids = {a.question_id for a in session.answers}
    for q in assessment.questions:
        if str(q.id) not in answered_ids:
            logger.success(f"Próxima questão encontrada para sessão {session_id}.")
            return q.model_dump(mode="json")

    logger.info(f"Nenhuma questão pendente na sessão {session_id}.")
    return None


async def submit_answer(
    session_id: UUID,
    question_id: str,
    student_answer: str,
) -> tuple[QuizSession, QuizAnswer | None]:
    """Submete resposta e retorna a sessão. Adia avaliação de discursivas."""
    logger.info(f"Submetendo resposta para questão {question_id} na sessão {session_id}...")
    session = await get_session(session_id)
    if not session or session.status != SessionStatus.IN_PROGRESS:
        logger.error(f"Sessão {session_id} inválida ou já finalizada.")
        raise ValueError("Sessão inválida ou já finalizada.")

    assessment = await get_assessment_by_id(UUID(session.assessment_id))
    if not assessment:
        logger.error(f"Avaliação não encontrada para sessão {session_id}.")
        raise ValueError("Avaliação não encontrada.")

    question = next((q for q in assessment.questions if str(q.id) == question_id), None)
    if not question:
        logger.error(f"Questão {question_id} não encontrada na sessão {session_id}.")
        raise ValueError(f"Questão {question_id} não encontrada.")

    # Correção imediata apenas para múltipla escolha
    if question.type.value == "multiple_choice":
        eval_result = AnswerEvaluator.evaluate_mcq(student_answer, question.correct_answer)
        score = eval_result.score
        justification = eval_result.justification
    else:
        # Discursivas são marcadas como pendentes
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

    # Atualiza resposta na sessão (evita duplicados)
    session.answers = [a for a in session.answers if a.question_id != question_id]
    session.answers.append(answer)

    session.total_score = sum(a.score for a in session.answers)
    await save_session(session)
    logger.success(f"Resposta submetida para questão {question_id} na sessão {session_id}.")
    return session, answer


async def evaluate_pending_answers(
    session_id: UUID,
    pending: list[tuple[str, str]],
) -> dict[str, dict]:
    """Avalia respostas SA/Calc pendentes em lote via LLM."""
    logger.info(f"Avaliando {len(pending)} respostas pendentes na sessão {session_id}...")
    session = await get_session(session_id)
    if not session or session.status != SessionStatus.IN_PROGRESS:
        logger.error(f"Sessão {session_id} inválida ou já finalizada.")
        raise ValueError("Sessão inválida ou já finalizada.")

    assessment = await get_assessment_by_id(UUID(session.assessment_id))
    if not assessment:
        logger.error(f"Avaliação não encontrada para sessão {session_id}.")
        raise ValueError("Avaliação não encontrada.")

    questions_data = []
    for qid, student_answer in pending:
        question = next((q for q in assessment.questions if str(q.id) == qid), None)
        if not question:
            continue
        questions_data.append(
            {
                "question_id": qid,
                "question_text": question.text,
                "question_type": question.type.value,
                "expected_answer": question.correct_answer,
                "student_answer": student_answer,
            }
        )

    if not questions_data:
        logger.info("Nenhuma questão pendente para avaliar.")
        return {}

    evaluator = AnswerEvaluator()
    # Chama o novo método de avaliação em lote
    batch_result = await evaluator.evaluate_batch(questions_data)

    # Mapeia resultados por question_id
    results_map = {res.question_id: res for res in batch_result.results}

    # Atualiza as respostas na sessão
    for answer in session.answers:
        if answer.question_id in results_map:
            eval_item = results_map[answer.question_id]
            answer.score = eval_item.score
            answer.justification = eval_item.justification

    session.total_score = sum(a.score for a in session.answers)
    await save_session(session)
    logger.success(f"Avaliação em lote concluída para sessão {session_id}.")
    return {
        res.question_id: {"score": res.score, "justification": res.justification}
        for res in batch_result.results
    }


async def finish_quiz(session_id: UUID) -> QuizSession:
    """Finaliza o quiz e persiste no PostgreSQL."""
    logger.info(f"Finalizando quiz da sessão {session_id}...")
    session = await get_session(session_id)
    if not session:
        logger.error(f"Sessão {session_id} não encontrada.")
        raise ValueError("Sessão não encontrada.")

    session.status = SessionStatus.COMPLETED
    session.total_score = sum(a.score for a in session.answers)

    persisted = await save_quiz_session(session)
    logger.success(f"Quiz da sessão {session_id} finalizado com sucesso.")
    return persisted
