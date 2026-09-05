import re
from hashlib import sha256
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ACTIVE_QUESTION = "No active scientific question"


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def canonical_lf_bytes(path: str) -> bytes:
    text = (ROOT / path).read_bytes().decode("utf-8")
    return text.replace("\r\n", "\n").encode("utf-8")


def test_vibrasim2_is_the_only_active_programme():
    assert "## Active programme (2026-09-05) — Vibrasim II" in read("AGENTS.md")
    assert "## Active programme (2026-09-05) — Vibrasim II" in read("CLAUDE.md")
    assert read("AGENTS.md") == read("CLAUDE.md")
    frontier = read("FRONTIER.md")
    assert "## Active programme: Vibrasim II — no open experiment" in frontier
    assert "no active scientific question" in frontier.lower()
    assert "closed `UNRESOLVED`" in frontier
    for path in ("AGENTS.md", "CLAUDE.md", "FRONTIER.md"):
        assert ACTIVE_QUESTION.lower() in read(path).lower(), path
    assert "V2-P1 mechanism audit — **UNRESOLVED**" in read("LOGBOOK.md")
    for path in ("AGENTS.md", "CLAUDE.md", "FRONTIER.md"):
        current = read(path)
        assert "Active programme: belief path" not in current
        assert "active programme (belief path)" not in current.lower()
        assert not re.search(
            r"active programme[^\n]{0,100}belief path", current, flags=re.IGNORECASE
        )


def test_vibrasim1_authorities_are_visibly_historical():
    assert "historical programme charter — frozen" in read("docs/BELIEF_PATH.md")
    assert "historical operating doctrine — frozen" in read("docs/DISCIPLINE_SHARP.md")
    assert "UNEXECUTED DRAFT — ARCHIVED" in read(
        "docs/amendments/bp_c6c_transverse_readability.md"
    )
    assert (ROOT / "docs/archive/vibrasim_i/FRONTIER_2026-08-13.md").is_file()


def test_frozen_p0_preregistration_is_unchanged():
    digest = sha256(canonical_lf_bytes("docs/amendments/v2_p0_reciprocal_channel.md")).hexdigest()
    assert digest == "28992a8b131100ed4eb2cd9147ddea7b3251921777211a63bb4b64e5524ca9e1"


def test_scope_addendum_changes_no_registered_bar():
    addendum = read("docs/amendments/v2_p0_scope_addendum.md")
    assert "FROZEN ADDENDUM — BEFORE IMPLEMENTATION OR DATA" in addendum
    assert "supplied coupling edges" in addendum
    assert "No model, fixture, constant, threshold, verdict predicate, or budget changes" in addendum
    assert "no scientific verdict" in addendum.lower()
    digest = sha256(canonical_lf_bytes("docs/amendments/v2_p0_scope_addendum.md")).hexdigest()
    assert digest == "f0c20858ffaf3750320bd05cc1b120222264e7bd3e84109406f7b4a3cb7d9cb0"


def test_p0_output_baseline_is_empty_before_implementation():
    assert read("docs/vibrasim2/P0_OUTPUT_BASELINE.json") == (
        '{"files":[],"root":"archive/run-logs/v2-p0","schema_version":1}\n'
    )
