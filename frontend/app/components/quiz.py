"""Componente de quiz para exibição de questões de avaliação."""

import streamlit as st


def render_question(question: dict, index: int):
    """Renderiza uma questão do quiz.

    Args:
        question: Dicionário com os dados da questão.
        index: Índice da questão (1-based).
    """
    type_labels = {
        "multiple_choice": "📝 Múltipla Escolha",
        "short_answer": "✍️ Resposta Curta",
        "calculation": "🧮 Cálculo",
    }
    difficulty_label = (
        "Fácil"
        if question["difficulty"] < 0.4
        else "Médio"
        if question["difficulty"] < 0.7
        else "Difícil"
    )

    st.markdown(f"### Questão {index}")
    st.caption(
        f"{type_labels.get(question['type'], question['type'])} — "
        f"Dificuldade: {difficulty_label} — "
        f"Tópico: {question['topic']}"
    )
    st.write(question["text"])

    # Input baseado no tipo
    if question["type"] == "multiple_choice":
        selected = st.radio(
            "Selecione a alternativa correta:",
            question.get("options", []),
            key=f"q_{question['id']}",
            index=None,
        )
        if selected:
            st.session_state[f"answer_{question['id']}"] = selected

    elif question["type"] == "short_answer":
        answer = st.text_area(
            "Sua resposta:",
            key=f"q_{question['id']}",
            height=80,
        )
        if answer:
            st.session_state[f"answer_{question['id']}"] = answer

    elif question["type"] == "calculation":
        answer = st.text_area(
            "Resolução:",
            key=f"q_{question['id']}",
            height=120,
        )
        if answer:
            st.session_state[f"answer_{question['id']}"] = answer

    st.divider()


def render_quiz(questions: list[dict]):
    """Renderiza o quiz completo com todas as questões.

    Args:
        questions: Lista de dicionários com dados das questões.
    """
    st.header("📋 Avaliação Diagnóstica")

    total = len(questions)
    answered = sum(1 for q in questions if st.session_state.get(f"answer_{q['id']}"))
    st.progress(answered / total, text=f"{answered}/{total} respondidas")

    for i, question in enumerate(questions, 1):
        render_question(question, i)
