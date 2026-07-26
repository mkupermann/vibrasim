# BP-C95 — Free dual talent with t_refractory (never free dual knob)

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** free dual NULL farm C27–C94; `t_refractory` used as fixed param not free dual treatment  
**Discipline:** **new mechanism** = elevated t_refractory free dual + wall vs default 0.05. Budget-fit T=500 N=250. n_emit=0.

## Hypothesis

Wall ON. Neuron dynamics ON.  
Treatment: free dual L-low R-high with `t_refractory=0.20` (long refractory).  
Control: `t_refractory=0.05` (default).

B1 treat ordered ≥0.90 · B2 ctrl ≤0.80 · B3 treat pop ≥0.80 · B4 delta ≥0.15

## Bars

| id | criterion | threshold |
|----|-----------|-----------|
| B1 | treat ordered fraction | ≥0.90 |
| B2 | ctrl ordered fraction | ≤0.80 |
| B3 | treat dual-side L4+ pop | ≥0.80 |
| B4 | B1−B2 | ≥0.15 |

Seeds {7581,7591} trials 2. T=500. Budget ~8 min, hard cap 16 min.

## Prediction

🔮 LEAN NULL. Longer refractory more likely suppresses firing than unlocks decade order.

## RESULT

**NULL** (2026-07-26). B1=0.25 B2=0.0 B3=0.25 B4=0.25.  
Elevated `t_refractory=0.20` does not unlock free dual talent.

