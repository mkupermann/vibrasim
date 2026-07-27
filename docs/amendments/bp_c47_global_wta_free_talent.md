# BP-C47 — Free dual talent with global_wta_k sparse WTA (new mechanism)

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** free dual NULL farm C27–C46; G65 global_wta_k never used in BP free dual  
**Discipline:** **new mechanism** = `global_wta_k=8` (only top-K charged atoms fire per tick) free dual + wall vs k=0. Budget-fit T=500 N=250.

## Hypothesis
Wall ON. Neuron dynamics ON both. Treatment: free dual L-low R-high with `global_wta_k=8`.  
Control: same inject `global_wta_k=0`.  

B1 treat ordered ≥0.90 · B2 ctrl ≤0.80 · B3 treat pop ≥0.80 · B4 delta ≥0.15

## Bars
B1–B4. Seeds {5481,5491} trials 2. T=500. Budget ~8 min, hard cap 16 min.

## Prediction
🔮 LEAN NULL. Global WTA may sparsify firing without unlocking ordered decade talent.

## RESULT
**NULL** (2026-07-26). B1=0.0 B2=0.0 B3=0.0 B4=0.0. global_wta_k=8 collapses treat pop / no ordered unlock.
