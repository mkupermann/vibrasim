# BP-E72 — Soft-cut OR bypass, disarm emitters, then restore

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E71 NULL (L3–R-only restore fails)  
**Discipline:** not E71 bar retune — **disarm `k_weaken_bridge_emitter` after cut**, then restore L3–R

## Hypothesis
E71: soft-cut silences L3; L3–R rewrite fails. Residual weaken emitters at L3 may re-zero bridges during restore/probe.
1. Soft-cut L3 → L3 OFF ≥0.90  
2. Clear all weaken emitters; restore L3–R → L3 ON ≥0.85  
3. AND (L1+L2) still ON ≥0.90  

## Bars
| ID | thr |
|----|-----|
| B1 bypass OFF after cut | ≥0.90 |
| B2 bypass ON after disarm+restore | ≥0.85 |
| B3 AND still ON | ≥0.90 |

Seeds {2131,2141} trials 8. Budget ~4 min, hard cap 8 min.

## Prediction
🔮 LEAN PASS if residual emitter caused E71 fail. NULL if soft cut permanently damages nodes/R-side.

## RESULT
**PASS** (2026-07-20). B1=B2=B3=1.0. Disarm weaken emitters after soft-cut unlocks L3–R restore. Closes E71: residual emitters re-weakened rewritten bridges.
