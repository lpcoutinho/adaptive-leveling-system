"""Aplicação principal — Página inicial do Adaptive Leveling System."""

import streamlit as st

from frontend.app.config import get_frontend_settings

settings = get_frontend_settings()

st.set_page_config(page_title=settings.app_title, page_icon="🎓", layout="wide")

# Estado global compartilhado entre páginas via st.session_state
if "last_pdf_id" not in st.session_state:
    st.session_state.last_pdf_id = None

st.title("🎓 Adaptive Leveling System")
st.subheader("Plataforma de nivelamento educacional baseada em IA")

st.write("""
Esta plataforma utiliza Inteligência Artificial para:
1. **Analisar** aulas em PDF.
2. **Identificar** pré-requisitos necessários.
3. **Avaliar** seu nível de prontidão através de quizes.
4. **Gerar** conteúdo de nivelamento personalizado para fechar seus gaps.
""")

st.divider()

col1, col2 = st.columns(2)

with col1:
    st.info("### 🚀 Comece por aqui")
    st.write("Faça o upload de uma aula em PDF para iniciar o processo.")
    if st.button("Ir para Upload"):
        st.switch_page("pages/1_📄_Upload.py")

with col2:
    st.success("### 📊 Seu Progresso")
    st.write("Veja seus gaps de conhecimento e planos de estudo.")
    if st.button("Ver Resultados"):
        st.warning("Página de resultados em desenvolvimento (Fase 6)")

st.sidebar.title("📚 Adaptive Leveling System")
st.sidebar.info("🎓 v0.1.0")
