# BP-E65 — (L1∧L2) OR L3 hybrid path

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** PRIM9 AND; E34 OR; E63 hard AND disable  
**Discipline:** compose AND fan-in with independent OR bypass

## Hypothesis
AND branch: L1–M, L2–M, M–R (M coincidence gate).  
OR bypass: L3–R direct (no gate).
1. Fire L1+L2 → R ON ≥0.90 (AND path)  
2. Fire L3 alone → R ON ≥0.90 (bypass)  
3. Fire L1 alone → R OFF ≥0.90 (AND incomplete, no bypass)  

## Bars
| ID | thr |
|----|-----|
| B1 AND path ON | ≥0.90 |
| B2 OR bypass ON | ≥0.90 |
| B3 L1-only OFF | ≥0.90 |

Seeds {1931,1941} trials 8. Budget ~4 min, hard cap 8 min.

## Prediction
🔮 LEAN PASS if spatial isolation keeps L3–R free of coincidence gating. Miss if L3 charge leaks into gated M.

## RESULT
**PASS** (2026-07-20). B1=B2=B3=1.0. (L1∧L2) OR L3 hybrid: AND path, OR bypass, L1-only silent.
