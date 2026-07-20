# BP-E38 — AND-gate boundary (expect NULL)

**PRE-REGISTERED 2026-07-20 before data**  
**Hard negative:** does fan-in require **both** L1 and L2?

## Hypothesis (likely false)
Fire L1 only → R peak ≤0.25; fire L2 only → R≤0.25; fire **both** → R≥1.0.  
If L1 alone already lights R (E34 OR), B1 fails → **NULL** documents no AND without new primitive.

## Bars
| ID | Criterion | thr |
|----|-----------|-----|
| B1 | L1 only R≤0.25 | ≥0.85 |
| B2 | L2 only R≤0.25 | ≥0.85 |
| B3 | both L R≥1.0 | ≥0.85 |

Seeds {1141,1151} trials 8. Same topology as E34.

## Prediction
🔮 **NULL** — E34 OR means B1/B2 fail.

## RESULT
**NULL** (2026-07-20). B1=0 B2=0 B3=1.0. Prediction HIT: OR not AND; single L still lights R. AND needs new primitive.
