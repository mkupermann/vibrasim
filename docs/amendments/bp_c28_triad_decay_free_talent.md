# BP-C28 — Free dual talent with **short triad_decay_time** (new mechanism, budget-fit)

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** C16 CLOSED PARTIAL; C24–C27 NULL/FAILED  
**Discipline:** **new mechanism** = short `triad_decay_time` (faster higher-order structure churn) during free dual inject + wall. Budget-fit: T=500, N_SIDE=250, 2×2 trials, hard cap 12 min.

## Hypothesis
Wall ON. Treatment: free dual L-low R-high with `triad_decay_time=80`.  
Control: same with `triad_decay_time=600` (default).  
Success: treatment ordered ≥0.90; control ≤0.80; treat pop ≥0.80; delta ≥0.15.

## Bars
| ID | Criterion | thr |
|----|-----------|-----|
| B1 | Treatment ordered | ≥0.90 |
| B2 | Control ordered | ≤0.80 |
| B3 | Treatment pop | ≥0.80 |
| B4 | Delta | ≥0.15 |

Seeds {4361,4371} trials 2. T=500. N_SIDE=250. n_nodes_max=8192. Budget ~6 min, hard cap 12 min.

## Prediction
🔮 LEAN NULL. Shorter triad decay unlikely to unlock free dual ordered talent.

## RESULT
**NULL** (2026-07-26). B1=0.50 B2=0.25 B3=0.75 B4=0.25. Short triad_decay_time does not unlock free dual ordered talent (B1/B3 fail). Same family as C24–C27 decay/inject ceiling.
