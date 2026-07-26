# BP-C94 — Free dual talent with synaptic_transmission_threshold (never tried)

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** free dual NULL farm C27–C93; C74 synaptic_transmission_strength NULL; `synaptic_transmission_threshold` never BP free dual  
**Discipline:** **new mechanism** = elevated synaptic_transmission_threshold free dual + wall vs default. Both arms strength=0.5. Budget-fit T=500 N=250. n_emit=0.

## Hypothesis

Wall ON. Neuron dynamics ON. Both arms `synaptic_transmission_strength=0.5`.  
Treatment: `synaptic_transmission_threshold=20.0` (high activation bar).  
Control: `synaptic_transmission_threshold=5.0` (default).

B1 treat ordered ≥0.90 · B2 ctrl ≤0.80 · B3 treat pop ≥0.80 · B4 delta ≥0.15

## Bars

| id | criterion | threshold |
|----|-----------|-----------|
| B1 | treat ordered fraction | ≥0.90 |
| B2 | ctrl ordered fraction | ≤0.80 |
| B3 | treat dual-side L4+ pop | ≥0.80 |
| B4 | B1−B2 | ≥0.15 |

Seeds {7541,7551} trials 2. T=500. Budget ~8 min, hard cap 16 min.

## Prediction

🔮 LEAN NULL. Transmission threshold unlikely to unlock free dual decade specialisation from inject alone.

## RESULT

**NULL** (2026-07-26). B1=0.50 B2=0.25 B3=0.50 B4=0.25.  
Elevated `synaptic_transmission_threshold=20` does not unlock free dual talent (B1/B3 fail).

