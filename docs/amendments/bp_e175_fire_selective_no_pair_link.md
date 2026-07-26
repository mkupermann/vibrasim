# BP-E175 — Fire-selective residual without pair-link (pure dual ILW)

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** E171 PASS with pair-link; E170 mean-select NULL without fire  
**Discipline:** train c0+c1 via dual `apply_ilw_port_event` only; **`ilw_pair_link_enabled=False`**; same fire-select bars as E171

## Hypothesis
Multislot ON. Pair-link OFF.  
1. Fire L-lo → R-hi select ≥0.80  
2. Fire L-hi → R-lo select ≥0.80  
3. Both ≥0.70  

Tests whether fire-select requires engineered pair bridges or emerges from dual ILW content alone.

## Bars
B1 L-lo→R-hi ≥0.80 · B2 L-hi→R-lo ≥0.80 · B3 both ≥0.70  

Seeds {4641,4651} trials 8. Budget ~16 min, hard cap 32 min.

## Prediction
🔮 LEAN NULL — without pair-links, bridge graph may not connect matched L/R slots; fire prop fails select. PASS only if dual ILW spontaneously forms usable bridges.

## RESULT
**NULL** (2026-07-26). B1=B2=B3=0.0. Pure dual ILW without pair-link does **not** support fire-select. Engineered pair bridges are necessary (E171 family depends on PRIM5 pair-link).
