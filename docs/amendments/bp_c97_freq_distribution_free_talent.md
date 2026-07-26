# BP-C97 — Free dual talent with freq_distribution (never tried)

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** free dual NULL farm C27–C96; `freq_distribution` never BP free dual  
**Discipline:** **new mechanism** = freq_distribution linear vs log free dual + wall (inject still log-sampled; knob may affect residual spawn paths). Budget-fit T=500 N=250. n_emit=0.

## Hypothesis

Wall ON. Neuron dynamics ON.  
Treatment: free dual L-low R-high with `freq_distribution="linear"`.  
Control: `freq_distribution="log"` (default).

Note: free dual inject uses log-uniform sampling in runner; treatment still sets WorldConfig freq_distribution for any internal generation.

B1 treat ordered ≥0.90 · B2 ctrl ≤0.80 · B3 treat pop ≥0.80 · B4 delta ≥0.15

## Bars

| id | criterion | threshold |
|----|-----------|-----------|
| B1 | treat ordered fraction | ≥0.90 |
| B2 | ctrl ordered fraction | ≤0.80 |
| B3 | treat dual-side L4+ pop | ≥0.80 |
| B4 | B1−B2 | ≥0.15 |

Seeds {7661,7671} trials 2. T=500. Budget ~8 min, hard cap 16 min.

## Prediction

🔮 LEAN NULL. Inject-driven free dual largely ignores freq_distribution; unlikely decade unlock.

## RESULT

**NULL** (2026-07-26). B1=0.0 B2=0.0 B3=0.25 B4=0.0.  
`freq_distribution=linear` vs log does not unlock free dual talent.

