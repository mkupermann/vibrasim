# BP-E173 — Fire-selective residual disrupted by hard R bridge kill + restore

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** E171 PASS; E165 residual content survives hard kill (content ≠ bridges)  
**Discipline:** train fire-select; hard kill R-port bridges; fire L-lo select fails; re-pair-write restore; fire select returns

## Hypothesis
1. After train: fire L-lo → R-hi select ≥0.90  
2. Hard kill bridges at PORT_R: fire L-lo select **fails** ≥0.70  
3. Restore pair_write c0+c1 brief: fire L-lo select returns ≥0.80  

Tests that E171 select depends on bridges (not only content co-presence).

## Bars
B1 pre-kill select ≥0.90 · B2 post-kill fail ≥0.70 · B3 restore select ≥0.80  

Seeds {4601,4611} trials 8. Budget ~18 min, hard cap 36 min.

## Prediction
🔮 LEAN PASS if hard bridge kill silences latch prop while content remains. NULL if select survives hard kill (content-only path).

## RESULT
**PASS** (2026-07-26). B1=B2=B3=1.0. Hard R bridge kill silences fire-select; pair_write restore returns select. E171 select is **bridge-dependent**, not content-only (contrast E165 residual content survival under hard kill).
