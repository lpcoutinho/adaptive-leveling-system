import streamlit as st

st.set_page_config(page_title="Workflow Completo", page_icon="⚙️", layout="wide")

st.title("⚙️ Análise Completa com Workflow")

st.markdown(
    """
    Execute o pipeline completo do Adaptive Leveling System em um único fluxo:
    1. **📄 Upload** → 2. **🧠 Extrair Pré-requisitos** → 3. **📋 Gerar Avaliação**
    4. **🏁 Quiz** → 5. **🔍 Analisar Prontidão** → 6. **📚 Plano de Nivelamento**
    """
)

if "current_pdf_id" not in st.session_state:
    st.session_state["current_pdf_id"] = None
if "workflow_state" not in st.session_state:
    st.session_state["workflow_state"] = None

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Configuração")
    uploaded_file = st.file_uploader("Upload do PDF da aula", type=["pdf"])
    if uploaded_file:
        pdf_id = f"mock-{hash(uploaded_file.name)}"
        st.session_state["current_pdf_id"] = pdf_id
        st.success(f"PDF carregado: {uploaded_file.name}")

    if st.session_state["current_pdf_id"] and st.button(
        "🚀 Iniciar Análise Completa", type="primary"
    ):
        st.session_state["workflow_state"] = {
            "pdf_id": st.session_state["current_pdf_id"],
            "status": "in_progress",
            "current_node": "extract",
            "progress": 0.0,
            "steps_completed": [],
            "active": True,
        }

with col2:
    wf = st.session_state.get("workflow_state")
    if wf and wf.get("active"):
        st.subheader("📊 Progresso do Workflow")

        steps = [
            ("extract", "Extração de Pré-requisitos", 0.2),
            ("assessment", "Geração de Avaliação", 0.4),
            ("quiz_await", "Quiz (aguardando aluno)", 0.6),
            ("readiness", "Análise de Prontidão", 0.8),
            ("leveling", "Plano de Nivelamento", 1.0),
        ]

        import time

        progress_bar = st.progress(0.0)
        status_text = st.empty()

        completed = wf.get("steps_completed", [])
        current = wf.get("current_node", "extract")

        for step_name, step_label, step_progress in steps:
            step_done = step_name in completed
            step_active = step_name == current and not step_done

            if step_done:
                st.success(f"✅ {step_label}")
            elif step_active:
                st.info(f"⏳ {step_label}...")
                progress_bar.progress(step_progress)
                status_text.text(f"Executando: {step_label}")
                time.sleep(0.3)
                completed.append(step_name)
                st.session_state["workflow_state"]["steps_completed"] = completed
                st.rerun()
            else:
                st.markdown(f"⏸️ {step_label}")

        if len(completed) >= len(steps):
            st.balloons()
            st.success("🎉 Workflow concluído!")
            wf["status"] = "completed"
            wf["active"] = False
            progress_bar.progress(1.0)
            status_text.text("Workflow concluído!")

            st.divider()
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                if st.button("📋 Ver Avaliação"):
                    st.switch_page("pages/3_📋_Assessment.py")
            with col_b:
                if st.button("🧠 Ver Prontidão"):
                    st.switch_page("pages/6_🧠_Readiness.py")
            with col_c:
                if st.button("📚 Ver Plano"):
                    st.switch_page("pages/7_📚_Leveling.py")
    elif wf and not wf.get("active") and wf.get("status") == "completed":
        st.success("✅ Workflow concluído!")
        st.metric("Progresso", "100%")
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            if st.button("📋 Ver Avaliação"):
                st.switch_page("pages/3_📋_Assessment.py")
        with col_b:
            if st.button("🧠 Ver Prontidão"):
                st.switch_page("pages/6_🧠_Readiness.py")
        with col_c:
            if st.button("📚 Ver Plano"):
                st.switch_page("pages/7_📚_Leveling.py")
    else:
        st.info("Faça upload de um PDF e clique em 'Iniciar Análise Completa'.")
