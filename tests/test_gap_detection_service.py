"""Testes para o serviço de detecção de gaps."""

import pytest

from backend.domain.models.prerequisite import KnowledgeGraph, Prerequisite
from backend.domain.models.readiness import GapAnalysis, ReadinessLevel
from backend.services.gap_detection_service import (
    _calculate_per_prerequisite_scores,
    _classify_readiness,
    _identify_gaps_and_strengths,
    _prioritize_gaps,
    _weighted_overall_score,
)


@pytest.fixture
def mock_knowledge_graph():
    return KnowledgeGraph(
        pdf_id="00000000-0000-0000-0000-000000000001",
        main_concepts=[],
        prerequisites=[
            Prerequisite(name="Derivadas", description="", importance="Critical", topics=[]),
            Prerequisite(name="Limites", description="", importance="Important", topics=[]),
            Prerequisite(name="Frações", description="", importance="Helpful", topics=[]),
        ],
    )


@pytest.fixture
def mock_mapping():
    return {
        "q1": "Derivadas",
        "q2": "Derivadas",
        "q3": "Limites",
        "q4": "Frações",
    }


@pytest.fixture
def mock_answers():
    from backend.domain.models.quiz import QuizAnswer

    return [
        QuizAnswer(
            question_id="q1", question_type="multiple_choice", student_answer="a", score=50.0
        ),
        QuizAnswer(
            question_id="q2", question_type="multiple_choice", student_answer="a", score=60.0
        ),
        QuizAnswer(
            question_id="q3", question_type="multiple_choice", student_answer="a", score=75.0
        ),
        QuizAnswer(
            question_id="q4", question_type="multiple_choice", student_answer="a", score=95.0
        ),
    ]


class TestWeightedScoring:
    def test_critical_weight_3x(self):
        data = {"Derivadas": {"score": 100.0, "importance": "Critical", "evaluated": True}}
        score = _weighted_overall_score(data)
        assert score == 100.0

    def test_important_weight_2x(self):
        data = {"Limites": {"score": 100.0, "importance": "Important", "evaluated": True}}
        score = _weighted_overall_score(data)
        assert score == 100.0

    def test_helpful_weight_1x(self):
        data = {"Frações": {"score": 100.0, "importance": "Helpful", "evaluated": True}}
        score = _weighted_overall_score(data)
        assert score == 100.0

    def test_mixed_weights(self):
        data = {
            "Derivadas": {"score": 100.0, "importance": "Critical", "evaluated": True},
            "Limites": {"score": 0.0, "importance": "Important", "evaluated": True},
            "Frações": {"score": 100.0, "importance": "Helpful", "evaluated": True},
        }
        score = _weighted_overall_score(data)
        expected = round((100 * 3 + 0 * 2 + 100 * 1) / (3 + 2 + 1), 2)
        assert score == expected

    def test_empty_data(self):
        assert _weighted_overall_score({}) == 0.0

    def test_all_zeros(self):
        data = {
            "Derivadas": {"score": 0.0, "importance": "Critical", "evaluated": True},
            "Limites": {"score": 0.0, "importance": "Important", "evaluated": True},
        }
        assert _weighted_overall_score(data) == 0.0


class TestClassifier:
    def test_ready_threshold(self):
        assert _classify_readiness(85.0) == ReadinessLevel.READY

    def test_ready_exact(self):
        assert _classify_readiness(80.0) == ReadinessLevel.READY

    def test_needs_review_mid(self):
        assert _classify_readiness(65.0) == ReadinessLevel.NEEDS_REVIEW

    def test_needs_review_low(self):
        assert _classify_readiness(50.0) == ReadinessLevel.NEEDS_REVIEW

    def test_not_ready(self):
        assert _classify_readiness(30.0) == ReadinessLevel.NOT_READY

    def test_not_ready_below_threshold(self):
        assert _classify_readiness(49.99) == ReadinessLevel.NOT_READY


