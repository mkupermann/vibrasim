# BP-C84 — Free dual talent with polarity_split (never tried)

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** free dual NULL farm C27–C83; `polarity_split` never BP free dual (C46 was polarity knob class but different — this is spawn polarity fraction)  
**Discipline:** **new mechanism** = asymmetric polarity_split free dual + wall vs default 0.5. Budget-fit T=500 N=250. n_emit=0.

## Hypothesis

Wall ON. Neuron dynamics ON.  
Treatment: free dual L-low R-high with `polarity_split=0.9` (strongly biased polarity at generation/defaults interaction).  
Control: `polarity_split=0.5` (default).

Note: free dual inject sets polarity by slot index; polarity_split may only affect residual generation paths — still an honest never-tried WorldConfig probe.

B1 treat ordered ≥0.90 · B2 ctrl ≤0.80 · B3 treat pop ≥0.80 · B4 delta ≥0.15

## Bars

| id | criterion | threshold |
|----|-----------|-----------|
| B1 | treat ordered fraction | ≥0.90 |
| B2 | ctrl ordered fraction | ≤0.80 |
| B3 | treat dual-side L4+ pop | ≥0.80 |
| B4 | B1−B2 | ≥0.15 |

Seeds {6941,6951} trials 2. T=500. Budget ~8 min, hard cap 16 min.

## Prediction

🔮 LEAN NULL. Inject-driven free dual largely ignores polarity_split; unlikely decade unlock.

## RESULT

**NULL** (2026-07-26). B1=0.0 B2=0.25 B3=0.0 B4=-0.25.  
`polarity_split=0.9` does not unlock free dual talent; treat pop collapses (B3=0).

