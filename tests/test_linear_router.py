import os, sys
import pytest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))
pytest.importorskip("sentence_transformers")


def test_linear_router_routes_ambiguous():
    from linear_router import LinearRouter
    r = LinearRouter().fit({
        "contact": ["who is the plumber", "the dentist", "that lawyer guy", "the accountant"],
        "task": ["when is the tax due", "the sink fix job", "what's due in 2025", "review the lease"],
        "note": ["the budget note", "what I wrote about the trip", "that money cap thing", "my car note"]})
    assert r.route("when's the tax thing") == "task"   # keyword routing mis-routes this to note (GEO-85)
    assert r.route("the teeth doctor") == "contact"
