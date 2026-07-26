# BP-C38 — Free dual talent with corr_plasticity Hebbian bridges (new mechanism)

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** C16 CLOSED PARTIAL; BET-099 corr_plasticity never tried in free dual C family  
**Discipline:** **new mechanism** = `corr_plasticity_rate>0` co-firing bridge drive during free dual + wall vs rate=0. Budget-fit T=500 N=250.

## Hypothesis
Wall ON. Neuron dynamics ON both arms. Treatment: free dual L-low R-high with `corr_plasticity_rate=0.5`.  
Control: same inject `corr_plasticity_rate=0`.  

B1 treat ordered ≥0.90 · B2 ctrl ≤0.80 · B3 treat pop ≥0.80 · B4 delta ≥0.15

## Bars
B1–B4. Seeds {5041,5051} trials 2. T=500. Budget ~8 min, hard cap 16 min.

## Prediction
🔮 LEAN NULL. Hebbian bridge corr during free dual unlikely to unlock ordered talent (may need structured co-fire).

## RESULT
**NULL** (2026-07-26). B1=0.0 B2=0.0 B3=0.0 B4=0.0. corr_plasticity free dual collapses treat pop; no ordered talent unlock.
