# BP-E46 — Multi-trial path switch via soft cut/restore

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E45 selective soft cut PASS

## Hypothesis
Two paths. Curriculum: (1) both ON; (2) soft-cut path1, only path2 ON; (3) restore path1 + soft-cut path2, only path1 ON.

| ID | Criterion | thr |
|----|-----------|-----|
| B1 | Phase both: R1≥1 and R2≥1 | ≥0.85 |
| B2 | Phase cut1: R1≤0.25 and R2≥1 | ≥0.85 |
| B3 | Phase cut2 after restore1: R1≥1 and R2≤0.25 | ≥0.85 |

Seeds {1441,1451} trials 8. I1 near M1, I2 near M2.

## Prediction
🔮 PASS.

## RESULT
**PASS** (2026-07-20). B1=1.0 B2=1.0 B3=1.0. Multi-trial switch: both → cut1 → restore1+cut2.
