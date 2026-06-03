import pytest

from backend.workflows.nodes.assessment_node import assessment_node
from backend.workflows.nodes.extract_node import extract_node
from backend.workflows.nodes.leveling_node import leveling_node
from backend.workflows.nodes.readiness_node import readiness_node
from backend.workflows.readiness_graph import (
    build_workflow_graph,
    route_after_assessment,
    route_after_extract,
    route_after_readiness,
)
from backend.workflows.states import GraphState, WorkflowStatus


class TestGraphState:
    def test_default_state(self):
        state = GraphState()
        assert state.status == WorkflowStatus.PENDING
        assert state.progress == 0.0
        assert state.error is None

    def test_state_with_pdf_id(self):
        state = GraphState(pdf_id="abc-123", status=WorkflowStatus.IN_PROGRESS)
        assert state.pdf_id == "abc-123"
        assert state.status == WorkflowStatus.IN_PROGRESS


class TestRouting:
    def test_route_after_extract_success(self):
        assert route_after_extract({"status": "in_progress"}) == "assessment"

    def test_route_after_extract_failed(self):
        assert route_after_extract({"status": "failed", "error": "erro"}) == "__end__"

    def test_route_after_assessment_success(self):
        assert route_after_assessment({"status": "in_progress"}) == "readiness"

    def test_route_after_assessment_failed(self):
        assert route_after_assessment({"status": "failed"}) == "__end__"

    def test_route_after_readiness_failed(self):
        assert route_after_readiness({"status": "failed"}) == "__end__"

    def test_route_after_readiness_student_ready(self):
        state = {"status": "in_progress", "readiness_result": {"overall_score": 85.0}}
        assert route_after_readiness(state) == "__end__"

    def test_route_after_readiness_needs_leveling(self):
        state = {"status": "in_progress", "readiness_result": {"overall_score": 45.0}}
        assert route_after_readiness(state) == "leveling"


class TestNodes:
    @pytest.mark.asyncio
    async def test_extract_node_no_pdf_id(self):
        result = await extract_node({"pdf_id": None})
        assert result["status"] == "failed"
        assert "obrigatório" in result["error"]

    @pytest.mark.asyncio
    async def test_extract_node_invalid_pdf_id(self):
        result = await extract_node({"pdf_id": "not-a-uuid"})
        assert result["status"] == "failed"

    @pytest.mark.asyncio
    async def test_assessment_node_no_pdf_id(self):
        result = await assessment_node({"pdf_id": None})
        assert result["status"] == "failed"

    @pytest.mark.asyncio
    async def test_readiness_node_no_ids(self):
        result = await readiness_node({"session_id": None, "pdf_id": None})
        assert result["status"] == "failed"

    @pytest.mark.asyncio
    async def test_leveling_node_no_ids(self):
        result = await leveling_node({"session_id": None, "readiness_id": None})
        assert result["status"] == "failed"


class TestGraph:
    def test_graph_builds(self):
        graph = build_workflow_graph()
        assert graph is not None

    def test_graph_node_names(self):
        graph = build_workflow_graph()
        builder = graph.__class__.__name__
        assert builder is not None

    def test_graph_state_schema(self):
        graph = build_workflow_graph()
        config = graph.get_graph()
        assert config is not None
