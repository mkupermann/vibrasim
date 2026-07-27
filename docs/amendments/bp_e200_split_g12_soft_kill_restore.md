# BP-E200 — Split-port G12 soft-kill R1 then retrain-restore pid2

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** E199 PASS soft-kill arm-selective; E183 hard kill+restore; E44 soft restore  
**Discipline:** multi-trial curriculum under G12+split: soft kill R1 silences pid2; pid1 survives; retrain L1↔R1 restores pid2 select. Not E199 (no restore); not E183 (no G12/soft).

## Hypothesis
1. Soft kill R1: fire L1 → R1 select **fails** ≥0.70  
2. Soft kill R1: active_pattern_id=1; fire L0 → R0 select ≥0.80  
3. Retrain L1–R1 (pid2 tags): fire L1 → R1 select ≥0.80  

## Bars
B1 post soft pid2 fail ≥0.70 · B2 pid1 survives ≥0.80 · B3 restore pid2 ≥0.80  

Seeds {5561,5571} trials 6. Budget ~20 min, hard cap 40 min.

## Prediction
🔮 LEAN PASS if retrain ILW rebuilds soft-weakened bridges on split R1 under G12 (E44-class restore + E199 isolation).

## RESULT
**PASS** (2026-07-26). B1=1.0 B2=1.0 B3=1.0. Soft kill R1 silences pid2; pid1 survives; retrain L1–R1 restores pid2 under G12+split.
