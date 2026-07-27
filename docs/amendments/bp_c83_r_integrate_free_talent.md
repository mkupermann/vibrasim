# BP-C83 — Free dual talent with r_integrate (never tried)

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** free dual NULL farm C27–C82; `r_integrate` never BP free dual  
**Discipline:** **new mechanism** = elevated integrate radius free dual + wall vs default. Budget-fit T=500 N=250. n_emit=0 (avoid C80-class emit slowdown).

## Hypothesis

Wall ON. Neuron dynamics ON.  
Treatment: free dual L-low R-high with `r_integrate=12.0` (wider charge integration neighbourhood).  
Control: `r_integrate=5.0` (default).

B1 treat ordered ≥0.90 · B2 ctrl ≤0.80 · B3 treat pop ≥0.80 · B4 delta ≥0.15

## Bars

| id | criterion | threshold |
|----|-----------|-----------|
| B1 | treat ordered fraction | ≥0.90 |
| B2 | ctrl ordered fraction | ≤0.80 |
| B3 | treat dual-side L4+ pop | ≥0.80 |
| B4 | B1−B2 | ≥0.15 |

Seeds {6901,6911} trials 2. T=500. Budget ~8 min, hard cap 16 min.

## Prediction

🔮 LEAN NULL. Wider integrate radius may blur more than specialise free dual decade order.

## RESULT

**NULL** (2026-07-26). B1=0.50 B2=0.25 B3=0.75 B4=0.25.  
Elevated `r_integrate=12` does not meet treat order bar (B1); B4 delta passes alone but talent unlock fails. No free dual unlock.

