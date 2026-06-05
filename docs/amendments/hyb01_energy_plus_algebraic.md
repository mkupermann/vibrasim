# HYB-01 — Constructive payoff: energy model + algebraic discovery escapes the SQ wall

## Motivation
JEP-461 proved the order-8 wall is the SQ-hardness of parity — a barrier of the LOCAL/correlational
algorithm class (which the energy model is), escapable by an ALGEBRAIC (GF(2)) method. The constructive
implication for Michael's energy model: keep the local energy learning, but BOLT ON an algebraic
structure-discovery module for the SQ-hard parts. HYB-01 demonstrates this directly with the actual
energy model (`world/valence_reservoir.ValenceReservoirLearner`): on order-8 parity it fails on raw
inputs (its random/correlational features hit the SQ wall), but augmented with ONE GF(2)-discovered
parity feature it succeeds. Established methods (reservoir/RLS + GF(2) parity learning), named — the
contribution is the demonstrated escape ARCHITECTURE, not new science.

## Method (`tools/run_hyb01_energy_plus_algebraic.py`)
Order-8 parity, P=18, seeds 0 & 7. Three learners, held-out accuracy:
- **raw energy:** `ValenceReservoirLearner` (M=400 random features + online RLS) on the raw 18-dim input.
- **+ algebraic feature:** GF(2) Gaussian elimination on a small sample discovers the parity set s;
  add the single feature φ = ∏_{i∈s} x_i to the input; the SAME energy learner trains on [x, φ].
- **GF(2) only:** the pure algebraic solve (reference — solves parity but is not a local learner).

## Pre-registered PREDICTION + bars (BEFORE the run)
- **HYB01a (raw energy hits the SQ wall):** raw energy held-out ≤ 0.65, both seeds.
- **HYB01b (the hybrid escapes it):** energy + algebraic feature held-out ≥ 0.95, both seeds.
- **HYB01c (the energy learner does the final work):** the hybrid uses the energy model's own readout
  over [x, φ] (not GF(2)'s prediction directly) and still ≥ 0.95 — the local learner, given the
  discovered structure, learns it.

Predicted PASS → the energy model, augmented with an algebraic structure-discovery module, escapes its
SQ barrier — a concrete, working architecture for the boundary JEP-461 identified. NULL if HYB01b fails
(the augmentation does not help — the barrier is deeper than feature access). Bars locked; no retuning.
No transformer; no new science (a demonstrated combination of established methods).

## RESULT (2026-06-05): **PASS** — the energy model escapes its SQ wall with an algebraic assist

| seed | raw energy | energy + algebraic feature | GF(2)-only (ref) |
|------|------------|----------------------------|------------------|
| 0 | 0.515 | 1.000 | 1.000 (set ✓) |
| 7 | 0.482 | 1.000 | 1.000 (set ✓) |

HYB01a ✓ (raw energy at chance — the SQ wall), HYB01b ✓ (hybrid 1.000) → **PASS, both seeds.**

## Verdict: a concrete architecture past the boundary
The actual `ValenceReservoirLearner` (the energy model) is at chance on order-8 parity from raw inputs
— its random/correlational features hit the SQ wall (JEP-459/460/461). Given ONE GF(2)-discovered
parity feature, the SAME energy learner's readout solves it at 1.000. So **local energy-driven
learning + a bolt-on algebraic structure-discovery module escapes the fundamental SQ barrier** of
local learning. This is the constructive payoff of the whole 438→461 frontier arc:
- the barrier is real and precisely located (SQ-hardness of high-order, no-low-order-signal structure),
- it cannot be moved by compute or width (only by an algebraic, non-local mechanism),
- and a working escape architecture is the energy model PLUS an algebraic discovery module — which
  composes cleanly (the energy learner does the final prediction over the discovered feature).

Honest scope: established methods (reservoir/ELM + RLS; GF(2) parity learning), named — the
contribution is the demonstrated escape architecture and the precise boundary it addresses, NOT new
science. For Michael's energy model this is the actionable design conclusion: keep the local energy
learning; add an algebraic structure-discovery module for the SQ-hard parts. No transformer.
