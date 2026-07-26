# BP-E170 — Pair-link multi-assoc selective residual (engineered bridges)

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** E169 selective residual (likely NULL co-presence); PRIM5 pair-link  
**Discipline:** same selective bars as E169 but train via `apply_ilw_pair_write` + `ilw_pair_link_enabled` (bridges between L/R slots); still no baked map in readout

## Hypothesis
Multislot ON. Pair-link ON (replace OFF).  
Train c0 and c1 via pair_write multi-trial. Probe L-only at c0 vs c1 L-freq.  

1. Probe A L-lo → R high ≥0.80  
2. Probe B L-hi → R low ≥0.80  
3. mean_R(A) > mean_R(B) ≥0.80  

Tests whether engineered pair bridges enable selective residual beyond pure dual ILW co-presence.

## Bars
B1 probeA R high ≥0.80 · B2 probeB R low ≥0.80 · B3 selectivity ≥0.80  

Seeds {4521,4531} trials 8. Budget ~14 min, hard cap 28 min.

## Prediction
🔮 LEAN NULL still — bridges alone do not reweight residual means under L-only rewrite without fire/readout dynamics. PASS only if pair links bias R content under L probe.

## RESULT
**NULL** (2026-07-26). B1=1.0 B2=0.0 B3=0.0. Same failure mode as E169: pair-links do not enable selective residual under L-only rewrite. Engineered bridges ≠ associative readout of partner band.
