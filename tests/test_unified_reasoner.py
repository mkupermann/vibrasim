"""Regression tests for the UnifiedReasoner auto-dispatching agent (GEO-49)."""
import os, sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))
pytest.importorskip("sentence_transformers", reason="needs sentence-transformers")


@pytest.fixture(scope="module")
def agent():
    from unified_reasoner import UnifiedReasoner
    u = UnifiedReasoner(abstain_tau=0.30)
    for p, t in [("Alice", "Analytics"), ("David", "Analytics"), ("Bob", "Platform")]:
        u.add_person(p, t)
    u.add_team_city("Analytics", "Boston")
    u.add_team_city("Platform", "Denver")
    u.add_time_fact("Alice", 2020, "Analytics")
    u.add_time_fact("Alice", 2023, "Platform")
    return u


def test_routes_factoid(agent):
    assert agent.answer("Which team is Bob on?") == {"intent": "FACTOID", "answer": "Platform"}


def test_routes_count(agent):
    assert agent.answer("How many people work in Boston?")["answer"] == 2


def test_routes_temporal(agent):
    assert agent.answer("Which team was Alice on in 2021?")["answer"] == "Analytics"
    assert agent.answer("Which team was Alice on in 2024?")["answer"] == "Platform"


def test_routes_join(agent):
    res = agent.answer("Who is on the same team as Alice?")
    assert res["intent"] == "JOIN" and res["answer"] == {"David"}
