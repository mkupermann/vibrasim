# BET-118 — Sparse Distributed Representations vs Sequence Interference

Pre-registered: 2026-05-31. BET-117 showed multi-sequence recall fails on the
MECHANISM (interference), not capacity. Principled non-transformer fix: SPARSE
patterns (few active units). Sparse codes overlap less, so transitions interfere
less and capacity rises (Kanerva SDM / sparse Hopfield, covariance learning rule).

## Mechanism
Patterns are sparse: P(+1)=a (low activity, e.g. 0.15), else -1. Learn with the
CENTERED (covariance) rule for both attractors W and transitions T:
dW ∝ (p-μ)(p-μ)ᵀ∘M, dT ∝ (p_{t+1}-μ)(p_t-μ)ᵀ∘M, μ=2a-1. Recall relaxes with a
sparsity-preserving activation. Test multiple sequences vs the dense baseline.

## Bars
| ID | Criterion | Bar |
|----|-----------|-----|
| T118a | Sparse beats dense | S=3 @ N=300 sparse min content overlap ≥ 0.90 (dense was 0.74) |
| T118b | Scales | S=5 @ N=300 sparse min content overlap ≥ 0.85 (dense was 0.46) |
| T118c | Control | shuffled-T sparse control fails (< 0.70) |

PASS => sparse coding breaks the interference wall: a real, transformer-free step
toward the context-dependent sequence capacity language needs. NULL => even sparse
geometric memory hits the wall — the honest limit of this paradigm.

## RESULT (2026-05-31): NULL — sparse helps marginally, wall holds

sparse S=3@N300=0.740 (= dense 0.74), S=5@N300=0.607 (> dense 0.46, but < 0.85);
shuffled-T control 0.373 (fails). Sparse coding helps the over-packed case a bit
but does NOT break the interference wall. T118a/b x, T118c ok.

This is the 5th NULL on the multi-sequence line (BET-114..118): more N,
context-tags, and sparse codes all fail to cleanly separate overlapping
context-dependent sequences. Per the charter (>=3 NULLs on a line -> stop the
line), the multi-sequence/context-prediction line is consolidated, not extended.
See docs/SEQUENCE_WALL.md.
