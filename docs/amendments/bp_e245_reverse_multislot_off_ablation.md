# BP-E245 — Cascade reverse multislot OFF ablation

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** E214 cascade reverse (multislot ON); PRIM4 multislot  
**Discipline:** multi-trial reverse **ablation** — `ilw_multislot_enabled=False` vs ON. Not mid-kill; not pair_replace (E244); not hop-depth re-probe.

## Hypothesis

Same dual L–M–R scaffold as E214.

1. **Multislot ON** (control): fire R0 → rev p0 and fire R1 → rev p1 both ≥0.90 (same-trial both) ≥0.80  
2. **Multislot OFF**: fire R0 → rev p0 ≥0.80  
3. **Multislot OFF**: fire R1 → rev p1 ≥0.80  

## Bars

| id | criterion | threshold |
|----|-----------|-----------|
| B1 | multislot ON both reverse in trial | ≥0.80 |
| B2 | multislot OFF rev p0 | ≥0.80 |
| B3 | multislot OFF rev p1 | ≥0.80 |

Seeds {7361,7371} trials 6. Budget ~22 min, hard cap 44 min.

## What is NOT claimed

Not free dual. Not pair_replace. Not mid-kill. If OFF fails reverse → NULL names multislot load-bearing for dual reverse content.

## Prediction

🔮 LEAN PASS if dual reverse content segregation works without multislot (Y-separation alone) OR LEAN NULL if multislot required for dual reverse co-residence.

## RESULT

**PASS** (2026-07-26). B1=1.0 B2=1.0 B3=1.0.  
Multislot ON dual reverse OK; multislot OFF both reverse paths still work. Dual reverse co-residence does not require multislot under Y-separated cascade scaffold.

