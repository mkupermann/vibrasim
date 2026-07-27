# BP-E71 — Soft-cut then restore OR bypass of AND-OR hybrid

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E66 soft-cut bypass PASS; E44/E52 restore doctrine  
**Discipline:** E66 cut, then **retrain L3–R only**; AND must stay; bypass returns

## Hypothesis
AND L1/L2–M–R + OR L3–R. Soft I at L3.
1. Soft-cut L3 → fire L3 → R OFF ≥0.90  
2. Fire L1+L2 → R ON ≥0.90 (AND intact)  
3. Restore L3–R → fire L3 → R ON ≥0.85  

## Bars
| ID | thr |
|----|-----|
| B1 bypass OFF after cut | ≥0.90 |
| B2 AND ON after cut | ≥0.90 |
| B3 bypass ON after restore | ≥0.85 |

Seeds {2081,2091} trials 8. Budget ~4 min, hard cap 8 min.

## Prediction
🔮 LEAN PASS. Miss if soft cut also zeros M–R and B2 fails.

## RESULT
**NULL** (2026-07-20). B1=1.0 B2=1.0 B3=0.0.  
Soft-cut silences bypass and AND stays; **L3–R-only retrain does not restore bypass**. Soft weaken at L3 may leave residual emitter/node damage or R-side state that single-hop rewrite does not fix.
