"""Aplicação principal do frontend usando Streamlit."""

import streamlit as st

from frontend.app.config import get_frontend_settings

# Importar as páginas
from frontend.app.pages.health import show_health
from frontend.app.pages.upload import show_upload

settings = get_frontend_settings()


def main():
    """Ponto de entrada do frontend."""
    st.set_page_config(page_title=settings.app_title, page_icon="🎓", layout="wide")

    # Navegação na Sidebar
    st.sidebar.title("📚 Menu")
    page = st.sidebar.radio(
        "Navegue entre as etapas:", ["Home", "Upload de Aula", "Status do Sistema"]
    )

    if page == "Home":
        show_home()
    elif page == "Upload de Aula":
        show_upload()
    elif page == "Status do Sistema":
        show_health()

    st.sidebar.divider()
    st.sidebar.info("🎓 Adaptive Leveling System v0.1.0")


def show_home():
    """Renderiza a página inicial."""
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
            st.rerun()  # Recarrega para refletir a navegação se necessário (ou use query params)

    with col2:
        st.success("### 📊 Seu Progresso")
        st.write("Veja seus gaps de conhecimento e planos de estudo.")
        if st.button("Ver Resultados"):
            st.warning("Página de resultados em desenvolvimento (Fase 6)")


if __name__ == "__main__":
    main()
