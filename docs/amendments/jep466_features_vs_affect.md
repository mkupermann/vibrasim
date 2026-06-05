# JEP-466 — Reservoir feature count IS the lever for the affect ceiling (the actionable knob)

## Motivation
JEP-463/464/465 located the energy model's affect ceiling (~order 2 over clouds) and ruled out the
learner (464) and dimension (465). The remaining lever is the reservoir's NUMBER OF FEATURES (its main
hyperparameter) — the JEP-429 random-features scaling applied to the real cloud.

## Method
Order-3 affect over VSA clouds (D=4096), `ValenceReservoirLearner`, sweep `n_features` ∈ {600, 1500,
3000, 6000}, seeds 0 & 7. (Pre-registered: J466a more features help (M6000 ≥ M600+0.10); J466b M6000
crosses 0.80.)

## RESULT (2026-06-05): **PASS** — the lever works

| seed | M=600 | M=1500 | M=3000 | M=6000 |
|------|-------|--------|--------|--------|
| 0 | 0.608 | 0.733 | 0.855 | 0.930 |
| 7 | 0.630 | 0.683 | 0.777 | 0.908 |

J466a ✓ · J466b ✓ → **PASS, both seeds.**

## Verdict: the affect ceiling is a feature-count lever (at the C(P,k) cost) — actionable for the model
The reservoir's feature count is THE knob: the deployed default (M=600) caps at order-2 (order-3 = 0.61),
but raising features lifts order-3 monotonically — M=3000 → 0.86, M=6000 → 0.91–0.93 (solved). This is
the JEP-429 random-features law on the real cloud: order-k is learnable with ~more features, achievable
for order-3 at M≈6000.

**Complete, actionable characterization of Michael's energy model affect ceiling (JEP-463→466):**
- Default (M=600): affect ceiling = **order 2** (adequate for real low-order affect — predators/sounds).
- **Lever:** raise reservoir features (NOT the learner — JEP-464 worse; NOT the dimension — JEP-465 flat).
  M≈6000 reaches **order 3** (0.91).
- **Cost / boundary:** features scale with interaction order (C(P,k)) — order-4/5 need exponentially more
  → impractical; for genuinely high-order affect the efficient escape is the algebraic hybrid module
  (HYB-01/03), not ever-more features.

So the deployed model has a clear, tunable affect-complexity dial (feature count) up to ~order 3, and a
characterized hybrid path beyond. Established methods (reservoir/ELM + RLS; the C(P,k) random-features
law), named; a measurement that gives actionable levers, not new science. No transformer.
