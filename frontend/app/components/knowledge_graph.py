"""Componente de visualização do grafo de conhecimento."""

import streamlit as st


def show_knowledge_graph(graph: dict):
    """Exibe uma visualização textual estruturada do grafo de conhecimento.

    Args:
        graph: Dicionário com main_concepts e prerequisites.
    """
    st.subheader("📚 Grafo de Conhecimento")

    if not graph or not graph.get("main_concepts"):
        st.info("Nenhum dado disponível para visualização.")
        return

    st.markdown("### Conceitos e suas Dependências")

    for concept in graph["main_concepts"]:
        name = concept.get("name", "Conceito")
        prereqs = concept.get("prerequisites", [])

        with st.container(border=True):
            cols = st.columns([1, 3])
            with cols[0]:
                st.markdown(f"**{name}**")
            with cols[1]:
                if prereqs:
                    prereq_list = ", ".join(prereqs)
                    st.caption(f"Depende de: {prereq_list}")
                else:
                    st.caption("Nenhum pré-requisito específico")
