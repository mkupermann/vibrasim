# BP-C89 — Free dual talent with synaptic_post_search_samples (never tried)

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** free dual NULL farm C27–C88; C74 synaptic_transmission_strength NULL; `synaptic_post_search_samples` never BP free dual  
**Discipline:** **new mechanism** = elevated post-search samples free dual + wall vs default 1 (transmission strength default both). Budget-fit T=500 N=250. n_emit=0.

## Hypothesis

Wall ON. Neuron dynamics ON. Both arms default `synaptic_transmission_strength=0.5`.  
Treatment: `synaptic_post_search_samples=5`.  
Control: `synaptic_post_search_samples=1` (default).

B1 treat ordered ≥0.90 · B2 ctrl ≤0.80 · B3 treat pop ≥0.80 · B4 delta ≥0.15

## Bars

| id | criterion | threshold |
|----|-----------|-----------|
| B1 | treat ordered fraction | ≥0.90 |
| B2 | ctrl ordered fraction | ≤0.80 |
| B3 | treat dual-side L4+ pop | ≥0.80 |
| B4 | B1−B2 | ≥0.15 |

Seeds {7141,7151} trials 2. T=500. Budget ~8 min, hard cap 16 min.

## Prediction

🔮 LEAN NULL. Post-search sampling on bridges unlikely to unlock free dual decade order without engineered ports.

## RESULT

**NULL** (2026-07-26). B1=0.0 B2=0.25 B3=0.25 B4=-0.25.  
Elevated `synaptic_post_search_samples=5` does not unlock free dual talent.

