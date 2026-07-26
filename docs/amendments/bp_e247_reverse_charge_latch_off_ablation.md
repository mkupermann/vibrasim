# BP-E247 — Cascade reverse charge_latch OFF ablation

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** E214 cascade reverse (latch ON); PRIM6 latch  
**Discipline:** multi-trial reverse **ablation** — `charge_latch_enabled=False` vs ON. Not multislot ablation re-probe (E245); not mid-kill.

## Hypothesis

Same dual L–M–R scaffold as E214.

1. **Latch ON** (control): fire R0 → rev p0 and fire R1 → rev p1 both in trial ≥0.80  
2. **Latch OFF**: fire R0 → rev p0 ≥0.80  
3. **Latch OFF**: fire R1 → rev p1 ≥0.80  

## Bars

| id | criterion | threshold |
|----|-----------|-----------|
| B1 | latch ON both reverse in trial | ≥0.80 |
| B2 | latch OFF rev p0 | ≥0.80 |
| B3 | latch OFF rev p1 | ≥0.80 |

Seeds {7401,7411} trials 6. Budget ~22 min, hard cap 44 min.

## What is NOT claimed

Not free dual. Not pair_replace. Not mid-kill. If OFF fails → latch load-bearing for reverse readout.

## Prediction

🔮 LEAN NULL if reverse metrics rely on latch peak readout and charge decays without latch (B2/B3 fail). Or LEAN PASS if residual charge still peaks ≥1 during prop window.

## RESULT

*(filled after run)*
