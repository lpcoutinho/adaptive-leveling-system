import streamlit as st

st.set_page_config(page_title="Plano de Nivelamento", page_icon="📚", layout="wide")

st.title("📚 Plano de Nivelamento")

st.info("💡 Este plano é gerado com base nos gaps identificados na análise de prontidão.")

if "readiness_result" not in st.session_state:
    st.warning("Nenhuma análise de prontidão encontrada. Complete o quiz primeiro.")
    if st.button("Ir para Quiz"):
        st.switch_page("pages/5_🏁_Quiz.py")
    st.stop()

result = st.session_state["readiness_result"]
gaps = result.get("gaps", [])

if not gaps:
    st.success("✅ Nenhum gap de conhecimento identificado! Você está pronto para Cálculo I.")
    st.stop()

mock_explanations = [
    {
        "gap_name": g["name"],
        "importance": g["importance"],
        "current_score": g["score"],
        "why_important": (
            f"Dominar {g['name']} é essencial para entender "
            "conceitos avançados de Cálculo I, como derivadas e integrais."
        ),
        "explanation": (
            f"{g['name']} é um conceito fundamental que aparece "
            "frequentemente em problemas de Cálculo I."
        ),
        "calculus_example": (
            "Exemplo: Em Cálculo I, usamos este conceito para resolver limites e derivadas."
        ),
        "exercise": "Resolva um exercício prático envolvendo este conceito.",
        "exercise_answer": "Consulte seu material didático para verificar a resposta.",
    }
    for g in gaps
]

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Progresso")
    progress = st.session_state.get("leveling_progress", 0)
    st.progress(progress / len(gaps) if gaps else 0.0)
    st.metric("Gaps", len(gaps))
    st.metric("Concluídos", progress)

with col2:
    st.subheader("📖 Ordem de Estudo")

    for i, expl in enumerate(mock_explanations):
        if expl["importance"] == "Critical":
            badge = "🔴 Crítico"
        elif expl["importance"] == "Important":
            badge = "🟡 Importante"
        else:
            badge = "🟢 Complementar"

        with st.expander(f"{i + 1}. {expl['gap_name']} — {badge}", expanded=i == 0):
            score_col, _, _ = st.columns(3)
            with score_col:
                st.metric("Score Atual", f"{expl['current_score']:.0f}%")

            st.markdown("**❓ Por que é importante**")
            st.write(expl["why_important"])

            st.markdown("**📝 Explicação**")
            st.write(expl["explanation"])

            st.markdown("**📐 Exemplo em Cálculo I**")
            st.write(expl["calculus_example"])

            st.markdown("**✏️ Exercício**")
            answer = st.text_area(
                "Sua resposta:",
                key=f"exercise_{i}",
                height=80,
            )
            if answer and st.button("Verificar", key=f"check_{i}"):
                st.info(f"Gabarito: {expl['exercise_answer']}")
                st.success("✅ Marque como concluído!")

            if st.button(f"✅ Marcar Concluído #{i + 1}", key=f"done_{i}"):
                current = st.session_state.get("leveling_progress", 0)
                st.session_state["leveling_progress"] = min(current + 1, len(gaps))
                st.rerun()

st.divider()
col_a, col_b, col_c = st.columns(3)
with col_a:
    if st.button("🔄 Refazer Avaliação"):
        for k in ["quiz_session_id", "quiz_current_idx", "quiz_answers", "quiz_results"]:
            st.session_state.pop(k, None)
        st.switch_page("pages/5_🏁_Quiz.py")
with col_b:
    if st.button("📥 Exportar Plano"):
        st.info("Exportação disponível em breve.")
with col_c:
    if st.button("🧠 Ver Resultados"):
        st.switch_page("pages/6_🧠_Readiness.py")
