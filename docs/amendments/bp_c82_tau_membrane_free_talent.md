# BP-C82 — Free dual talent with tau_membrane (never tried)

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** free dual NULL farm C27–C81; `tau_membrane` never BP free dual  
**Discipline:** **new mechanism** = elevated membrane time-constant free dual + wall vs default. Budget-fit T=500 N=250.

## Hypothesis

Wall ON. Neuron dynamics ON.  
Treatment: free dual L-low R-high with `tau_membrane=2.0` (slower charge decay → longer integration).  
Control: `tau_membrane=0.5` (default).

B1 treat ordered ≥0.90 · B2 ctrl ≤0.80 · B3 treat pop ≥0.80 · B4 delta ≥0.15

## Bars

| id | criterion | threshold |
|----|-----------|-----------|
| B1 | treat ordered fraction | ≥0.90 |
| B2 | ctrl ordered fraction | ≤0.80 |
| B3 | treat dual-side L4+ pop | ≥0.80 |
| B4 | B1−B2 | ≥0.15 |

Seeds {6861,6871} trials 2. T=500. Budget ~8 min, hard cap 16 min.

## Prediction

🔮 LEAN NULL. Integration tau unlikely to create decade specialisation from free dual inject alone.

## RESULT

**NULL** (2026-07-26). B1=0.0 B2=0.25 B3=0.25 B4=-0.25.  
Elevated `tau_membrane=2.0` does not unlock free dual talent; treat pop weak; no positive delta.

