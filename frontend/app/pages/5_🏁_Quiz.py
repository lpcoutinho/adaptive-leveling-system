"""Página de quiz interativo."""

import httpx
import streamlit as st

from frontend.app.config import get_frontend_settings

settings = get_frontend_settings()


def check_backend():
    try:
        r = httpx.get(f"{settings.api_url}/health/basic", timeout=5)
        return r.status_code == 200
    except Exception:
        return False


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
        session_id = st.session_state.get("quiz_session_id")
        current_idx = st.session_state.get("quiz_current_idx", 0)
        answers = st.session_state.get("quiz_answers", {})

        total = len(questions)

        if not session_id:
            st.info(f"Este quiz contém **{total} questões**. Clique para começar!")
            if st.button("▶️ Começar Quiz", type="primary"):
                st.session_state.quiz_session_id = "local"
                st.session_state.quiz_current_idx = 0
                st.session_state.quiz_answers = {}
                st.session_state.quiz_results = {}
                st.rerun()
        else:
            if current_idx >= total:
                st.success("✅ Quiz finalizado!")
                results = st.session_state.get("quiz_results", {})
                total_score = sum(r.get("score", 0) for r in results.values())
                max_score = total * 100
                pct = (total_score / max_score * 100) if max_score > 0 else 0

                st.metric("Pontuação Final", f"{total_score:.0f}/{max_score}", f"{pct:.1f}%")

                if st.button("📊 Ver Resultados"):
                    st.info("Fase 6 em desenvolvimento.")

                if st.button("🔄 Refazer Quiz"):
                    for k in [
                        "quiz_session_id",
                        "quiz_current_idx",
                        "quiz_answers",
                        "quiz_results",
                    ]:
                        st.session_state.pop(k, None)
                    st.rerun()
            else:
                q = questions[current_idx]
                q_id = str(q.get("id", current_idx))
                q_type = q.get("type", "")
                progress_text = f"Questão {current_idx + 1} de {total}"
                st.progress((current_idx + 1) / total, text=progress_text)

                type_labels = {
                    "multiple_choice": "📝 Múltipla Escolha",
                    "short_answer": "✍️ Resposta Curta",
                    "calculation": "🧮 Cálculo",
                }
                st.markdown(f"### {type_labels.get(q_type, q_type)}")
                st.write(q.get("text", ""))

                result = st.session_state.get("quiz_results", {}).get(q_id)
                if result:
                    st.success(f"Score: {result['score']:.0f}/100")
                    st.info(f"Justificativa: {result['justification']}")
                    if st.button("Próxima Questão ➡️"):
                        st.session_state.quiz_current_idx = current_idx + 1
                        st.rerun()
                else:
                    student_answer = ""
                    if q_type == "multiple_choice":
                        student_answer = (
                            st.radio(
                                "Selecione:", q.get("options", []), key=f"mc_{q_id}", index=None
                            )
                            or ""
                        )
                    elif q_type == "short_answer":
                        student_answer = (
                            st.text_area("Sua resposta:", key=f"sa_{q_id}", height=80) or ""
                        )
                    elif q_type == "calculation":
                        student_answer = (
                            st.text_area("Resolução:", key=f"calc_{q_id}", height=120) or ""
                        )

                    if st.button("✅ Responder", type="primary"):
                        if not student_answer.strip():
                            st.warning("Escreva uma resposta antes de continuar.")
                        else:
                            if q_type == "multiple_choice":
                                correct = q.get("correct_answer", "")
                                is_correct = (
                                    student_answer.strip().lower() == correct.strip().lower()
                                )
                                score = 100.0 if is_correct else 0.0
                                justification = "Correta!" if is_correct else "Incorreta."
                            else:
                                score = 0.0
                                justification = "Avaliação via LLM em implementação."

                            results = st.session_state.setdefault("quiz_results", {})
                            results[q_id] = {"score": score, "justification": justification}
                            st.session_state.quiz_results = results
                            st.rerun()
