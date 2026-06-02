"""Aplicação principal do frontend usando Streamlit."""

import streamlit as st

from frontend.app.config import get_frontend_settings

settings = get_frontend_settings()


def main():
    """Ponto de entrada do frontend."""
    st.set_page_config(page_title=settings.app_title, page_icon="🎓", layout="wide")

    st.sidebar.title("Navegação")
    st.sidebar.info("🎓 Adaptive Leveling System")

    st.title("🎓 Adaptive Leveling System")
    st.subheader("Plataforma de nivelamento educacional baseada em IA")

    st.write("""
    Esta plataforma utiliza Inteligência Artificial para:
    1. Analisar aulas em PDF.
    2. Identificar pré-requisitos necessários.
    3. Avaliar seu nível de prontidão.
    4. Gerar conteúdo de nivelamento personalizado.
    """)

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.info("### 🚀 Comece por aqui")
        st.write("Faça o upload de uma aula em PDF para iniciar o processo.")
        if st.button("Ir para Upload"):
            st.info("Página de upload em desenvolvimento (Fase 2)")

    with col2:
        st.success("### 📊 Seu Progresso")
        st.write("Veja seus gaps de conhecimento e planos de estudo.")
        if st.button("Ver Resultados"):
            st.info("Página de resultados em desenvolvimento (Fase 6)")


if __name__ == "__main__":
    main()
