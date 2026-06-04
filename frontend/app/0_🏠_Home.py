"""Aplicação principal — Página inicial do Adaptive Leveling System."""

import httpx
import streamlit as st

from frontend.app.config import get_frontend_settings

settings = get_frontend_settings()
API_BASE = f"{settings.api_url}/api/v1"

st.set_page_config(page_title=settings.app_title, page_icon="🎓", layout="wide")

# Inicialização do estado global
if "last_pdf_id" not in st.session_state:
    st.session_state.last_pdf_id = None
if "last_pdf_hash" not in st.session_state:
    st.session_state.last_pdf_hash = None


def upload_pdf(file):
    """Envia o arquivo PDF para o backend."""
    try:
        files = {"file": (file.name, file.getvalue(), "application/pdf")}
        response = httpx.post(f"{API_BASE}/pdf/upload", files=files, timeout=30.0)
        return response
    except Exception as e:
        st.error(f"Erro de conexão com o servidor: {e}")
        return None


st.title("🎓 Adaptive Leveling System")
st.subheader("Plataforma de nivelamento educacional baseada em IA")

st.write(
    "Esta plataforma utiliza Inteligência Artificial para transformar "
    "suas aulas em percursos adaptativos:"
)
st.write("1. **Analise** o conteúdo profundo de aulas em PDF.")
st.write("2. **Identifique** pré-requisitos fundamentais que o aluno já deveria dominar.")
st.write("3. **Avalie** a prontidão real através de quizes diagnósticos inteligentes.")
st.write("4. **Gere** material de nivelamento personalizado para fechar gaps específicos.")

st.divider()

# --- ÁREA DE UPLOAD ---
st.markdown("### 📄 Passo 1: Carregar Aula")
uploaded_file = st.file_uploader("Selecione um arquivo PDF de aula para começar", type="pdf")

if uploaded_file is not None:
    st.info(f"Arquivo selecionado: {uploaded_file.name} ({uploaded_file.size / 1024:.2f} KB)")

    if st.button("🚀 Processar Documento", type="primary"):
        with st.spinner("Enviando e extraindo inteligência do PDF..."):
            response = upload_pdf(uploaded_file)

            if response and response.status_code == 201:
                data = response.json()
                st.session_state["last_pdf_id"] = data["id"]
                st.session_state["last_pdf_hash"] = data["hash"]
                st.success("✅ Documento processado com sucesso!")
            elif response:
                error_detail = response.json().get("detail", "Erro desconhecido")
                st.error(f"Erro no processamento: {error_detail}")

# --- NAVEGAÇÃO APÓS UPLOAD ---
if st.session_state.last_pdf_id:
    st.divider()
    st.markdown("### 🧭 Passo 2: Escolha seu percurso")
    st.write("Como você deseja prosseguir com este documento?")

    col_manual, col_auto = st.columns(2)

    with col_manual, st.container(border=True):
        st.markdown("#### 🛠️ Fluxo Passo-a-Passo")
        st.write(
            "Tenha controle total sobre cada etapa: extração, geração de questões e diagnóstico."
        )
        if st.button("Seguir Manualmente", use_container_width=True):
            st.switch_page("pages/2_🧠_Prerequisites.py")

    with col_auto, st.container(border=True):
        st.markdown("#### ⚙️ Piloto Automático (Workflow)")
        st.write("Deixe a IA orquestrar todo o percurso de forma automatizada via LangGraph.")
        if st.button("Iniciar Workflow IA", type="primary", use_container_width=True):
            st.switch_page("pages/8_⚙️_Workflow.py")

st.sidebar.title("📚 Adaptive Leveling System")
st.sidebar.info("Plataforma Adaptativa de Ensino")

if st.session_state.last_pdf_id:
    st.sidebar.divider()
    st.sidebar.write("📄 **Documento Ativo:**")
    st.sidebar.code(str(st.session_state.last_pdf_id)[:13] + "...", language=None)
    if st.sidebar.button("🗑️ Limpar Sessão"):
        st.session_state.clear()
        st.rerun()
