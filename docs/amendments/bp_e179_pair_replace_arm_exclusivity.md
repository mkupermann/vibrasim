# BP-E179 — Pair-replace arm exclusivity (last association wins fire-select)

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** E171 both arms with replace OFF; PRIM8 pair_replace  
**Discipline:** shared L/R ports; train c0 then c1 with `ilw_pair_replace_enabled=True`; fire-select only last arm

## Hypothesis
Multislot ON. Shared PORT_L/PORT_R.  
**Treatment replace ON:** train c0 then c1 multi-trial.  
1. Fire L-hi → R-lo select (c1 last) ≥0.80  
2. Fire L-lo → R-hi select **fails** (c0 replaced) ≥0.70  
**Control replace OFF:** same train both; fire L-lo → R-hi select ≥0.80  

## Bars
B1 treat c1 select ≥0.80 · B2 treat c0 fail ≥0.70 · B3 ctrl c0 select ≥0.80  

Seeds {4761,4771} trials 8. Budget ~18 min, hard cap 36 min.

## Prediction
🔮 LEAN PASS if replace drops other endpoint bridges (PRIM8). NULL if multislot retains both paths under fire-select.

## RESULT
**NULL** (2026-07-26). B1=1.0 B2=0.0 B3=1.0. Replace ON keeps c1 select and control c0 select, but **c0 fire-select still succeeds after c1 train** (B2 fail). PRIM8 replace does not enforce exclusive last-arm fire-select under multislot shared ports.
