# BP-C77 — Free dual talent with membrane_channel_uptake (never tried)

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** free dual NULL farm C27–C76; C65 membrane_channel_k NULL; membrane_channel_uptake never BP free dual  
**Discipline:** **new mechanism** = `membrane_channel_k>0` + `membrane_channel_uptake=True` free dual + wall vs channel without uptake. Budget-fit T=500 N=250.

## Hypothesis
Wall ON. Neuron dynamics ON. Treatment: free dual L-low R-high with membrane_channel_k=1.0, membrane_channel_uptake=True, mode=atom.  
Control: membrane_channel_k=1.0, membrane_channel_uptake=False.  

B1 treat ordered ≥0.90 · B2 ctrl ≤0.80 · B3 treat pop ≥0.80 · B4 delta ≥0.15

## Bars
B1–B4. Seeds {6701,6711} trials 2. T=500. Budget ~8 min, hard cap 16 min.

## Prediction
🔮 LEAN NULL. Uptake needs formed membrane atoms; free dual inject unlikely to unlock decade order via uptake toggle.

## RESULT
**NULL** (2026-07-26). B1=0.25 B2=0.0 B3=0.5 B4=0.25. membrane_channel_uptake does not unlock free dual talent.
