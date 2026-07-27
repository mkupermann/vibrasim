# BP-C104 — Free dual talent with correlation plasticity ON (BET-099 Hebbian, never as free dual)

**PRE-REGISTERED 2026-07-27 before data**  
**Depends on:** free dual NULL farm C27–C103; BET-099 `apply_correlation_plasticity` (Hebbian co-firing bridge write over the bistable barrier); C50 lateral_inhibition NULL  
**Discipline:** **new mechanism** = correlational (Hebbian) plasticity ON free dual + wall vs OFF. `compartment_boundary=0` (no engineered cross-write block — this is the *free* test, not the BET-103 engineered compartment). Budget-fit T=500 N=250. n_emit=0.

## Hypothesis

Wall ON. Neuron dynamics ON. `compartment_boundary=0.0` (free, not engineered).  
Treatment: `corr_plasticity_rate=1.0` (Hebbian co-firing write ON), `corr_potentiation` default 1.0.  
Control: `corr_plasticity_rate=0.0` (OFF).

Correlational plasticity is the canonical mechanism by which co-active same-decade atoms on one side strengthen intra-side bonds and self-organise into decade-selective structure. If any free-chemistry lever unlocks free dual, this is the most principled candidate in the config surface.

B1 treat ordered ≥0.90 · B2 ctrl ordered ≤0.80 · B3 treat pop ≥0.80 · B4 delta ≥0.15

## Bars

| id | criterion | threshold |
|----|-----------|-----------|
| B1 | treat ordered fraction | ≥0.90 |
| B2 | ctrl ordered fraction | ≤0.80 |
| B3 | treat dual-side L4+ pop | ≥0.80 |
| B4 | B1−B2 | ≥0.15 |

Seeds {7921,7931} trials 2. T=500. Budget ~9 min, hard cap 18 min.

## What is NOT claimed

Not the BET-103 engineered compartment (`compartment_boundary>0`). Not ILW ports. Not dual-drive frequency talent (C1–C3). Free co-firing plasticity only.

## Prediction

🔮 LEAN NULL. 60+ free-chemistry levers NULL (C27–C103). Hebbian co-firing plasticity strengthens whatever co-fires, but with the physical wall already separating sides and no decade-selective write signal, co-firing alone is unlikely to drive mean(L decade) < mean(R decade) at the 0.90 bar. Still the strongest untried candidate — a PASS would be a genuine free-chemistry talent finding.

## RESULT

*(filled after run)*
