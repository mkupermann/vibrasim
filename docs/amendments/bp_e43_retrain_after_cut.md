# BP-E43 — Retrain restores path after structural NOT

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** PRIM12 PASS; multi-trial recovery

## Hypothesis
1. Train L–M–R; fire L → R ≥1.0 ≥0.90  
2. Fire I (kill bridges near M); fire L → R ≤0.25 ≥0.90  
3. **Retrain** M–R (and L–M if needed) with ILW pair_write; fire L → R ≥1.0 ≥0.90  

## Bars
| ID | thr |
|----|-----|
| B1 initial L→R ON | ≥0.90 |
| B2 after cut L→R OFF | ≥0.90 |
| B3 after retrain L→R ON | ≥0.90 |

Seeds {1331,1341} trials 10.

## Prediction
🔮 PASS: retrain rebuilds exclusive links.

## RESULT
**PASS** (2026-07-20). B1=1.0 B2=1.0 B3=1.0. Path cut by I; retrain restores L→R.
