# BP-E48 — Retrain after XOR structural cut

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E42 XOR PASS; E43 retrain after cut PASS

## Hypothesis
1. XOR train; fire L1 → R ON ≥0.85  
2. Fire both L → cut; fire L1 → R OFF ≥0.85  
3. Retrain OR path only (L1–Mor–R, L2–Mor–R, no Mand re-arm); fire L1 → R ON ≥0.85  

## Bars
| ID | thr |
|----|-----|
| B1 L1 ON pre-cut | ≥0.85 |
| B2 L1 OFF after both-cut | ≥0.85 |
| B3 L1 ON after OR retrain | ≥0.85 |

Seeds {1481,1491} trials 8.

## Prediction
🔮 PASS.

## RESULT
**PASS** (2026-07-20). B1=1.0 B2=1.0 B3=1.0. XOR cut then OR retrain restores L1→R.
