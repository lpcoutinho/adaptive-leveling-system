"""Página para exibição de pré-requisitos extraídos via LLM."""

import asyncio

import httpx
import streamlit as st

from frontend.app.config import get_frontend_settings

settings = get_frontend_settings()


async def check_llm_status():
    """Verifica se o LLM está configurado no backend."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{settings.api_url}/health/detailed", timeout=5.0)
            if response.status_code == 200:
                data = response.json()
                return data.get("llm_provider"), data.get("llm_configured", False)
            return None, False
    except Exception:
        return None, False


def fetch_prerequisites(pdf_id: str):
    """Busca os pré-requisitos na API."""
    try:
        response = httpx.get(f"{settings.api_url}/api/v1/prerequisites/{pdf_id}", timeout=10.0)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception:
        return None


def trigger_extraction(pdf_id: str):
    """Aciona a extração de inteligência via LLM."""
    try:
        response = httpx.post(
            f"{settings.api_url}/api/v1/prerequisites/extract/{pdf_id}", timeout=60.0
        )
        if response.status_code == 201:
            return response.json()
        return None
    except Exception as e:
        st.error(f"Erro ao conectar com a API de inteligência: {e}")
        return None


st.title("🧠 Inteligência da Aula")
st.write("Análise de conceitos principais e conhecimentos prévios necessários.")

pdf_id = st.session_state.get("last_pdf_id")

if not pdf_id:
    st.warning("⚠️ Nenhum PDF selecionado. Por favor, faça o upload de uma aula primeiro.")
    if st.button("Ir para Upload"):
        st.switch_page("pages/1_📄_Upload.py")
else:
    st.info(f"Analisando Documento ID: {pdf_id}")

    graph = fetch_prerequisites(pdf_id)
    has_prerequisites = bool(graph and (graph.get("main_concepts") or graph.get("prerequisites")))

    if has_prerequisites:
        st.divider()

        st.subheader("📚 Conceitos Abordados na Aula")
        for concept in graph["main_concepts"]:
            with st.expander(f"📌 {concept['name']}"):
                st.write(concept["description"])
                if concept["prerequisites"]:
                    st.caption(f"Requer: {', '.join(concept['prerequisites'])}")

        st.divider()

        st.subheader("🛠️ O que você precisa saber antes")
        cols = st.columns(3)
        importance_levels = [
            ("Critical", "🔴 Críticos", cols[0]),
            ("Important", "🟡 Importantes", cols[1]),
            ("Helpful", "🔵 Úteis", cols[2]),
        ]

        for level, label, col in importance_levels:
            with col:
                st.markdown(f"#### {label}")
                items = [p for p in graph["prerequisites"] if p["importance"] == level]
                if not items:
                    st.write("Nenhum identificado.")
                for item in items:
                    with st.container(border=True):
                        st.write(f"**{item['name']}**")
                        st.write(item["description"])
                        if item["topics"]:
                            st.caption(f"Tópicos: {', '.join(item['topics'])}")

        st.divider()
        if st.button("🎯 Próxima Etapa: Gerar Avaliação", type="primary"):
            st.switch_page("pages/3_📋_Assessment.py")

    else:
        st.write("Esta aula ainda não foi analisada pela IA.")

        provider, llm_ready = asyncio.run(check_llm_status())

        if llm_ready and provider and provider != "mock":
            if st.button("🚀 Iniciar Análise com IA"):
                msg = (
                    "O LLM está lendo a aula e mapeando conceitos... "
                    "Isso pode levar alguns segundos."
                )
                with st.spinner(msg):
                    graph = trigger_extraction(pdf_id)
                    if graph and (graph.get("main_concepts") or graph.get("prerequisites")):
                        st.success("✅ Análise concluída com sucesso!")
                        st.rerun()
                    elif graph:
                        st.warning("⚠️ A análise não retornou dados. Tente novamente.")
        elif provider == "mock":
            st.error(
                "⚠️ Nenhuma chave de API configurada. Para utilizar a análise "
                "com inteligência artificial, configure uma chave de API válida no "
                "arquivo `.env` (GROQ_API_KEY), defina LLM_PROVIDER=groq e "
                "**reinicie o servidor**."
            )
        else:
            st.error(
                "⚠️ Provedor de IA não configurado. Verifique as credenciais "
                "no arquivo `.env` e reinicie o servidor."
            )
