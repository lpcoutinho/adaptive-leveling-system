"""Página de status de saúde dos serviços."""

import asyncio

import httpx
import streamlit as st

from frontend.app.config import get_frontend_settings

settings = get_frontend_settings()


async def check_api_health():
    """Verifica saúde da API backend."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{settings.api_url}/health/detailed", timeout=5.0)
            if response.status_code == 200:
                return response.json()
            return None
    except Exception:
        return None


st.title("🔍 Status do Sistema")
st.write("Verificando conexão com serviços...")

health_data = asyncio.run(check_api_health())

if health_data:
    st.success("✅ Backend está UP")

    cols = st.columns(4)

    with cols[0]:
        st.metric("Banco de Dados", health_data.get("database", "Unknown"))
    with cols[1]:
        st.metric("Cache (Valkey)", health_data.get("cache", "Unknown"))
    with cols[2]:
        st.metric("Storage (S3)", health_data.get("storage", "Unknown"))
    with cols[3]:
        st.metric("LLM Provider", health_data.get("llm_provider", "Unknown"))

else:
    st.error("❌ Backend está DOWN ou inacessível")
    st.write(f"Tentando conectar em: {settings.api_url}")
