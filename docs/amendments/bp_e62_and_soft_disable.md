# BP-E62 — Soft-disable one input of coincidence AND

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** PRIM9 PASS; E61 NULL (G-self-drive); E45 soft cut  
**Discipline:** PRIM9 dual-input AND geometry; soft-cut **one input arm** to disable AND; restore re-enables

## Hypothesis
L1–M, L2–M, M–R. M is coincidence gate. Soft I near L1–M mid.
1. Fire L1+L2 → R ON ≥0.90  
2. Soft-cut L1–M arm → fire L1+L2 → R OFF ≥0.90 (AND disabled)  
3. Restore L1–M → fire L1+L2 → R ON ≥0.85  

## Bars
| ID | thr |
|----|-----|
| B1 both-on | ≥0.90 |
| B2 soft-disable OFF | ≥0.90 |
| B3 restore ON | ≥0.85 |

Seeds {1811,1821} trials 8. Budget ~4 min, hard cap 8 min.

## Prediction
🔮 LEAN PASS. Miss if soft cut of L1–M also kills L2–M or M–R (collateral).

## RESULT
**NULL** (2026-07-20). B1=1.0 B2=0.0 B3=1.0.  
Soft I at L1–M mid did not silence dual-input AND (both-on still lights R). Likely soft radius misses L1–M endpoints or residual bridges keep coincidence.
