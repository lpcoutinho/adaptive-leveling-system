"""Página de orquestração de workflow com LangGraph com Quiz embutido."""

from typing import Any

import httpx
import streamlit as st

from frontend.app.config import get_frontend_settings

settings = get_frontend_settings()
API = f"{settings.api_url}/api/v1"

st.set_page_config(page_title="Workflow", page_icon="⚙️", layout="wide")

st.title("⚙️ Orquestração de Workflow")
st.markdown("Acompanhe e interaja com o percurso educacional automatizado.")

if "last_pdf_id" not in st.session_state or not st.session_state.last_pdf_id:
    st.warning("⚠️ Nenhum PDF carregado. Vá para a página inicial primeiro.")
    if st.button("Ir para Home"):
        st.switch_page("0_🏠_Home.py")
    st.stop()

pdf_id = st.session_state.last_pdf_id


def _get_workflow_status(workflow_id: str):
    """Busca o status atual do workflow no backend."""
    try:
        resp = httpx.get(f"{API}/workflow/{workflow_id}", timeout=10)
        if resp.status_code == 200:
            return resp.json()
        return None
    except Exception:
        return None


def _start_workflow(pdf_id: str):
    """Inicia um novo workflow para o PDF."""
    try:
        resp = httpx.post(f"{API}/workflow/execute", json={"pdf_id": pdf_id}, timeout=10)
        if resp.status_code == 201:
            return resp.json()["workflow_id"]
        return None
    except Exception as e:
        st.error(f"Erro ao iniciar workflow: {e}")
        return None


# --- UI DA PÁGINA ---

st.info(f"Analisando Documento ID: {pdf_id}")

# 1. Início do Workflow
if "current_workflow_id" not in st.session_state and st.button(
    "🚀 Iniciar Processamento Automático", type="primary"
):
    wid = _start_workflow(str(pdf_id))
    if wid:
        st.session_state.current_workflow_id = wid
        st.session_state.pop("wf_quiz_idx", None)
        st.session_state.wf_quiz_answers = {}
        st.rerun()

