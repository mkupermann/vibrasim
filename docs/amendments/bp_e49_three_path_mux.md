# BP-E49 — Three-path soft MUX curriculum

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E45/E46 selective soft cut

## Hypothesis
Three parallel L–M–R paths (y=12,25,38). I_k near each M_k.  
Curriculum: cut all but path k for k=1,2,3 in sequence (restore previous before next cut).

| ID | Criterion | thr |
|----|-----------|-----|
| B1 | Select path1 only: R1≥1, R2≤0.25, R3≤0.25 | ≥0.80 |
| B2 | Then select path2 only | ≥0.80 |
| B3 | Then select path3 only | ≥0.80 |

Seeds {1501,1511} trials 6 (heavier).

## Prediction
🔮 LEAN PASS; miss if I radii overlap.

## RESULT
**PASS** (2026-07-20). B1=1.0 B2=1.0 B3=1.0. Three-path soft MUX curriculum.
