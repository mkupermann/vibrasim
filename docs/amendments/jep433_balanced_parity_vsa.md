# JEP-433 — Balanced non-linear (parity) affect over real VSA clouds: the decisive test

## Motivation
JEP-431 (memorization) and JEP-432 (sparse-XOR collapse + imbalance) both failed to isolate the
valence-reservoir's non-linear advantage over real VSA energy-clouds. JEP-433 removes both defects
with a clean construction: a BALANCED (50/50) parity rule over two independent binary feature-slots,
so base rate = 0.5 and the rule is true XOR with no degenerate case. A linear readout provably
cannot represent parity; if the reservoir energy model carries it on real clouds, that is the
genuine transfer claim. Established methods (VSA/HRR, reservoir/ELM, RLS), named. No transformer.

## Method (`tools/run_jep433_balanced_vsa.py`)
- **Two binary slots.** Slot A = one of {A0,A1} (50/50); slot B = one of {B0,B1} (50/50). Each
  concept cloud = normalized sum of [chosen-A vec, chosen-B vec, K_fill=4 filler features sampled
  uniquely from a 200-feature filler vocab]. The filler makes every cloud distinct and noisy;
  train/test filler-sets are DISJOINT.
- **Balanced parity affect.** valence = +1 (bright) iff `whichA == whichB`, else −1 (dark). Exactly
  50/50, genuinely non-linear (XOR of two binary variables), no rare/degenerate case.
- `ValenceReservoirLearner(n_inputs=D=4096, n_features=600)`; compare reservoir vs raw-linear
  least-squares vs shuffled-valence control. Seeds 0 and 7; 800 train / 400 test.

## Pre-registered PREDICTION + bars (BEFORE the run)
- **J433a (energy model learns balanced parity over real clouds):** reservoir held-out ≥ 0.85, both seeds.
- **J433b (linear readout provably cannot):** raw-linear ≤ 0.65 (≈ chance on parity), both seeds.
- **J433c (negative control fails):** shuffled-valence reservoir ≤ 0.60, both seeds.
- (sanity) base rate ≈ 0.50.

Predicted PASS: the reservoir cracks balanced parity on real VSA clouds (0.85+), raw-linear at
chance, control at chance. This would be the clean demonstration that the energy model learns
genuinely non-linear affect over the substrate's real distributed representation. NULL if J433a < 0.85
(filler noise or the cloud geometry defeats the reservoir too — no transfer) — honest. If raw-linear
somehow clears parity (J433b fails on a balanced rule), the "VSA linearizes low-order logic" finding
is established and the sub-thread closes. Bars locked; no retuning. No transformer.

## RESULT (2026-06-05): **PASS** (prediction HIT)

| seed | reservoir held-out | raw-linear | shuffled control | base rate |
|------|--------------------|------------|------------------|-----------|
| 0 | 0.912 | 0.522 | 0.505 | 0.520 |
| 7 | 0.880 | 0.482 | 0.495 | 0.520 |

J433a ✓ (reservoir ≥ 0.85), J433b ✓ (raw-linear ≈ chance), J433c ✓ (control ≈ chance), base rate
≈ 0.50 → **PASS, all bars, both seeds.**

## Verdict: the energy model learns genuinely non-linear affect over the substrate's REAL clouds
With the balanced parity construction (the fix for JEP-431's memorization and JEP-432's
sparse-collapse/imbalance), the result is unambiguous: the valence-reservoir energy model predicts
the affect of **UNSEEN** real VSA energy-clouds at **0.88–0.91**, while a linear readout sits exactly
at chance (0.48–0.52) — because parity is not linearly separable — and the shuffled-valence control
is also at chance. This is the clean demonstration that JEP-430's toy-XOR result **transfers to the
substrate's actual distributed representation**: the reservoir's random non-linear features recover
a balanced XOR-affect rule from the energy cloud alone, online, no enumeration, no labels beyond the
scalar valence.

**Honest scope.** All established (VSA/HRR — Plate, Kanerva; reservoir/ELM — Rahimi-Recht, Huang;
RLS), named — NOT new science. The contribution is the integration: Michael's affective-energy
signal, learned over the project's own VSA clouds, with a genuine non-linear advantage isolated.
The 431→432→433 arc also leaves a real secondary finding: **low-order** affect over VSA clouds is
largely *linearly* readable (feature presence is a linear projection; sparse low-order logic
collapses to linear separability) — the reservoir's non-linearity is needed only for genuinely
balanced higher-structure rules like parity, which it handles. No transformer.
