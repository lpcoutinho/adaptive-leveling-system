"""Página de orquestração de workflow com LangGraph com Quiz embutido."""

import httpx
import streamlit as st

from frontend.app.config import get_frontend_settings

settings = get_frontend_settings()
API = f"{settings.api_url}/api/v1"

st.set_page_config(page_title="Workflow", page_icon="⚙️", layout="wide")

st.title("⚙️ Orquestração de Workflow")
st.markdown("Acompanhe e interaja com o percurso educacional automatizado.")

if "last_pdf_id" not in st.session_state or not st.session_state.last_pdf_id:
    st.warning("⚠️ Nenhum PDF carregado. Vá para a página de Upload primeiro.")
    if st.button("Ir para Upload"):
        st.switch_page("pages/1_📄_Upload.py")
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
        st.session_state.pop("wf_quiz_answers", None)
        st.rerun()

# 2. Acompanhamento do Workflow
if "current_workflow_id" in st.session_state:
    wid = st.session_state.current_workflow_id
    status_data = _get_workflow_status(wid)

    if status_data:
        status = status_data.get("status", "unknown")
        current_node = status_data.get("current_node", "START")
        state = status_data.get("state", {})

        st.subheader(f"Status: {status.upper()}")

        # Mapa visual do grafo
        nodes = ["extract", "assessment", "quiz", "readiness", "leveling"]
        cols = st.columns(len(nodes))
        for i, node in enumerate(nodes):
            with cols[i]:
                is_current = node == current_node
                label = f"**{node.upper()}**" if is_current else node.upper()
                border = "3px solid #FF4B4B" if is_current else "1px solid #ddd"
                bg = "#fff1f1" if is_current else "#f9f9f9"
                st.markdown(
                    f"<div style='text-align:center; padding:10px; border:{border}; "
                    f"background-color:{bg}; border-radius:5px;'>{label}</div>",
                    unsafe_allow_html=True,
                )

        st.divider()

        # --- LÓGICA DE INTERAÇÃO (QUIZ EMBUTIDO) ---

        if status == "awaiting_input" and current_node == "quiz":
            st.markdown("### 📝 Hora do Quiz Diagnóstico")
            st.write("A IA gerou as questões abaixo para validar seu conhecimento base.")

            assessment = state.get("assessment", {})
            questions = assessment.get("questions", [])
            session_id = state.get("session_id")

            if not questions:
                st.error("Erro: Nenhuma questão encontrada no estado do workflow.")
            else:
                if "wf_quiz_idx" not in st.session_state:
                    st.session_state.wf_quiz_idx = 0
                    st.session_state.wf_quiz_answers = {}

                idx = st.session_state.wf_quiz_idx
                total = len(questions)

                if idx < total:
                    q = questions[idx]
                    q_id = str(q.get("id", idx))

                    st.progress((idx + 1) / total, text=f"Questão {idx + 1} de {total}")
                    st.markdown(f"**{q.get('type', '').upper()}**: {q.get('text')}")

                    prev = st.session_state.wf_quiz_answers.get(q_id, "")

                    if q.get("type") == "multiple_choice":
                        options = q.get("options", [])
                        ans = st.radio(
                            "Sua resposta:",
                            options,
                            index=options.index(prev) if prev in options else None,
                            key=f"q_{idx}",
                        )
                    else:
                        ans = st.text_area("Sua resposta:", value=prev, key=f"q_{idx}")

                    c1, c2 = st.columns(2)
                    if idx > 0 and c1.button("◀️ Anterior"):
                        st.session_state.wf_quiz_answers[q_id] = ans
                        st.session_state.wf_quiz_idx -= 1
                        st.rerun()

                    label = "Finalizar Quiz 🏁" if idx == total - 1 else "Próxima Questão ➡️"
                    if c2.button(label, type="primary"):
                        st.session_state.wf_quiz_answers[q_id] = ans
                        st.session_state.wf_quiz_idx += 1
                        st.rerun()

                else:
                    # Quiz finalizado no frontend -> Processar no backend
                    with st.spinner("IA avaliando respostas e retomando workflow..."):
                        try:
                            # 1. Avalia em lote
                            payload = [
                                {"question_id": k, "student_answer": v}
                                for k, v in st.session_state.wf_quiz_answers.items()
                            ]
                            httpx.post(
                                f"{API}/quiz/{session_id}/evaluate-pending",
                                json={"answers": payload},
                                timeout=60,
                            )
                            # 2. Finaliza sessão
                            httpx.post(f"{API}/quiz/{session_id}/finish", timeout=10)
                            # 3. Retoma Workflow
                            httpx.post(f"{API}/workflow/{wid}/resume", timeout=20)

                            st.session_state.pop("wf_quiz_idx", None)
                            st.session_state.pop("wf_quiz_answers", None)
                            st.success("Respostas processadas! Workflow retomado.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao processar quiz: {e}")
                            if st.button("Tentar Novamente"):
                                st.rerun()

        elif status == "completed":
            st.balloons()
            st.success("✅ **Percurso Automático Concluído!**")
            st.write("A IA analisou seu desempenho e já preparou o diagnóstico e nivelamento.")

            c1, c2 = st.columns(2)
            if c1.button("🧠 Ver Diagnóstico", use_container_width=True):
                st.session_state["quiz_session_id"] = state.get("session_id")
                st.session_state["current_assessment"] = state.get("assessment")
                st.switch_page("pages/6_🧠_Readiness.py")
            if c2.button("📚 Ir para Nivelamento", type="primary", use_container_width=True):
                st.session_state["quiz_session_id"] = state.get("session_id")
                st.session_state["current_readiness_id"] = state.get("readiness_id")
                st.switch_page("pages/7_📚_Leveling.py")

        elif status == "failed":
            st.error(f"❌ O processamento falhou: {status_data.get('error', 'Erro desconhecido')}")
            if st.button("Reiniciar Workflow"):
                st.session_state.pop("current_workflow_id", None)
                st.rerun()

        else:
            st.write("⏳ A IA está trabalhando no processamento automático...")
            st.write(f"Nó atual: **{current_node.upper()}**")
            if st.button("🔄 Atualizar Status Manualmente"):
                st.rerun()

            # Auto-refresh simples
            import time

            time.sleep(2)
            st.rerun()

    else:
        st.error("Não foi possível recuperar o status do workflow.")
