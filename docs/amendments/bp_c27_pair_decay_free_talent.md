# BP-C27 — Free dual talent with **short pair_decay_time** (new mechanism, budget-fit)

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** C16 family CLOSED PARTIAL; C24–C26 NULL/FAILED  
**Discipline:** **new mechanism** = short `pair_decay_time` (faster unbound structure churn) during free dual inject + wall — not dual-inject+decay alone, not port-seed/scaffold/latch. **Budget-fit:** T=500, N_SIDE=250, 2 seeds × 2 trials (hard cap 12 min).

## Hypothesis
Wall ON. Treatment: free dual L-low R-high with `pair_decay_time=15`.  
Control: same free dual with `pair_decay_time=60` (default).  
Success: treatment ordered ≥0.90; control ≤0.80; delta ≥0.15; treat pop ≥0.80.

## Bars
| ID | Criterion | thr |
|----|-----------|-----|
| B1 | Treatment ordered mean_decade L < R | ≥0.90 |
| B2 | Control ordered | ≤0.80 |
| B3 | Treatment both sides populated | ≥0.80 |
| B4 | Treatment − control delta | ≥0.15 |

Seeds {4321,4331} trials 2. T=500. N_SIDE=250. Box 80×50×50 mid=40. n_nodes_max=8192. Budget ~6 min, hard cap 12 min.

## Prediction
🔮 LEAN NULL. Faster pair decay may thin structure without unlocking ordered talent; maps pair-decay free class under tight wallclock.

## RESULT
**NULL** (2026-07-20). B1=0.5 B2=0.0 B3=0.5 B4=0.5. Short pair_decay_time does not unlock free dual talent (pop and ordered both short of bars).
