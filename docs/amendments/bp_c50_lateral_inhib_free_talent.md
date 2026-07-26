# BP-C50 — Free dual talent with G8 lateral_inhibition (never tried)

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** C12 STDP free dual NULL; G8 lateral_inhibition never BP-tested on free dual  
**Discipline:** **new mechanism** = `lateral_inhibition_enabled=True` with `stdp_enabled=True` (G8 needs STDP LTP) free dual + wall vs STDP-only control. Budget-fit T=500 N=250.

## Hypothesis
Wall ON. Neuron dynamics ON. STDP ON both arms.  
Treatment: lateral_inhibition_enabled. Control: lateral_inhibition off.  

B1 treat ordered ≥0.90 · B2 ctrl ≤0.80 · B3 treat pop ≥0.80 · B4 delta ≥0.15

## Bars
B1–B4. Seeds {5621,5631} trials 2. T=500. Budget ~8 min, hard cap 16 min.

## Prediction
🔮 LEAN NULL. Bridge competition unlikely to create decade order from free dual inject alone (C12 STDP already NULL).

## RESULT
**NULL** (2026-07-26). B1=0.25 B2=0.0 B3=0.25 B4=0.25. G8 lateral_inhibition + STDP does not unlock free dual talent.
