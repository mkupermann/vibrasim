# BP-C43 — Replicate C42 wider freq_tolerance free dual (larger N)

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** C42 PASS budget-fit (2 seeds × 2 trials)  
**Discipline:** **honest replication** — same mechanism and **same bars** as C42; larger sample only (no bar retune, no threshold change)

## Hypothesis
Same as C42: free dual L-low R-high wall ON; treat `freq_tolerance=0.08` vs ctrl `0.03`.  
Expect treat ordered ≥0.90; ctrl ≤0.80; treat pop ≥0.80; delta ≥0.15 on expanded seed×trial set.

## Bars
Identical to C42:  
B1 treat ordered ≥0.90 · B2 ctrl ordered ≤0.80 · B3 treat pop ≥0.80 · B4 delta ≥0.15  

Seeds {5281,5291,5301,5311,5321} trials 3 (N=15 treat + 15 ctrl). T=500. N_SIDE=250. Budget ~15 min, hard cap 30 min.

## Prediction
🔮 LEAN PASS if C42 is real. NULL if budget-fit C42 was seed-set lucky (honest failure mode).

## RESULT
**NULL** (2026-07-26). B1=0.6667 B2=0.2667 B3=1.0 B4=0.40 (n=15+15). Treat ordered **below** 0.90 bar despite positive delta. **C42 budget-fit PASS does not replicate** at larger N under same bars. Wide freq_tol free dual is **fragile / seed-set sensitive**, not a locked unlock. No bar retune.
