"""Página de análise de prontidão do aluno baseada no quiz."""

import httpx
import streamlit as st

from frontend.app.config import get_frontend_settings

settings = get_frontend_settings()
API = f"{settings.api_url}/api/v1"

st.set_page_config(page_title="Prontidão", page_icon="🧠", layout="wide")

st.title("🧠 Análise de Prontidão")
st.markdown("Veja seu nível de preparação e identifique o que precisa ser revisado.")

# 1. Validação de Estado
if "current_assessment" not in st.session_state:
    st.warning("⚠️ Nenhuma avaliação carregada. Por favor, complete um quiz primeiro.")
    if st.button("Ir para Quiz"):
        st.switch_page("pages/5_🏁_Quiz.py")
    st.stop()

assessment = st.session_state["current_assessment"]
pdf_id = assessment.get("pdf_id")
session_id = st.session_state.get("quiz_session_id")

if not session_id:
    st.error("❌ Sessão de quiz não encontrada. Tente realizar o quiz novamente.")
    if st.button("Ir para Quiz"):
        st.switch_page("pages/5_🏁_Quiz.py")
    st.stop()


def _get_level_label(level: str) -> tuple[str, str]:
    """Retorna o rótulo e a cor para cada nível de prontidão."""
    levels = {
        "ready": ("✅ Pronto", "green"),
        "needs_review": ("⚡ Precisa Revisar", "orange"),
        "not_ready": ("❌ Não Pronto", "red"),
    }
    return levels.get(level.lower(), (level, "gray"))


def fetch_readiness():
    """Chama a API para analisar os resultados do quiz e gerar o diagnóstico."""
    try:
        # Tenta recuperar análise existente primeiro
        resp = httpx.get(f"{API}/readiness/{session_id}", timeout=10)

        if resp.status_code == 200:
            return resp.json()

        # Se não existe, solicita a análise (POST)
        resp = httpx.post(
            f"{API}/readiness/analyze",
            json={"session_id": str(session_id), "pdf_id": str(pdf_id)},
            timeout=20,
        )

        if resp.status_code in [200, 201]:
            return resp.json()

        st.error(f"Erro na análise: {resp.text}")
        return None
    except Exception as e:
        st.error(f"Erro ao conectar com o servidor: {e}")
        return None


# 2. Gatilho de Análise
if "readiness_result" not in st.session_state or st.session_state["readiness_result"] is None:
    with st.spinner("🧠 Gerando diagnóstico detalhado..."):
        result = fetch_readiness()
        if result:
            st.session_state["readiness_result"] = result
        else:
            st.stop()

# 3. Exibição dos Resultados
result = st.session_state["readiness_result"]
if result:
    score = result.get("overall_score", 0.0)
    level_key = result.get("level", "not_ready")
    level_label, color = _get_level_label(level_key)

    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("Score de Prontidão")

        # Gauge customizado simples
        html = f"""
            <div style="padding:24px; border:3px solid {color}; border-radius:15px;
                        text-align:center;">
                <h1 style="color:{color}; font-size: 64px; margin:0;">{score:.0f}%</h1>
                <h3 style="color:{color}; margin:0;">{level_label}</h3>
            </div>
        """
        st.markdown(html, unsafe_allow_html=True)
        st.write("")
        st.progress(min(score / 100.0, 1.0))

        st.metric("Total de Gaps", result.get("total_gaps", 0))
        st.metric("Pontos Fortes", result.get("total_strengths", 0))

    with col2:
        # --- SEÇÃO DE GAPS ---
        gaps = result.get("gaps", [])
        if gaps:
            st.subheader("🔴 Onde você deve focar")
            for g in gaps:
                name = g.get("prerequisite_name") or g.get("name", "Desconhecido")
                importance = g.get("importance", "Helpful")
                item_score = g.get("score", 0.0)
                icon = "🔥" if importance == "Critical" else "⭐"

                with st.expander(f"{icon} {name} — Domínio: {item_score:.0f}%"):
                    st.write(f"**Importância:** {importance}")
                    st.write("Este tópico é fundamental para o entendimento da aula de Cálculo I.")

        # --- SEÇÃO DE STRENGTHS ---
        strengths = result.get("strengths", [])
        if strengths:
            st.subheader("✅ O que você já domina")
            for s in strengths:
                name = s.get("prerequisite_name") or s.get("name", "Desconhecido")
                item_score = s.get("score", 0.0)
                st.success(f"**{name}** — Domínio: {item_score:.0f}%")

    st.divider()

    # 4. Ações Finais
    c_a, c_b, c_c = st.columns(3)
    with c_a:
        if st.button("🔄 Refazer Quiz", use_container_width=True):
            keys = [
                "quiz_session_id",
                "quiz_current_idx",
                "quiz_answers",
                "quiz_results",
                "readiness_result",
            ]
            for k in keys:
                st.session_state.pop(k, None)
            st.switch_page("pages/5_🏁_Quiz.py")

    with c_b:
        if st.button("📊 Ver Outras Aulas", use_container_width=True):
            st.switch_page("0_🏠_Home.py")

    with c_c:
        if st.button("🚀 Iniciar Nivelamento", type="primary", use_container_width=True):
            st.session_state["current_readiness_id"] = result.get("id")
            st.switch_page("pages/7_📚_Leveling.py")
