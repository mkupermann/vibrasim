# BP-C101 — Free dual talent with dream_hallucination_strength (never tried)

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** free dual NULL farm C27–C100; C13 dream free dual NULL; `dream_hallucination_strength` never BP free dual treatment  
**Discipline:** **new mechanism** = dream_mode ON + elevated hallucination strength free dual + wall vs default strength. Budget-fit T=500 N=250. n_emit=0.

## Hypothesis

Wall ON. Neuron dynamics ON. Both arms `dream_mode_enabled=True`.  
Treatment: `dream_hallucination_strength=2.0`.  
Control: `dream_hallucination_strength=1.0` (default).

B1 treat ordered ≥0.90 · B2 ctrl ≤0.80 · B3 treat pop ≥0.80 · B4 delta ≥0.15

## Bars

| id | criterion | threshold |
|----|-----------|-----------|
| B1 | treat ordered fraction | ≥0.90 |
| B2 | ctrl ordered fraction | ≤0.80 |
| B3 | treat dual-side L4+ pop | ≥0.80 |
| B4 | B1−B2 | ≥0.15 |

Seeds {7821,7831} trials 2. T=500. Budget ~8 min, hard cap 16 min.

## Prediction

🔮 LEAN NULL. Dream hallucination on free dual inject unlikely to unlock decade specialisation.

## RESULT

**NULL** (2026-07-26). B1=0.0 B2=0.50 B3=0.25 B4=-0.50.  
Elevated `dream_hallucination_strength=2` does not unlock free dual talent; treat worse than control.

