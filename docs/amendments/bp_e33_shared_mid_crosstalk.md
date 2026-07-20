# BP-E33 — Shared mid node crosstalk (boundary)

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E31 parallel isolation PASS

## Hypothesis
Two chains share **one mid M**: L1–M–R1 and L2–M–R2 (replace OFF). Fire L1 only: R1 peak≥1.0 ≥0.85 **and** R2 peak≥1.0 ≥0.85 (crosstalk expected — shared M).  
Control separate mids (E31-like): fire L1 → R2 peak≤0.25 ≥0.85.

Bars:
| ID | Criterion | thr |
|----|-----------|-----|
| B1 | Shared: fire L1 R1≥1 | ≥0.85 |
| B2 | Shared: fire L1 R2≥1 (crosstalk) | ≥0.85 |
| B3 | Separate mids: fire L1 R2≤0.25 | ≥0.85 |

If B1∧B2: shared mid **leaks**. Isolation requires distinct mids (E31).

## Prediction
🔮 PASS on all — shared M must light both R.

## RESULT
**PASS** (2026-07-20). B1=1.0 B2=1.0 B3=1.0. Shared mid **leaks** to both R; separate mids isolate (E31).
