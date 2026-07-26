# BP-C85 — Free dual talent with repulsion_threshold_ratio (never tried)

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** free dual NULL farm C27–C84; C30 atom_repulsion_k; `repulsion_threshold_ratio` never BP free dual  
**Discipline:** **new mechanism** = lowered repulsion threshold ratio free dual + wall vs default. Budget-fit T=500 N=250. n_emit=0.

## Hypothesis

Wall ON. Neuron dynamics ON. Default `repulsion_threshold_ratio=1000` (effectively sparse repulsion).  
Treatment: free dual L-low R-high with `repulsion_threshold_ratio=2.0` (repulsion engages more readily).  
Control: `repulsion_threshold_ratio=1000.0` (default).

B1 treat ordered ≥0.90 · B2 ctrl ≤0.80 · B3 treat pop ≥0.80 · B4 delta ≥0.15

## Bars

| id | criterion | threshold |
|----|-----------|-----------|
| B1 | treat ordered fraction | ≥0.90 |
| B2 | ctrl ordered fraction | ≤0.80 |
| B3 | treat dual-side L4+ pop | ≥0.80 |
| B4 | B1−B2 | ≥0.15 |

Seeds {6981,6991} trials 2. T=500. Budget ~8 min, hard cap 16 min.

## Prediction

🔮 LEAN NULL. Stronger repulsion more likely homogenises or collapses pop than unlocks decade order.

## RESULT

**NULL** (2026-07-26). B1=0.25 B2=0.25 B3=0.50 B4=0.0.  
Lowered `repulsion_threshold_ratio=2` does not unlock free dual talent; no delta vs default.

