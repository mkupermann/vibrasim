# EQMOD — Project Context

## What This Is

Bottom-up substrate simulator. Computational neuroscience / consciousness research. The goal is developing a deadlock-breaking process, not necessarily succeeding at the simulation.

## Active programme (2026-09-06) — Vibrasim II

### Separate L0 design update (2026-09-16)

For experiential-learning work read `docs/amendments/G176_l0_continuous_experience_learning.md`.
It supersedes the rejected three-tone L0 draft with a continuous-action research
specification. The candidate kernel and evaluator are now implemented and
technically tested; see `docs/validation/l0-20260916.md`. The subsequently authorised
G176/G177 30-seed run is now closed NULL; see `docs/l0/AI_EXPERIMENT.md` and
`archive/run-logs/l0/2026-09-16-observed-001/result.json`. All seeds reproduced
exactly; independent scoring passed. Absolute learning, adaptation and retention
bars were not met. No novelty claim or automatic follow-on run is authorised.
Keep G176/G177 and their manifest-hashed source files unchanged. `summarize` checks numeric inputs,
not artifact provenance; do not treat synthetic test fixtures as research evidence.
The historical substrate constraints below still govern those programmes; G176
is a separately described candidate, not a claim of physical emergence. No P0–P3
rerun or automatic learning experiment is authorised by this documentation update.
The subsequent implementation instruction covered technical tests and a non-target
resource benchmark; it did not execute the 30-seed research matrix.

**P3 seeded open maintenance is authorised as an engineering experiment.**
Read `docs/amendments/v2_p3_open_maintenance.md` first. Michael authorised this
new programme decision on 2026-09-06. It is not evidence for emergence or the
organisational-memory rung. V2-P2 stays closed `INCONCLUSIVE`; no P2 rerun is
authorised. P3 has one frozen eleven-cell run, no post-data retuning.

Read first, in order:

1. `docs/vibrasim2/CHARTER.md` — active programme charter
2. `docs/amendments/v2_p2_dynamic_maintenance.md` — frozen P2 contract
3. `archive/run-logs/v2-p2/2026-09-05-observed-001/result.json` — fixed P2 verdict
4. `docs/vibrasim2/P2_CLOSEOUT.md` — P2 evidence and stop decision
5. `docs/superpowers/specs/2026-09-04-v2-p1-mechanism-audit-design.md` — historical P1 contract
6. `docs/amendments/v2_p0_reciprocal_channel.md` — historical frozen P0 contract
7. `FRONTIER.md` — live one-screen board
8. newest entry in `LOGBOOK.md` — append-only research record

Vibrasim I and the Belief Path remain preserved as history. Do not reopen them
without an explicit programme decision. The fixed P0 and P2 datasets are closed
for further design selection. Any 3D live view or replay is an observer, never
evidence or a control surface.

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
