"""Página de quiz interativo com avaliação em lote ao final."""

import contextlib

import httpx
import streamlit as st

from frontend.app.config import get_frontend_settings

settings = get_frontend_settings()
API = f"{settings.api_url}/api/v1"


def _evaluate_mcq(student_answer: str, correct_answer: str) -> dict:
    """Avaliação determinística local para múltipla escolha."""
    correct = student_answer.strip().lower() == correct_answer.strip().lower()
    return {
        "score": 100.0 if correct else 0.0,
        "justification": "Resposta correta!" if correct else "Resposta incorreta.",
    }


st.title("🏁 Quiz Interativo")
st.markdown("Responda às questões para avaliar seu conhecimento.")

assessment = st.session_state.get("current_assessment")

if not assessment:
    st.warning("Nenhuma avaliação carregada. Gere uma avaliação primeiro.")
    if st.button("Ir para Avaliação"):
        st.switch_page("pages/3_📋_Assessment.py")
else:
    questions = assessment.get("questions", [])
    if not questions:
        st.error("A avaliação não contém questões.")
    else:
        total = len(questions)
        mode = st.session_state.get("quiz_mode")

        # --- TELA INICIAL ---
        if not mode:
            st.info(f"Este quiz contém **{total} questões**. Clique para começar!")
            if st.button("▶️ Começar Quiz", type="primary"):
                session_id = "local"
                try:
                    resp = httpx.post(
                        f"{API}/quiz/start",
                        json={"assessment_id": str(assessment["id"]), "student_id": "anonymous"},
                        timeout=10,
                    )
                    if resp.status_code == 201:
                        session_id = str(resp.json()["session_id"])
                except Exception:  # nosec
                    pass
                st.session_state.quiz_session_id = session_id
                st.session_state.quiz_current_idx = 0
                st.session_state.quiz_answers = {}  # Mapeia q_id -> answer_text
                st.session_state.quiz_mode = "answering"
                st.rerun()

        # --- RESPONDENDO ---
        elif mode == "answering":
            current_idx = st.session_state.get("quiz_current_idx", 0)

            if current_idx < total:
                q = questions[current_idx]
                q_id = str(q.get("id", current_idx))
                q_type = q.get("type", "")

                # Progresso
                progress_text = f"Questão {current_idx + 1} de {total}"
                st.progress((current_idx + 1) / total, text=progress_text)

                type_labels = {
                    "multiple_choice": "📝 Múltipla Escolha",
                    "short_answer": "✍️ Resposta Curta",
                    "calculation": "🧮 Cálculo",
                }
                st.markdown(f"### {type_labels.get(q_type, q_type)}")
                st.write(q.get("text", ""))

                # Recupera resposta anterior se houver
                prev_answer = st.session_state.quiz_answers.get(q_id, "")

                if q_type == "multiple_choice":
                    options = q.get("options", [])
                    # Encontra o índice da opção salva para pré-selecionar
                    try:
                        start_idx = options.index(prev_answer) if prev_answer in options else None
                    except ValueError:
                        start_idx = None
                    answer = (
                        st.radio("Selecione:", options, key=f"mc_{q_id}", index=start_idx) or ""
                    )
                elif q_type == "short_answer":
                    answer = (
                        st.text_area(
                            "Sua resposta:", key=f"sa_{q_id}", height=100, value=prev_answer
                        )
                        or ""
                    )
                else:  # calculation
                    answer = (
                        st.text_area(
                            "Resolução passo a passo:",
                            key=f"calc_{q_id}",
                            height=150,
                            value=prev_answer,
                        )
                        or ""
                    )

                col_a, col_b = st.columns([1, 1])
                with col_a:
                    if current_idx > 0 and st.button("◀️ Anterior"):
                        st.session_state.quiz_answers[q_id] = answer  # Salva antes de voltar
                        st.session_state.quiz_current_idx = current_idx - 1
                        st.rerun()
                with col_b:
                    label = "Finalizar e Avaliar 🏁" if current_idx == total - 1 else "Próxima ➡️"
                    if st.button(label, type="primary"):
                        st.session_state.quiz_answers[q_id] = answer  # Salva resposta
                        st.session_state.quiz_current_idx = current_idx + 1
                        st.rerun()

                st.caption(f"Status: {len(st.session_state.quiz_answers)} de {total} respondidas.")

            else:
                st.session_state.quiz_mode = "evaluating"
                st.rerun()

        # --- AVALIANDO (LOTE) ---
        elif mode == "evaluating":
            with st.spinner("A IA está avaliando suas respostas..."):
                all_answers = st.session_state.get("quiz_answers", {})
                session_id = st.session_state.get("quiz_session_id", "local")
                is_real = session_id != "local"

                final_results: dict[str, dict] = {}

                # 1. Avalia MCQ localmente
                for q in questions:
                    q_id = str(q.get("id", ""))
                    if q.get("type") == "multiple_choice":
                        ans = all_answers.get(q_id, "")
                        final_results[q_id] = _evaluate_mcq(ans, q.get("correct_answer", ""))

                # 2. Avalia SA/Calc via Backend (Batch)
                pending = [
                    {
                        "question_id": str(q.get("id", "")),
                        "student_answer": all_answers.get(str(q.get("id", "")), ""),
                    }
                    for q in questions
                    if q.get("type") != "multiple_choice"
                ]

                if pending and is_real:
                    try:
                        resp = httpx.post(
                            f"{API}/quiz/{session_id}/evaluate-pending",
                            json={"answers": pending},
                            timeout=60,
                        )
                        if resp.status_code == 200:
                            batch_data = resp.json()
                            for item in batch_data.get("results", []):
                                final_results[item["question_id"]] = {
                                    "score": item["score"],
                                    "justification": item["justification"],
                                }
                    except Exception as e:
                        st.error(f"Erro na avaliação em lote: {e}")

                # 3. Fallback para itens não avaliados
                for q in questions:
                    q_id = str(q.get("id", ""))
                    if q_id not in final_results:
                        ans = all_answers.get(q_id, "").strip()
                        msg = "Erro ao obter avaliação da IA." if ans else "Questão não respondida."
                        final_results[q_id] = {"score": 0.0, "justification": msg}

                st.session_state.quiz_results = final_results
                st.session_state.quiz_mode = "done"
                st.rerun()

        # --- RESULTADOS ---
        elif mode == "done":
            results = st.session_state.get("quiz_results", {})
            session_id = st.session_state.get("quiz_session_id", "local")

            # Persiste finalização no backend
            if session_id != "local":
                with contextlib.suppress(Exception):
                    httpx.post(f"{API}/quiz/{session_id}/finish", timeout=10)

            total_score = sum(r.get("score", 0.0) for r in results.values())
            max_score = total * 100
            percentage = (total_score / max_score * 100) if max_score > 0 else 0

            st.success("✅ Quiz concluído!")

            c1, c2 = st.columns(2)
            c1.metric("Pontuação Total", f"{total_score:.0f} / {max_score}")
            c2.metric("Aproveitamento", f"{percentage:.1f}%")

            st.divider()
            st.subheader("📋 Detalhamento das Respostas")

            for i, q in enumerate(questions):
                q_id = str(q.get("id", i))
                q_type = q.get("type", "")
                res = results.get(q_id, {"score": 0.0, "justification": "Sem dados"})

                score = res["score"]
                justification = res["justification"]

                color = "green" if score >= 80 else "orange" if score >= 50 else "red"
                icon = "✅" if score >= 80 else "⚠️" if score >= 50 else "❌"

                with st.expander(f"{icon} Questão {i + 1} ({q_type}) - Score: {score:.0f}/100"):
                    st.write(f"**Enunciado:** {q.get('text')}")
                    user_ans = st.session_state.quiz_answers.get(q_id, "(vazia)")
                    st.write(f"**Sua resposta:** {user_ans}")
                    st.write(f"**Gabarito:** {q.get('correct_answer')}")
                    st.markdown(f"**Justificativa da IA:** :{color}[{justification}]")

            st.divider()
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📊 Ver Diagnóstico de Prontidão", type="primary"):
                    st.switch_page("pages/6_🧠_Readiness.py")
            with col2:
                if st.button("🔄 Refazer este Quiz"):
                    keys = [
                        "quiz_session_id",
                        "quiz_current_idx",
                        "quiz_answers",
                        "quiz_results",
                        "quiz_mode",
                    ]
                    for k in keys:
                        st.session_state.pop(k, None)
                    st.rerun()
