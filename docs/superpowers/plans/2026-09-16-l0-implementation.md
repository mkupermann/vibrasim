# L0 implementation plan

**Goal:** Implement G176's isolated continuous experience kernel and evaluator;
verify technical behavior and measure resources without running the research matrix.

**Architecture:** `vibrasim2/l0/core.py` owns only attempts, feedback, action search
and persistence. `evaluation.py` owns targets, held-out data, controls and verdicts.
The evaluator never passes targets or held-out rewards into the learner.
`benchmark.py` measures arbitrary non-target inputs; it makes no learning claim.

**Tech stack:** Python 3.13, existing NumPy, pytest. No new dependency.
**Spec:** `docs/amendments/G176_l0_continuous_experience_learning.md`.

## Constraints and execution

Work in the existing non-main research checkout, preserving all pre-existing
changes. No commit, push, camera, microphone, sound output or P0–P3 experiment.
Implementation planning budget 60 minutes, hard stop 120 minutes. Start
2026-09-16 at the first creation of this plan. Research execution remains separate:
first freeze code hashes, protocol, named random streams and measured time budget.

## 1. Kernel and persistence

- [x] Write and run failing tests in `tests/vibrasim2/test_l0_core.py` for
  immediate/delayed feedback, absence versus neutral, invalid/duplicate/expired IDs,
  FIFO and pending limits, continuous choices, frozen control, and exact restart.
- [x] Implement `Learner.attempt(x, now)`, `feedback(id, reward, now)`,
  `expire(now)`, `values(x, actions)`, `evaluate(contexts, seed)`, `save(path)` and
  `load(path)` in `vibrasim2/l0/core.py`. Validate every public numeric boundary.
  Persist a versioned JSON snapshot including constants, memory, ID and PCG64 state;
  atomically replace a saved file. On restore discard and log pending IDs.
- [x] Run the new core tests. Hand examples must yield Q=0.25, -0.25 and
  0.09196986029286058; rejected feedback must never append an experience.

## 2. Independent evaluator

- [x] Write failing tests in `tests/vibrasim2/test_l0_evaluation.py` covering
  feedback derangement, block ordering, disjoint splits, matched contexts,
  evaluation immutability, restart action identity and synthetic verdict fixtures.
- [x] Implement the five arms, separated named PCG64 streams, block feedback,
  phase A/B evaluation and strict 30-seed paired statistics in `evaluation.py`.
  Report learning, baseline advantage, adaptation and retention independently.
  Invalid data must be FAIL; externally incomplete runs INCONCLUSIVE.
- [x] Run short technical fixtures only, without measuring target learning success.

## 3. Resource measurement and handoff

- [x] Implement `python -m vibrasim2.l0.benchmark --output <new-file.json>`.
  Fill memory using arbitrary generated attempts and unrelated feedback, measure
  full-memory action throughput, process peak memory and persisted size.
- [x] Run it once, derive a conservative proposed research time limit and record
  its assumptions; do not launch the research run.
- [x] Run targeted L0 and existing P3 technical tests, the repository safety
  auditor, compilation and `git diff --check`. Review code against all G176 sections.
- [x] Update G176 status, FRONTIER, AGENTS and append LOGBOOK with actual evidence,
  commands, limitations and next step. Preserve the historical design entry.
