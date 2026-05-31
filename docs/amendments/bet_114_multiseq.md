# BET-114 — Multiple Sequences Without Interference

Pre-registered: 2026-05-31 (BEFORE the run). Follows BET-113 (single sequence).
Can the energy substrate hold SEVERAL distinct temporal sequences at once and
recall each from its own start without cross-talk? Tests temporal-memory capacity.

## Method

N=120 (capacity ≈ 16, headroom for 12 patterns). Store S=3 sequences of length
L=4 (12 distinct random patterns). Train each with `train_sequence` (accumulates
the attractor weights W and the transition matrix T). Recall each sequence from
its start; measure per-step overlap, and check it does not drift into another
sequence (no cross-talk).

## Acceptance bars (locked pre-run)

| ID | Criterion | Bar |
|----|-----------|-----|
| T114a | All sequences recalled | for every sequence, min per-step overlap ≥ 0.90 |
| T114b | No cross-talk | each recalled state's nearest stored pattern is from its OWN sequence (≥ 10/12 steps) |
| T114c | Control FAILS | shuffled-transition control fails T114a (min overlap < 0.70 beyond starts) |

PASS = T114a–c. PASS = the substrate stores multiple temporal memories
concurrently — a step toward a usable episodic/world-model store. NULL (cross-talk
at shared capacity) would itself map the temporal-capacity limit.

## RESULT (2026-05-31): NULL — 3 sequences hit the capacity edge

min per-step overlap 0.517 (one sequence interfered), own-sequence 9/12 (some
cross-talk), shuffled-transition control min 0.267 (fails, as required). One
sequence recalled perfectly (1.0), but 3 sequences = 12 patterns sits exactly at
the static capacity of N=120 (~0.1*N=12), so the clean-up attractors are marginal
and sequence recall (which relies on clean-up) breaks for the over-packed case.

T114a ✗ (0.517), T114b ✗ (9/12), T114c ✓ (control fails). Honest NULL: it is a
CAPACITY-edge effect, not a mechanism failure — fewer sequences or a larger N
should hold. BET-115 measures temporal capacity directly (sequences vs N).
