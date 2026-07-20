# BP-E82 — Soft 2×2 dual-cut → identity restore → swap reconfig

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E79 identity restore; E80 swap restore; E69 reconfig  
**Discipline:** total soft-cut; restore identity; then soft-cut identity + restore swap (multi-trial after wipe)

## Hypothesis
1. Dual-cut all → OFF ≥0.80  
2. Restore identity → concurrent ON + L0 only R0 ≥0.80  
3. Soft-cut identity arms; restore swap → L0 only R1 ≥0.75  

## Bars
B1 OFF ≥0.80 · B2 identity state ≥0.80 · B3 swap state ≥0.75  

Seeds {2481,2491} trials 6. Budget ~10 min, hard cap 20 min.

## Prediction
🔮 LEAN PASS. Miss if multi-step residual after dual cut blocks swap reconfig.

## RESULT
**PASS** (2026-07-20). B1=B2=B3=1.0. Dual soft-cut → identity restore → swap reconfig multi-trial.
