# EQMOD — Project Context

## What This Is

Bottom-up substrate simulator. Computational neuroscience / consciousness research. The goal is developing a deadlock-breaking process, not necessarily succeeding at the simulation.

## Active programme (2026-09-04) — Vibrasim II

**One active question:** `V2-P0 reciprocal field–matter channel`.

Read first, in order:

1. `docs/vibrasim2/CHARTER.md` — active programme charter
2. `docs/amendments/v2_p0_reciprocal_channel.md` — frozen P0 contract
3. `docs/amendments/v2_p0_scope_addendum.md` — frozen pre-data scope
4. `FRONTIER.md` — live one-screen board
5. newest entry in `LOGBOOK.md` — append-only research record

Vibrasim I and the Belief Path remain preserved as history. Do not reopen them
without an explicit programme decision. P0 is headless by default; its 3D view
is an observer, never evidence or a control surface.

## Hard Constraints

- **NO LLM, NO transformer, NO pretrained embedding model, NO BPE tokenizer** in any solution.
- Stay strictly within the substrate's own primitives: STDP, BTSP eligibility traces, dream consolidation (G15/G18), k_pattern_id segregation (G10), SubstrateLibrary (mixture-of-experts memory), and engineered port topology (CONCEPT §4.8).
- Ports are axonal-projection analogues, not emergent CTC. Ports are engineered; internals must emerge.
- When asked for new capability (e.g., text output), propose amendments that reuse these primitives. Never bolt on neural-net layers.
- On the belief path: every step must still reduce toward vibrations/binding/matter/collections — no replacing a rung with an established ML stack and calling it emergence.

## Pre-Registration Discipline

- Amendments are G-numbered.
- Acceptance criteria pre-registered in docs/marker_protocol.md or docs/amendments/<name>.md BEFORE any run.
- Post-hoc threshold tuning is forbidden by protocol.
- Negative controls (matched-wallclock, no-engram) must FAIL for the trained result to be defensible.
- Time budget = hybrid: realistic estimate + hard 2x ceiling; overrun = written FAILED post-mortem in LOGBOOK.md, no quiet extension.
- PASS/FAIL/NULL are all valid verdicts — NULL is a finding, not a failure to retry.
- Reusable mechanisms surfaced as docs/patterns/ markdown, never hidden in code.

## Environment

- macOS-arm64, Python 3.13, .venv at repo root
- pyvista 0.48 installed (no pyvistaqt/PyQt)
- Numba JIT cache live for physics hot paths
- Default WorldConfig (1000 vibrations, 60³ box, n_nodes_max=1024) saturates node capacity quickly — for tests/smokes use renders/calibration_session3.toml instead
- Test suite: `pytest -m "not slow"` for the fast slice
- Interactive PyVista GUI: `python -m world gui` (world/interactive.py, single-thread design, play/pause/step/picker/sliders)

## Known Bugs

- F3b silent-pass (RESOLVED, guarded — 2026-06-12): the historic bug was `if n_strong_before == 0: persistence_fractions.append(1.0)` (test could never fail when no strong structures formed). The live test `tests/test_substrate_growth_e2e.py::test_F3b_strong_structures_persist` is now a `@pytest.mark.skip` stub raising `NotImplementedError`, and its docstring specifies the correct fix (`pytest.fail()` on the precondition, not a trivial pass). The pattern is statically guarded suite-wide by the AUTO-1 auditor `tests/test_audit_silent_pass.py` (3 tests, green). Live risk only returns if Plan A Task 10 implements F3b with the bad pattern — which the auditor would flag.
