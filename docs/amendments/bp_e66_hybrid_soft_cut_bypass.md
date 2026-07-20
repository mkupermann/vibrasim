# BP-E66 — Soft-cut OR bypass of AND-OR hybrid

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E65 PASS hybrid; E64 soft endpoint  
**Discipline:** E65 geometry; soft-cut L3–R bypass only; AND path must remain

## Hypothesis
AND: L1–M, L2–M, M–R (M gated). OR bypass L3–R. Soft I at L3, r=8, frac=1.
1. Fire L1+L2 → R ON ≥0.90 (AND intact after cut prep check after cut)  
2. Fire I → fire L3 → R OFF ≥0.90 (bypass dead)  
3. Fire L1+L2 → R ON ≥0.90 (AND still works after bypass cut)  

## Bars
| ID | thr |
|----|-----|
| B1 AND still ON after cut | ≥0.90 |
| B2 L3 OFF after cut | ≥0.90 |
| B3 L1-only still OFF | ≥0.90 |

Seeds {1951,1961} trials 8. Budget ~4 min, hard cap 8 min.

## Prediction
🔮 LEAN PASS if soft at L3 is local. Miss if cut bleeds to M–R.

## RESULT
**PASS** (2026-07-20). B1=B2=B3=1.0. Soft-cut L3 bypass silences OR arm; AND path and L1-only silence intact.
