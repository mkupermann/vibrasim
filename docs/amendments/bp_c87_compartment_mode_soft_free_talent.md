# BP-C87 — Free dual talent with compartment_mode soft (never tried)

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** free dual NULL farm C27–C86; C71 compartment_k (clamp) NULL; `compartment_mode=soft` never BP free dual  
**Discipline:** **new mechanism** = compartment_k ON + mode soft vs clamp free dual + wall. Budget-fit T=500 N=250. n_emit=0.

## Hypothesis

Wall ON. Neuron dynamics ON. Both arms `compartment_k=1.0`, centre/radius as C71.  
Treatment: `compartment_mode="soft"`.  
Control: `compartment_mode="clamp"`.

B1 treat ordered ≥0.90 · B2 ctrl ≤0.80 · B3 treat pop ≥0.80 · B4 delta ≥0.15

## Bars

| id | criterion | threshold |
|----|-----------|-----------|
| B1 | treat ordered fraction | ≥0.90 |
| B2 | ctrl ordered fraction | ≤0.80 |
| B3 | treat dual-side L4+ pop | ≥0.80 |
| B4 | B1−B2 | ≥0.15 |

Seeds {7061,7071} trials 2. T=500. Budget ~8 min, hard cap 16 min.

## Prediction

🔮 LEAN NULL. Soft vs clamp compartment boundary unlikely to unlock decade order over clamp (C71 already NULL for k-on).

## RESULT

**NULL** (2026-07-26). B1=0.50 B2=0.25 B3=0.50 B4=0.25.  
`compartment_mode=soft` vs clamp does not unlock free dual talent (B1/B3 fail; B4 alone not enough).

