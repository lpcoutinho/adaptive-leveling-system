"""Página de upload de aulas em PDF."""

import httpx
import streamlit as st

from frontend.app.config import get_frontend_settings

settings = get_frontend_settings()


def upload_pdf(file):
    """Envia o arquivo PDF para o backend."""
    try:
        files = {"file": (file.name, file.getvalue(), "application/pdf")}
        response = httpx.post(f"{settings.api_url}/api/v1/pdf/upload", files=files, timeout=30.0)
        return response
    except Exception as e:
        st.error(f"Erro de conexão com o servidor: {e}")
        return None


st.title("📄 Upload de Aula")
st.write("Selecione um arquivo PDF de aula para extração de pré-requisitos.")

uploaded_file = st.file_uploader("Escolha um arquivo PDF", type="pdf")

if uploaded_file is not None:
    st.info(f"Arquivo selecionado: {uploaded_file.name} ({uploaded_file.size / 1024:.2f} KB)")

    if st.button("🚀 Processar PDF"):
        with st.spinner("Enviando e extraindo texto..."):
            response = upload_pdf(uploaded_file)

            if response and response.status_code == 201:
                data = response.json()
                st.session_state["last_pdf_id"] = data["id"]
                st.session_state["last_pdf_hash"] = data["hash"]
                st.rerun()

            elif response:
                error_detail = response.json().get("detail", "Erro desconhecido")
                st.error(f"Erro no processamento: {error_detail}")

if st.session_state.get("last_pdf_id"):
    pdf_id = st.session_state["last_pdf_id"]
    hash_ = st.session_state["last_pdf_hash"]
    st.success("✅ PDF processado com sucesso!")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("ID do Documento", str(pdf_id)[:8] + "...")
    with col2:
        st.metric("Hash SHA-256", str(hash_)[:10] + "...")

    if st.button("Ir para Próxima Etapa (Pré-requisitos)"):
        st.switch_page("pages/2_🧠_Prerequisites.py")
