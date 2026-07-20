# BP-E35 — Diamond path redundancy

**PRE-REGISTERED 2026-07-20 before data**

## Hypothesis
L→M1→R and L→M2→R (two parallel mids). Fire L → R peak≥1.0 ≥0.90.  
Ablation: kill all bridges incident on M1 after train → still R≥1.0 ≥0.85 (M2 path).  
Ablation both mids' outbound: R≤0.25 ≥0.90.

## Bars
| ID | thr |
|----|-----|
| B1 full diamond R≥1 | ≥0.90 |
| B2 kill M1 path still R≥1 | ≥0.85 |
| B3 kill M1 and M2 out still R≤0.25 | ≥0.90 |

Seeds {1081,1091} trials 8.

## Prediction
🔮 PASS lean; miss if kill is incomplete.

## RESULT
*(after)*
