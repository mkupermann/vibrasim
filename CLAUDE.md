# EQMOD — Project Context

## What This Is

Bottom-up substrate simulator. Computational neuroscience / consciousness research. The goal is developing a deadlock-breaking process, not necessarily succeeding at the simulation.

## Active programme (2026-07-19)

**Belief path — restart the question, keep the lab.** Read first:

- `docs/BELIEF_PATH.md` — spine (vibrations → field → bind → electrons → atoms → molecules as information → matter → talented collections → brain), in/out of bounds, open rungs
- `FRONTIER.md` — one-screen current frontier

Do **not** default to archive tracks (VSA/reservoir language wins, Brian2 SNN stack, oscillator-Ising/SA/CIM, BET-144/145/146 temporal credit, GEO/LLM) unless Michael explicitly re-admits them. Those findings stay in LOGBOOK/summaries as boundaries.

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

- F3b-Test has silent-pass bug: `if n_strong_before == 0: persistence_fractions.append(1.0)` — test can never fail when no strong structures were formed.
