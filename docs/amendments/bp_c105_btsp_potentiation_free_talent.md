# BP-C105 — Free dual talent with elevated btsp_potentiation (never as free dual)

**PRE-REGISTERED 2026-07-27 before data**  
**Depends on:** free dual NULL farm C27–C104; C96 btsp_excitability_bias NULL; G14 BTSP (behavioral-timescale plasticity). `btsp_potentiation` magnitude never a free-dual treatment.  
**Discipline:** **new lever** = elevated per-event BTSP potentiation magnitude free dual + wall, vs default. Both arms `btsp_enabled=True`. Budget-fit T=500 N=250. n_emit=0.

## Hypothesis

Wall ON. Neuron dynamics ON. Both arms `btsp_enabled=True`.  
Treatment: `btsp_potentiation=150.0`.  
Control: `btsp_potentiation=50.0` (default).

Stronger one-shot BTSP potentiation of co-active assemblies could lock decade-consistent structures on each side harder than the default, sharpening spontaneous specialisation.

B1 treat ordered ≥0.90 · B2 ctrl ordered ≤0.80 · B3 treat pop ≥0.80 · B4 delta ≥0.15

## Bars

| id | criterion | threshold |
|----|-----------|-----------|
| B1 | treat ordered fraction | ≥0.90 |
| B2 | ctrl ordered fraction | ≤0.80 |
| B3 | treat dual-side L4+ pop | ≥0.80 |
| B4 | B1−B2 | ≥0.15 |

Seeds {7941,7951} trials 2. T=500. Budget ~9 min, hard cap 18 min.

## What is NOT claimed

Not C96 btsp_excitability_bias. Not ILW ports. Not engineered compartment. Not dual-drive frequency (C1–C3). Magnitude-only lever on an already-enabled BTSP.

## Prediction

🔮 LEAN NULL. C96 excitability NULL; C104 Hebbian corr-plasticity NULL. Stronger BTSP potentiation amplifies whatever plateaus fire, but without a decade-selective plateau signal it amplifies both correct and incorrect structure — unlikely to clear the 0.90 bar.

## RESULT

**NULL** (2026-07-27). B1=0.25 B2=0.25 B3=0.25 B4=0.00.
Elevated BTSP potentiation (150 vs 50) has zero effect — treatment identical to control (delta 0.00). Tripling the one-shot potentiation magnitude neither sharpens nor harms specialisation, because without a decade-selective plateau signal there is nothing selective to amplify. Extends NULL farm C27–C104 → C105.
