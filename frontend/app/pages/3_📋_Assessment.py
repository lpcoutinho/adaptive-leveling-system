"""Página de avaliação diagnóstica — gera e exibe questões."""

import httpx
import streamlit as st

from frontend.app.config import get_frontend_settings

settings = get_frontend_settings()


def generate_assessment(pdf_id: str):
    """Solicita geração de avaliação. Retorna (dict|None, erro|None)."""
    try:
        r = httpx.post(f"{settings.api_url}/api/v1/assessment/generate/{pdf_id}", timeout=120)
        if r.status_code == 201:
            return r.json(), None
        detail = r.json().get("detail", f"HTTP {r.status_code}")
        return None, detail
    except httpx.ConnectError:
        return None, f"Servidor offline em {settings.api_url}"
    except httpx.TimeoutException:
        return None, "A geração excedeu o tempo limite. Tente novamente."
    except Exception as e:
        return None, str(e)


def fetch_assessment(pdf_id: str):
    """Busca avaliação já existente para um PDF."""
    try:
        r = httpx.get(f"{settings.api_url}/api/v1/assessment/pdf/{pdf_id}", timeout=10)
        return r.json() if r.status_code == 200 else None
    except Exception:
        return None


st.title("📋 Geração de Avaliação Diagnóstica")
st.markdown("Gere questões personalizadas para avaliar os pré-requisitos da sua aula.")

pdf_id = st.session_state.get("last_pdf_id")

if not pdf_id:
    st.warning("Nenhuma aula selecionada. Vá para a página de upload primeiro.")
    if st.button("Ir para Upload"):
        st.switch_page("pages/1_📄_Upload.py")
else:
    st.sidebar.header("📄 Aula Atual")
    st.sidebar.info(f"ID: {str(pdf_id)[:8]}...")

    # Tenta carregar avaliação existente
    assessment = st.session_state.get("current_assessment")
    if not assessment:
        assessment = fetch_assessment(pdf_id)
        if assessment:
            st.session_state["current_assessment"] = assessment

    if not assessment:
        if st.sidebar.button("🔄 Gerar Avaliação", type="primary", use_container_width=True):
            with st.spinner("Gerando questões com IA... Isso pode levar alguns segundos."):
                result, error = generate_assessment(pdf_id)
                if result:
                    st.session_state["current_assessment"] = result
                    st.session_state["current_pdf_id"] = pdf_id
                    st.success("✅ Avaliação gerada com sucesso!")
                    st.rerun()
                else:
                    st.error(f"❌ Erro: {error}")

        st.info(
            "Clique em **Gerar Avaliação** na barra lateral para criar questões personalizadas."
        )
    else:
        questions = assessment.get("questions", [])

        if not questions:
            st.warning("⚠️ Nenhuma questão gerada. Extraia pré-requisitos primeiro.")
            if st.button("Ir para Pré-requisitos"):
                st.switch_page("pages/2_🧠_Prerequisites.py")
        else:
            col1, col2, col3 = st.columns(3)
            with col1:
                mc = sum(1 for q in questions if q["type"] == "multiple_choice")
                st.metric("Múltipla Escolha", mc)
            with col2:
                sa = sum(1 for q in questions if q["type"] == "short_answer")
                st.metric("Resposta Curta", sa)
            with col3:
                calc = sum(1 for q in questions if q["type"] == "calculation")
                st.metric("Cálculo", calc)

            st.divider()
            if st.button("🏁 Iniciar Quiz", type="primary"):
                st.session_state["current_assessment"] = assessment
                st.switch_page("pages/5_🏁_Quiz.py")
