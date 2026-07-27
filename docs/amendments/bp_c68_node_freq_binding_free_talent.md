# BP-C68 — Free dual talent with node_freq_binding OFF (never tried)

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** free dual NULL farm C27–C67; node_freq_binding defaults True, never BP-ablated on free dual  
**Discipline:** **new mechanism** = `node_freq_binding=False` (proximity-only node→node bind) free dual + wall vs True. Budget-fit T=500 N=250.

## Hypothesis
Wall ON. Neuron dynamics ON. Treatment: free dual L-low R-high with node_freq_binding=False.  
Control: node_freq_binding=True (default).  

B1 treat ordered ≥0.90 · B2 ctrl ≤0.80 · B3 treat pop ≥0.80 · B4 delta ≥0.15

## Bars
B1–B4. Seeds {6341,6351} trials 2. T=500. Budget ~8 min, hard cap 16 min.

## Prediction
🔮 LEAN NULL. Removing 8% node binding rule may increase mess without decade order unlock.

## RESULT
**PASS** (2026-07-26). B1=1.0 B2=0.5 B3=1.0 B4=0.5.  
`node_freq_binding=False` (proximity-only node→node bind) unlocks ordered free dual talent vs default ON.  
**Prediction miss:** 🔮 LEAN NULL; outcome PASS — proximity binding helps decade segregation more than expected.  
**Caution:** budget-fit 2×2; recommend larger-N replicate before treating as robust (C42-class risk).
