# BP-C90 — Free dual talent with bridge_charge_prop_rate (never free dual)

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** free dual NULL farm C27–C89; bridge_charge_prop used in port curricula not free dual talent  
**Discipline:** **new mechanism** = elevated bridge charge prop free dual + wall vs off. Budget-fit T=500 N=250. n_emit=0.

## Hypothesis

Wall ON. Neuron dynamics ON.  
Treatment: free dual L-low R-high with `bridge_charge_prop_rate=2.5`.  
Control: `bridge_charge_prop_rate=0.0` (default).

B1 treat ordered ≥0.90 · B2 ctrl ≤0.80 · B3 treat pop ≥0.80 · B4 delta ≥0.15

## Bars

| id | criterion | threshold |
|----|-----------|-----------|
| B1 | treat ordered fraction | ≥0.90 |
| B2 | ctrl ordered fraction | ≤0.80 |
| B3 | treat dual-side L4+ pop | ≥0.80 |
| B4 | B1−B2 | ≥0.15 |

Seeds {7181,7191} trials 2. T=500. Budget ~8 min, hard cap 16 min.

## Prediction

🔮 LEAN NULL. Charge prop needs strong oriented bridges; free dual inject unlikely to form load-bearing prop chains for decade order.

## RESULT

**NULL** (2026-07-26). B1=0.25 B2=0.0 B3=0.25 B4=0.25.  
`bridge_charge_prop_rate=2.5` free dual does not unlock talent (B1/B3 fail; B4 alone not enough).

