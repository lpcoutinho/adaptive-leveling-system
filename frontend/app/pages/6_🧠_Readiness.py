import streamlit as st

st.set_page_config(page_title="Prontidão", page_icon="🧠", layout="wide")

st.title("🧠 Análise de Prontidão")

if "current_assessment" not in st.session_state:
    st.info("Nenhuma avaliação selecionada. Complete um quiz primeiro.")
    if st.button("Ir para Avaliação"):
        st.switch_page("pages/3_📋_Assessment.py")
    st.stop()

assessment = st.session_state["current_assessment"]
pdf_id = assessment.get("pdf_id", "")

if "readiness_result" not in st.session_state:
    st.session_state["readiness_result"] = None


def analyze_readiness():
    mock_gaps = [
        {"name": "Derivadas de Funções Trigonométricas", "score": 45.0, "importance": "Critical"},
        {"name": "Regra da Cadeia", "score": 50.0, "importance": "Critical"},
        {"name": "Limites Fundamentais", "score": 55.0, "importance": "Important"},
        {"name": "Derivadas de Ordem Superior", "score": 40.0, "importance": "Important"},
    ]
    mock_strengths = [
        {"name": "Operações Básicas com Frações", "score": 95.0, "importance": "Helpful"},
        {"name": "Funções Polinomiais", "score": 88.0, "importance": "Important"},
    ]
    scores = [g["score"] for g in mock_gaps] + [s["score"] for s in mock_strengths]
    overall = round(sum(scores) / len(scores), 2) if scores else 0.0
    if overall >= 80:
        level = "ready"
        level_label = "✅ Pronto"
    elif overall >= 50:
        level = "needs_review"
        level_label = "⚡ Precisa Revisar"
    else:
        level = "not_ready"
        level_label = "❌ Não Pronto"

    st.session_state["readiness_result"] = {
        "overall_score": overall,
        "level": level,
        "level_label": level_label,
        "gaps": mock_gaps,
        "strengths": mock_strengths,
        "total_gaps": len(mock_gaps),
        "total_strengths": len(mock_strengths),
    }


if st.button("🔍 Analisar Prontidão", type="primary"):
    with st.spinner("Analisando resultados do quiz..."):
        analyze_readiness()

result = st.session_state.get("readiness_result")
if result:
    score = result["overall_score"]
    level_label = result["level_label"]
    level = result["level"]

    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("Score Geral")
        score_pct = min(score, 100.0)
        if level == "ready":
            bar_color = "green"
        elif level == "needs_review":
            bar_color = "orange"
        else:
            bar_color = "red"

        html = f"""
            <div style="padding:20px;border:2px solid {bar_color};">
                <div style="color:{bar_color};">{score_pct:.0f}%</div>
                <div style="color:{bar_color};">{level_label}</div>
            </div>
        """
        st.markdown(html, unsafe_allow_html=True)

        st.progress(score_pct / 100.0)

        st.metric("Gaps", result["total_gaps"])
        st.metric("Forças", result["total_strengths"])

    with col2:
        if result["gaps"]:
            st.subheader("🔴 Gaps de Conhecimento")
            for g in result["gaps"]:
                import_icon = "🔥" if g["importance"] == "Critical" else "⭐"
                expander = st.expander(
                    f"{import_icon} {g['name']} — Score: {g['score']:.0f}% — {g['importance']}"
                )
                with expander:
                    st.markdown(f"Nível de domínio: **{g['score']:.0f}%**")
                    st.markdown(f"Importância: **{g['importance']}**")

        if result["strengths"]:
            st.subheader("✅ Forças (Strengths)")
            for s in result["strengths"]:
                st.markdown(f"- **{s['name']}** — Score: {s['score']:.0f}% — {s['importance']}")

    st.divider()
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("📚 Ver Plano de Nivelamento"):
            st.info("Fase 7 em breve!")
    with col_b:
        if st.button("🔄 Refazer Quiz"):
            for k in ["quiz_session_id", "quiz_current_idx", "quiz_answers", "quiz_results"]:
                st.session_state.pop(k, None)
            st.switch_page("pages/5_🏁_Quiz.py")
