# BP-E171 — Fire-readout selective residual (freq-matched L fire → bridge charge)

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** E169/E170 NULL (L-only rewrite mean fails select); PRIM5 pair-link; circuit fire/latch readout  
**Discipline:** multi-assoc train with pair-links; **new readout** = charge only L nodes matching probe band; score R partner **peak latch** via bridge prop (not residual means)

## Hypothesis
Multislot ON. Pair-link ON. Train c0 (L=500↔R=5000) and c1 (L=5000↔R=500) multi-trial via `apply_ilw_pair_write`.  
Neuron dynamics + bridge_charge_prop. Clear charge/latch.  

**Probe A:** fire L-side k-nodes with |log f − log 500| small; measure peak latch on R high vs R low.  
**Probe B:** fire L-side with f near 5000; peak latch R low vs R high.  

1. Probe A: peak_R_high ≥ 1.0 and peak_R_high > peak_R_low ≥0.80  
2. Probe B: peak_R_low ≥ 1.0 and peak_R_low > peak_R_high ≥0.80  
3. Both A and B pass on same trial rate ≥0.70  

Tests associative selective residual under fire/bridge dynamics.

## Bars
B1 probeA select ≥0.80 · B2 probeB select ≥0.80 · B3 both ≥0.70  

Seeds {4541,4551} trials 8. Budget ~16 min, hard cap 32 min.

## Prediction
🔮 LEAN NULL if pair slots do not segregate bridges by band; LEAN PASS if multislot+pair links form band-matched bridges and fire prop selects partner.

## RESULT
**PASS** (2026-07-26). B1=B2=B3=1.0. Freq-matched L fire + bridge charge prop selects R partner latch under multislot pair-link multi-assoc train. **Selective residual requires fire/bridge readout**, not L-only rewrite residual means (E169/E170 NULL).
