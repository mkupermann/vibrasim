# BP-E169 — Map-free selective residual (probe L band selects R partner)

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** E166 multi-assoc capacity PASS; residual co-presence ≠ selective recall  
**Discipline:** multislot ON dual associations; L-only probe at c0 vs c1 L-freq; score R residual **selectivity** without baked class map

## Hypothesis
Multislot ON. c0: L=500↔R=5000 · c1: L=5000↔R=500.  
N_train=12 each dual (c0 then c1). Separate probes (fresh train each):  
- Probe A: L-only rewrite 500 → expect R mean high (c0 partner)  
- Probe B: L-only rewrite 5000 → expect R mean low (c1 partner)  

1. Probe A: R high residual ≥0.80  
2. Probe B: R low residual ≥0.80  
3. Selectivity: on paired trials, mean_R(A) > mean_R(B) ≥0.80  

Harder than co-presence (E162/E166). LEAN NULL if both R bands always co-present so means do not flip with L probe.

## Bars
B1 probeA R high ≥0.80 · B2 probeB R low ≥0.80 · B3 mean_R(A)>mean_R(B) ≥0.80  

Seeds {4501,4511} trials 8. Budget ~14 min, hard cap 28 min.

## Prediction
🔮 LEAN NULL. Multislot capacity retains both R bands; L-only rewrite does not selectively suppress the non-partner (not generative E12; not associative readout).

## RESULT
**NULL** (2026-07-26). B1=1.0 B2=0.0 B3=0.0. Probe A shows R-high residual (co-presence), but probe B does not yield R-low and mean_R(A)>mean_R(B) never holds. Capacity ≠ selective residual; L-only rewrite does not select partner band.
