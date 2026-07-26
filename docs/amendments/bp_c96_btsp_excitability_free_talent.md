# BP-C96 — Free dual talent with btsp_excitability_bias (never tried)

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** free dual NULL farm C27–C95; C11 BTSP free dual NULL; `btsp_excitability_bias` never BP free dual  
**Discipline:** **new mechanism** = BTSP ON + elevated excitability bias free dual + wall vs BTSP ON bias=0. Budget-fit T=500 N=250. n_emit=0.

## Hypothesis

Wall ON. Neuron dynamics ON. Both arms `btsp_enabled=True`.  
Treatment: `btsp_excitability_bias=2.0`.  
Control: `btsp_excitability_bias=0.0` (default).

B1 treat ordered ≥0.90 · B2 ctrl ≤0.80 · B3 treat pop ≥0.80 · B4 delta ≥0.15

## Bars

| id | criterion | threshold |
|----|-----------|-----------|
| B1 | treat ordered fraction | ≥0.90 |
| B2 | ctrl ordered fraction | ≤0.80 |
| B3 | treat dual-side L4+ pop | ≥0.80 |
| B4 | B1−B2 | ≥0.15 |

Seeds {7621,7631} trials 2. T=500. Budget ~8 min, hard cap 16 min.

## Prediction

🔮 LEAN NULL. Excitability bias on eligibility unlikely to unlock decade specialisation from free dual inject alone.

## RESULT

**NULL** (2026-07-26). B1=0.50 B2=0.0 B3=0.50 B4=0.50.  
`btsp_excitability_bias=2` with BTSP ON does not unlock free dual talent (B1/B3 fail despite positive delta).

