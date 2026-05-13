"""Meta-tests for research-mode autopilot.

Each test checks that the next-stage flux plan file exists with the
required pre-registered structure. These tests FAIL until the autopilot's
plan-writing session creates the corresponding plan.

Used by QUEUE.yaml items R-2 (F2 plan) and R-4 (F3 plan) as the objective
verdict criterion. The autopilot's plan-writing session passes by producing
a plan file at docs/superpowers/plans/*-flux-substrate-F{2,3}.md with the
required structural headings.

If the plan files exist already (post-vacation), these tests pass; if not,
they fail loudly so that postflight returns NULL/FAIL rather than silently
passing.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

# Meta-tests are deliberately excluded from the preflight fast-slice
# (`pytest -m "not slow"`). They are run on demand by postflight as the
# verdict criterion for R-2 (F2 plan) and R-4 (F3 plan).
pytestmark = pytest.mark.slow

REPO = Path(__file__).resolve().parent.parent
PLANS_DIR = REPO / "docs" / "superpowers" / "plans"

REQUIRED_SECTIONS = (
    "Acceptance contract",
    "File structure (locked decisions)",
    "Open calibration choices",
)


def _find_plan(suffix: str) -> Path | None:
    """Find a plan file matching pattern *-flux-substrate-{suffix}.md.

    Picks the lexicographically latest match (most recent date prefix).
    """
    matches = sorted(PLANS_DIR.glob(f"*-flux-substrate-{suffix}.md"))
    return matches[-1] if matches else None


def _assert_structure(plan: Path) -> None:
    body = plan.read_text()
    for sec in REQUIRED_SECTIONS:
        assert sec in body, (
            f"plan {plan.name} missing required section heading: '{sec}'"
        )
    assert re.search(r"^## Task \d", body, re.MULTILINE), (
        f"plan {plan.name} has no '## Task N' implementation section"
    )
    assert re.search(r"tests/flux/test_\w+\.py", body), (
        f"plan {plan.name} declares no tests/flux/test_*.py acceptance target"
    )


def test_F2_plan_exists_and_well_formed() -> None:
    plan = _find_plan("F2")
    if plan is None:
        pytest.fail(
            "No flux-substrate-F2.md plan found under docs/superpowers/plans/. "
            "R-2 acceptance: write the F2 plan per spec §5 (cochlea, audio I/O) "
            "and §7 T5+ tests."
        )
    _assert_structure(plan)
    body = plan.read_text()
    assert re.search(
        r"(?:§|section\s+|Section\s+)5", body
    ), f"F2 plan {plan.name} must reference spec section 5 (cochlea + audio I/O)"


def test_F3_plan_exists_and_well_formed() -> None:
    plan = _find_plan("F3")
    if plan is None:
        pytest.fail(
            "No flux-substrate-F3.md plan found under docs/superpowers/plans/. "
            "R-4 acceptance: write the F3 plan with a learning rule derived "
            "from the flux principle (NOT a Hebbian/STDP/BTSP reimplementation)."
        )
    _assert_structure(plan)
    body = plan.read_text().lower()
    assert "flux" in body, (
        f"F3 plan {plan.name} must reference the flux principle (the substrate's "
        "single foundational rule). A learning plan that doesn't mention flux is "
        "almost certainly importing STDP/BTSP/Hebbian by another name."
    )
    assert re.search(
        r"negative\s+control|matched.?wallclock", body
    ), (
        f"F3 plan {plan.name} must pre-register a negative control (matched-wallclock "
        "substrate without input must NOT develop the same structure)."
    )
