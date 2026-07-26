# BP-E174 — Fire-selective residual disrupted by soft R bridge weaken + restore

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** E173 hard kill silences fire-select PASS  
**Discipline:** same bars as E173 but **soft** weaken-bridge at PORT_R (not hard kill)

## Hypothesis
1. After train: fire L-lo → R-hi select ≥0.90  
2. Soft weaken bridges at PORT_R: fire L-lo select **fails** ≥0.70  
3. Restore pair_write brief: fire L-lo select returns ≥0.80  

## Bars
B1 pre ≥0.90 · B2 post-weaken fail ≥0.70 · B3 restore ≥0.80  

Seeds {4621,4631} trials 8. Budget ~18 min, hard cap 36 min.

## Prediction
🔮 LEAN PASS if soft weaken also silences prop (E44-class soft cut). NULL if soft leave residual bridges enough for select.

## RESULT
**PASS** (2026-07-26). B1=B2=B3=1.0. Soft R bridge weaken silences fire-select; pair_write restore returns. Soft+hard (E173/E174) both disrupt fire-select prop.
