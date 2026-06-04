"""Regression tests for the EQMOD-3 geometric reasoning tools (GEO-1..39 deliverable).

Covers the validated behaviours of tools/geometric_reasoner.py: grounded retrieval, abstention,
multi-hop chaining, and symbolic aggregation. These are fast (one small embedding model, CPU) and run
under `pytest -m "not slow"`. Generation tests (grounded_qa with an LLM) are NOT included here — they
download a ~1GB model and are exercised by the GEO-34/35/39 scripts.
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))

pytest.importorskip("sentence_transformers", reason="needs sentence-transformers")


@pytest.fixture(scope="module")
def reasoner():
    from geometric_reasoner import GeometricReasoner
    r = GeometricReasoner(abstain_tau=0.40)
    chains = [("Alice", "Acme", "Boston"), ("Bob", "Globex", "Boston"), ("Carol", "Initech", "Austin")]
    for p, c, city in chains:
        r.add_fact(f"{p} works at {c}.", subject=p, relation="works_at", object=c)
        r.add_fact(f"{c} is in {city}.", subject=c, object=city)
    return r


def test_grounded_retrieval(reasoner):
    res = reasoner.ask("Where does Alice work?")
    assert res["grounded"] is True
    assert "Acme" in res["text"]


def test_abstains_on_ungrounded(reasoner):
    res = reasoner.ask("What is the capital of Mars?")
    assert res["grounded"] is False
    assert res["answer"] is None


def test_multihop_chain(reasoner):
    hits = reasoner.chain(["What company does Alice work at?", "What city is {bridge} in?"])
    assert hits is not None
    assert hits[-1]["object"] == "Boston"


def test_symbolic_aggregation(reasoner):
    # resolve each person -> city via chain, then count (geometry filters, symbol counts)
    people = [m["subject"] for m in reasoner.fact_meta if m.get("relation") == "works_at"]
    in_boston = 0
    for p in people:
        h = reasoner.chain([f"What company does {p} work at?", "What city is {bridge} in?"])
        if h and h[-1].get("object") == "Boston":
            in_boston += 1
    assert in_boston == 2


def test_abstention_calibration_runs(reasoner):
    tau = reasoner.calibrate_abstention(
        ["Where does Alice work?", "What city is Acme in?"],
        ["What is the weather?", "Who won the game?"],
    )
    assert 0.0 < tau < 1.0


def test_contradiction_detection(reasoner):
    # same subject (Alice), different object -> flagged; consistent -> not flagged (GEO-41)
    assert reasoner.check_contradiction("Alice works at Globex.", subject="Alice", object="Globex") is not None
    assert reasoner.check_contradiction("Alice works at Acme.", subject="Alice", object="Acme") is None


def test_entity_resolution_is_typo_robust(reasoner):
    # near-duplicate / typo'd name resolves to the stored subject (GEO-44)
    assert reasoner.resolve_entity("Alic", candidates=["Alice", "Bob", "Carol"]) == "Alice"
