# HYB-03 — Robust hybrid: discover the SQ-hard part from the MISCLASSIFIED residual

## Motivation
HYB-02 proved the energy+algebraic hybrid can decompose a mixed rule (seed 0: perfect, exact set) but
the low-confidence residual selection was seed-unstable (seed 7: garbage). HYB-03 uses a cleaner,
general residual: the samples the local learner gets WRONG. On a rule whose easy part the local learner
solves, every misclassified sample lies in the SQ-hard region — a pure, unbiased subset for the
algebraic (GF(2)) discovery step. This is standard residual/boosting logic; it should make the
decomposition robust across seeds.

## Method (`tools/run_hyb03_misclassified_residual.py`)
Identical to HYB-02 (mixed gated rule `y = +1 if x0=+1 else parity(x1..x8)`, raw energy / pure-GF(2) /
hybrid) EXCEPT the hybrid's residual is the MISCLASSIFIED training set (sign(feel) ≠ y) instead of the
low-confidence half. GF(2) on that residual → parity set s → augment with φ = ∏_{i∈s} x_i → retrain the
energy learner on [x, φ]. Seeds 0 & 7.

## Pre-registered PREDICTION + bars (BEFORE the run)
- **HYB03a (raw local partial):** raw energy ∈ [0.65, 0.85], both seeds.
- **HYB03b (pure GF(2) fails):** GF(2)-linear-whole ≤ 0.80, both seeds.
- **HYB03c (robust decomposition):** hybrid ≥ 0.93 on BOTH seeds (the fix robustly isolates the SQ-hard
  part).

PASS → the energy+algebraic hybrid ROBUSTLY decomposes a mixed rule where neither pure method works:
local energy learning handles the gradient-accessible part, and an algebraic module recovers the
SQ-hard part from the local learner's own errors. This is the actionable, working architecture for the
boundary JEP-461 identified. NULL if HYB03c still fails (residual isolation is harder than the
misclassified set provides). Bars locked; no retuning. Established methods (reservoir/RLS + GF(2) +
residual boosting), named — the contribution is the working decomposition, not new science.

## RESULT (2026-06-05): **PASS** — robust decomposition of a mixed rule

| seed | raw energy | GF(2)-whole | HYBRID | residual set |
|------|------------|-------------|--------|--------------|
| 0 | 0.745 | 0.496 | **0.981** | {1..8} ✓ |
| 7 | 0.759 | 0.497 | **0.976** | {1..8} ✓ |

HYB03a ✓, HYB03b ✓, HYB03c ✓ (both seeds ≥ 0.93) → **PASS.**

## Verdict: a robust, working architecture that decomposes mixed rules
Switching the residual from low-confidence (HYB-02, seed-unstable) to the MISCLASSIFIED set makes the
hybrid robust: both seeds recover the exact SQ-hard parity set {1..8} from the local learner's OWN
errors and reach ~0.98, where raw energy is ~0.75 (gets the gate, misses the parity) and pure GF(2) is
at chance (the mixture is not GF(2)-linear). So the energy+algebraic hybrid genuinely DECOMPOSES a rule
that neither pure method can: local energy learning handles the gradient-accessible part; an algebraic
module mines its residual for the SQ-hard structure.

**The constructive close of the 438→461 frontier arc, complete and robust:**
1. Local energy-driven learning has a fundamental SQ barrier on high-order, no-low-order-signal
   structure (rigorously located: not compute, not width — JEP-459/460/461).
2. The escape is an ALGEBRAIC structure-discovery module (HYB-01), and
3. it composes ROBUSTLY with the energy model on MIXED rules via the misclassified residual (HYB-03) —
   the actionable architecture: keep the energy learning, bolt on an algebraic module that mines the
   energy learner's errors for what it cannot reach.

Established methods (reservoir/ELM + RLS; GF(2) parity learning; residual boosting), named — the
contribution is the working, robust decomposition architecture and the precise boundary it addresses,
NOT new science. No transformer.