class TestGapIdentification:
    def test_identify_gaps_below_60(self):
        data = {"Derivadas": {"score": 45.0, "importance": "Critical", "evaluated": True}}
        gaps, strengths = _identify_gaps_and_strengths(data)
        assert len(gaps) == 1
        assert gaps[0].is_gap is True
        assert gaps[0].is_strength is False

    def test_identify_strength_above_80(self):
        data = {"Derivadas": {"score": 90.0, "importance": "Critical", "evaluated": True}}
        gaps, strengths = _identify_gaps_and_strengths(data)
        assert len(strengths) == 1
        assert strengths[0].is_strength is True
        assert len(gaps) == 0

    def test_neutral_zone_both_false(self):
        data = {"Derivadas": {"score": 70.0, "importance": "Important", "evaluated": True}}
        gaps, strengths = _identify_gaps_and_strengths(data)
        assert len(gaps) == 0
        assert len(strengths) == 0

    def test_exact_gap_threshold(self):
        data = {"Derivadas": {"score": 59.99, "importance": "Critical", "evaluated": True}}
        gaps, _ = _identify_gaps_and_strengths(data)
        assert len(gaps) == 1

    def test_exact_strength_threshold(self):
        data = {"Derivadas": {"score": 80.0, "importance": "Important", "evaluated": True}}
        _, strengths = _identify_gaps_and_strengths(data)
        assert len(strengths) == 1

    def test_multiple_gaps_and_strengths(self):
        data = {
            "A": {"score": 30.0, "importance": "Critical", "evaluated": True},
            "B": {"score": 90.0, "importance": "Important", "evaluated": True},
            "C": {"score": 70.0, "importance": "Helpful", "evaluated": True},
        }
        gaps, strengths = _identify_gaps_and_strengths(data)
        assert len(gaps) == 1
        assert len(strengths) == 1

    def test_all_gaps(self):
        data = {
            "A": {"score": 10.0, "importance": "Critical", "evaluated": True},
            "B": {"score": 20.0, "importance": "Important", "evaluated": True},
        }
        gaps, strengths = _identify_gaps_and_strengths(data)
        assert len(gaps) == 2
        assert len(strengths) == 0


class TestGapPrioritization:
    def test_prioritize_by_importance_then_score(self):
        gaps = [
            GapAnalysis(prerequisite_name="A", score=50.0, importance="Important"),
            GapAnalysis(prerequisite_name="B", score=30.0, importance="Critical"),
            GapAnalysis(prerequisite_name="C", score=40.0, importance="Important"),
        ]
        prioritized = _prioritize_gaps(gaps)
        assert prioritized[0].prerequisite_name == "B"
        assert prioritized[1].prerequisite_name == "C"
        assert prioritized[2].prerequisite_name == "A"

    def test_critical_first_same_score(self):
        gaps = [
            GapAnalysis(prerequisite_name="A", score=40.0, importance="Important"),
            GapAnalysis(prerequisite_name="B", score=40.0, importance="Critical"),
        ]
        prioritized = _prioritize_gaps(gaps)
        assert prioritized[0].prerequisite_name == "B"
        assert prioritized[1].prerequisite_name == "A"

    def test_empty_gaps(self):
        assert _prioritize_gaps([]) == []


class TestPerPrerequisite:
    def test_calculate_average(self, mock_knowledge_graph, mock_answers, mock_mapping):
        scores = _calculate_per_prerequisite_scores(
            mock_answers, mock_knowledge_graph, mock_mapping
        )
        assert scores["Derivadas"]["score"] == 55.0
        assert scores["Limites"]["score"] == 75.0
        assert scores["Frações"]["score"] == 95.0

    def test_importance_preserved(self, mock_knowledge_graph, mock_answers, mock_mapping):
        scores = _calculate_per_prerequisite_scores(
            mock_answers, mock_knowledge_graph, mock_mapping
        )
        assert scores["Derivadas"]["importance"] == "Critical"
        assert scores["Limites"]["importance"] == "Important"
        assert scores["Frações"]["importance"] == "Helpful"
