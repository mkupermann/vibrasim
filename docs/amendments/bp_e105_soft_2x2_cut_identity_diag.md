# BP-E105 — Soft 2×2 full restore then soft-cut identity diagonal (00+11)

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E104 cut both in-edges PASS; E80 swap  
**Discipline:** after full restore, soft-cut **identity diagonal** → pure swap routing

## Hypothesis
Wide 2×2. Soft dual-cut all; restore all; soft-cut 00 and 11.
1. After full restore: concurrent both R ON ≥0.80  
2. Soft-cut 00+11: L0 → R1 ON R0 OFF ≥0.80 (swap)  
3. L1 → R0 ON R1 OFF ≥0.80 (swap)  

## Bars
B1 concurrent after full ≥0.80 · B2 L0 swap ≥0.80 · B3 L1 swap ≥0.80  

Seeds {3001,3011} trials 6. Budget ~10 min, hard cap 20 min.

## Prediction
🔮 LEAN PASS (E104 composition on diagonal). Miss if soft cut collaterals swap mids.

## RESULT
**PASS** (2026-07-20). B1=B2=B3=1.0. Soft-cut identity diagonal after full restore yields pure swap routing.
