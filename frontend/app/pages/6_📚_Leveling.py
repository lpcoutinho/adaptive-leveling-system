"""Página de geração e exibição do plano de nivelamento personalizado."""

import httpx
import streamlit as st

from frontend.app.config import get_frontend_settings

settings = get_frontend_settings()
API = f"{settings.api_url}/api/v1"

st.set_page_config(page_title="Plano de Nivelamento", page_icon="📚", layout="wide")

st.title("📚 Plano de Nivelamento")
st.info(
    "💡 Este plano contém explicações e exercícios sob medida para "
    "fechar seus gaps de conhecimento."
)

# 1. Validação de Estado
if "current_readiness_id" not in st.session_state:
    st.warning("⚠️ Diagnóstico de prontidão não encontrado. Por favor, realize a análise primeiro.")
    if st.button("Ir para Prontidão"):
        st.switch_page("pages/5_🧠_Readiness.py")
    st.stop()

readiness_id = st.session_state["current_readiness_id"]
session_id = st.session_state.get("quiz_session_id")


def fetch_leveling_plan():
    """Chama a API para gerar ou recuperar o plano de nivelamento."""
    try:
        # Tenta gerar/recuperar o plano
        resp = httpx.post(
            f"{API}/leveling/generate",
            json={"session_id": str(session_id), "readiness_id": str(readiness_id)},
            timeout=120,  # Pode demorar pois chama o LLM para cada gap
        )

        if resp.status_code in [200, 201]:
            return resp.json()

        st.error(f"Erro ao gerar plano: {resp.text}")
        return None
    except Exception as e:
        st.error(f"Erro ao conectar com o servidor: {e}")
        return None


# 2. Gatilho de Geração
if "leveling_plan" not in st.session_state or st.session_state["leveling_plan"] is None:
    with st.spinner("🧠 A IA está preparando seu material de estudo personalizado..."):
        plan = fetch_leveling_plan()
        if plan:
            st.session_state["leveling_plan"] = plan
        else:
            st.stop()

# 3. Exibição do Plano
plan = st.session_state["leveling_plan"]
if plan:
    explanations = plan["explanations"]
    total_gaps = plan["total_gaps"]

    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("Seu Progresso")
        completed = st.session_state.get("leveling_completed_count", 0)
        progress = completed / total_gaps if total_gaps > 0 else 1.0

        st.progress(progress)
        st.metric("Tópicos para Revisar", total_gaps)
        st.metric("Tópicos Concluídos", completed)

        if progress == 1.0:
            st.balloons()
            st.success("🎉 Parabéns! Você concluiu todo o nivelamento.")

    with col2:
        st.subheader("📖 Material de Estudo")

        for i, expl in enumerate(explanations):
            importance = expl["importance"]
            if importance == "Critical":
                badge = "🔴 Crítico"
            elif importance == "Important":
                badge = "🟡 Importante"
            else:
                badge = "🔵 Útil"

            with st.expander(f"{i + 1}. {expl['gap_name']} — {badge}", expanded=(i == 0)):
                st.markdown(f"**Score no Quiz:** {expl['current_score']:.0f}%")

                st.markdown("### ❓ Por que é importante?")
                st.write(expl["why_important"])

                st.markdown("### 📝 Explicação")
                st.write(expl["explanation"])

                st.markdown("### 📐 Exemplo na Disciplina")
                st.info(expl["discipline_example"])

                st.markdown("### ✏️ Exercício de Fixação")
                st.write(expl["exercise"])

                # Sistema de correção simples do exercício
                with st.container():
                    user_answer = st.text_area("Sua resolução:", key=f"ans_{i}")
                    if st.button("Verificar Resposta", key=f"btn_{i}"):
                        if user_answer:
                            st.markdown("**Gabarito Sugerido:**")
                            st.success(expl["exercise_answer"])
                        else:
                            st.warning("Escreva sua resposta primeiro.")

                if st.button(f"✅ Marcar '{expl['gap_name']}' como Concluído", key=f"done_{i}"):
                    # Simula progresso local (idealmente seria uma chamada de API)
                    current_completed = st.session_state.get("completed_topics", set())
                    if expl["gap_name"] not in current_completed:
                        current_completed.add(expl["gap_name"])
                        st.session_state["completed_topics"] = current_completed
                        st.session_state["leveling_completed_count"] = len(current_completed)
                        st.rerun()

    st.divider()

    # 4. Ações Finais
    c1, c2 = st.columns(2)
    with c1:
        if st.button("📥 Exportar Plano (PDF)", use_container_width=True):
            st.warning("Funcionalidade de exportação em desenvolvimento.")
    with c2:
        if st.button("🔄 Refazer Avaliação Completa", use_container_width=True):
            keys = [
                "quiz_session_id",
                "quiz_current_idx",
                "quiz_answers",
                "quiz_results",
                "readiness_result",
                "leveling_plan",
                "completed_topics",
                "leveling_completed_count",
            ]
            for k in keys:
                st.session_state.pop(k, None)
            st.switch_page("pages/4_🏁_Quiz.py")