# 2. Acompanhamento do Workflow
if "current_workflow_id" in st.session_state:
    wid = st.session_state.current_workflow_id
    status_data = _get_workflow_status(wid)

    if status_data:
        status = status_data.get("status", "unknown")
        current_node = status_data.get("current_node", "START")
        # O estado pode estar no topo ou aninhado
        state = status_data.get("state") or status_data

        st.subheader(f"Status: {status.upper()}")

        # Mapa visual do grafo com cores corrigidas para visibilidade
        nodes = ["extract", "assessment", "quiz", "readiness", "leveling"]
        cols = st.columns(len(nodes))
        for i, node in enumerate(nodes):
            with cols[i]:
                is_current = node == current_node
                label = f"**{node.upper()}**" if is_current else node.upper()

                # Cores estritas para garantir leitura em temas claros/escuros
                if is_current:
                    border = "3px solid #FF4B4B"
                    bg = "#FF4B4B"
                    text_color = "white"
                else:
                    border = "1px solid #ddd"
                    bg = "#f0f2f6"
                    text_color = "#31333F"

                st.markdown(
                    f"<div style='text-align:center; padding:10px; border:{border}; "
                    f"background-color:{bg}; color:{text_color}; border-radius:5px; "
                    f"font-weight: bold;'>{label}</div>",
                    unsafe_allow_html=True,
                )

        st.divider()

        # --- LÓGICA DE INTERAÇÃO (QUIZ EMBUTIDO) ---

        if status == "awaiting_input" and current_node == "quiz":
            st.markdown("### 📝 Hora do Quiz Diagnóstico")
            st.write("A IA gerou as questões abaixo para validar seu conhecimento base.")

            # Busca assessment de forma resiliente
            assessment = state.get("assessment") or {}
            questions = assessment.get("questions") or []
            session_id = state.get("session_id") or state.get("quiz_session", {}).get("id")

            if not questions:
                st.error("Erro: Nenhuma questão encontrada no estado do workflow.")
                if st.button("🔄 Tentar recuperar questões"):
                    st.rerun()
            else:
                if "wf_quiz_idx" not in st.session_state:
                    st.session_state.wf_quiz_idx = 0
                if "wf_quiz_answers" not in st.session_state:
                    st.session_state.wf_quiz_answers = {}

                idx = st.session_state.wf_quiz_idx
                total = len(questions)

                if idx < total:
                    q = questions[idx]
                    q_id = str(q.get("id", idx))

                    st.progress((idx + 1) / total, text=f"Questão {idx + 1} de {total}")

                    # Estilização da pergunta
                    st.info(f"**Tipo: {q.get('type', '').replace('_', ' ').title()}**")
                    st.markdown(f"#### {q.get('text')}")

                    prev = st.session_state.wf_quiz_answers.get(q_id, "")

                    if q.get("type") == "multiple_choice":
                        options = q.get("options", [])
                        try:
                            def_idx = options.index(prev) if prev in options else None
                        except ValueError:
                            def_idx = None
                        ans = st.radio("Sua resposta:", options, index=def_idx, key=f"q_{idx}")
                    else:
                        ans = st.text_area("Sua resposta:", value=prev, key=f"q_{idx}", height=150)

                    c1, c2 = st.columns(2)
                    with c1:
                        if idx > 0 and st.button("◀️ Anterior", use_container_width=True):
                            st.session_state.wf_quiz_answers[q_id] = ans
                            st.session_state.wf_quiz_idx -= 1
                            st.rerun()

                    with c2:
                        label = "Finalizar Quiz 🏁" if idx == total - 1 else "Próxima Questão ➡️"
                        if st.button(label, type="primary", use_container_width=True):
                            st.session_state.wf_quiz_answers[q_id] = ans
                            st.session_state.wf_quiz_idx += 1
                            st.rerun()
                else:
                    # Quiz finalizado -> Avaliar e mostrar resultados antes de continuar
                    if "wf_quiz_results" not in st.session_state:
                        # Primeira vez após finalizar: avaliar as respostas
                        with st.spinner("🤖 IA avaliando suas respostas..."):
                            try:
                                answers_map = st.session_state.wf_quiz_answers
                                payload = [
                                    {"question_id": k, "student_answer": v}
                                    for k, v in answers_map.items()
                                ]

                                # Chamada de avaliação
                                resp = httpx.post(
                                    f"{API}/quiz/{session_id}/evaluate-pending",
                                    json={"answers": payload},
                                    timeout=60,
                                )
                                st.session_state.wf_quiz_results = resp.json()
                                st.session_state.wf_quiz_session_id = session_id
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro ao avaliar quiz: {e}")
                                if st.button("Tentar Novamente"):
                                    st.rerun()
                    else:
                        # Mostrar resultados
                        st.markdown("### 📊 Seus Resultados")
                        st.write("A IA avaliou suas respostas. Confira abaixo:")

                        results = st.session_state.wf_quiz_results.get("results", [])

                        # Calcular estatísticas
                        total_score = sum(r.get("score", 0) for r in results)
                        avg_score = total_score / len(results) if results else 0

                        # Mostrar estatísticas
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Questões Respondidas", len(results))
                        with col2:
                            st.metric("Score Médio", f"{avg_score:.1f}%")
                        with col3:
                            score_color = (
                                "🟢" if avg_score >= 70 else "🟡" if avg_score >= 50 else "🔴"
                            )
                            status_label = "Aprovado" if avg_score >= 70 else "Precisa Estudar"
                            st.metric("Status", f"{score_color} {status_label}")

                        st.divider()

                        # Mostrar detalhes de cada questão
                        for i, result in enumerate(results):
                            q_id = result.get("question_id")
                            # Encontrar a pergunta original
                            question: dict[str, Any] = next(
                                (q for q in questions if str(q.get("id")) == q_id), {}
                            )

                            with st.expander(
                                f"Questão {i + 1}: {question.get('text', 'N/A')[:60]}...",
                                expanded=i == 0,
                            ):
                                st.markdown("**Sua resposta:**")
                                st.info(st.session_state.wf_quiz_answers.get(q_id, "N/A"))

                                score = result.get("score", 0)
                                score_color = (
                                    "green" if score >= 70 else "orange" if score >= 50 else "red"
                                )
                                st.markdown(f"**Score:** :{score_color}[**{score:.1f}%**]")

                                st.markdown("**Justificativa da IA:**")
                                st.success(result.get("justification", "Sem justificativa."))

                        st.divider()

                        # Botões de ação
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("🔄 Refazer Quiz", use_container_width=True):
                                st.session_state.pop("wf_quiz_results", None)
                                st.session_state.pop("wf_quiz_answers", None)
                                st.session_state.wf_quiz_idx = 0
                                st.rerun()

                        with col2:
                            if st.button(
                                "▶️ Continuar Workflow IA", type="primary", use_container_width=True
                            ):
                                with st.spinner("IA processando diagnóstico e nivelamento..."):
                                    try:
                                        session_id = st.session_state.wf_quiz_session_id
                                        # Finaliza sessão
                                        httpx.post(f"{API}/quiz/{session_id}/finish", timeout=10)
                                        # Retoma Workflow
                                        httpx.post(f"{API}/workflow/{wid}/resume", timeout=20)

                                        # Limpar estado do quiz
                                        st.session_state.pop("wf_quiz_idx", None)
                                        st.session_state.pop("wf_quiz_answers", None)
                                        st.session_state.pop("wf_quiz_results", None)
                                        st.session_state.pop("wf_quiz_session_id", None)

                                        st.success("Workflow retomado!")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Erro ao continuar workflow: {e}")

        elif status == "completed":
            st.balloons()
            st.success("✅ **Percurso Automático Concluído!**")
            st.write("A IA analisou seu desempenho e já preparou o diagnóstico e nivelamento.")

            c1, c2 = st.columns(2)
            if c1.button("🧠 Ver Diagnóstico", use_container_width=True):
                st.session_state["quiz_session_id"] = state.get("session_id") or state.get(
                    "quiz_session", {}
                ).get("id")
                st.session_state["current_assessment"] = state.get("assessment")
                st.switch_page("pages/5_🧠_Readiness.py")
            if c2.button("📚 Ir para Nivelamento", type="primary", use_container_width=True):
                st.session_state["quiz_session_id"] = state.get("session_id") or state.get(
                    "quiz_session", {}
                ).get("id")
                st.session_state["current_readiness_id"] = state.get("readiness_id")
                st.switch_page("pages/6_📚_Leveling.py")

        elif status == "failed":
            st.error(f"❌ O processamento falhou: {status_data.get('error', 'Erro desconhecido')}")
            if st.button("Reiniciar Workflow"):
                st.session_state.pop("current_workflow_id", None)
                st.session_state.pop("wf_quiz_idx", None)
                st.session_state.pop("wf_quiz_answers", None)
                st.rerun()

        else:
            st.write("⏳ A IA está trabalhando no processamento automático...")
            st.write(f"Nó atual: **{current_node.upper()}**")

            # Auto-refresh para acompanhar o progresso
            import time

            time.sleep(2)
            st.rerun()

    else:
        st.error("Não foi possível recuperar o status do workflow.")
