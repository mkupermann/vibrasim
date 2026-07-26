# BP-E213 — Reverse split hard-kill L1 then retrain-restore reverse pid2

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** E212 PASS reverse hard-kill; E210 reverse soft restore  
**Discipline:** multi-trial reverse under G12+split: hard kill L1 silences reverse pid2; reverse pid1 survives; retrain L1↔R1 restores reverse pid2. Completes hard path of reverse surgery.

## Hypothesis
1. Hard kill L1: fire R1 → L1 reverse **fails** ≥0.70  
2. Hard kill L1: pid1; fire R0 → L0 reverse ≥0.80  
3. Retrain L1–R1 (pid2): fire R1 → L1 reverse ≥0.80  

## Bars
B1 post hard reverse pid2 fail ≥0.70 · B2 reverse pid1 survives ≥0.80 · B3 restore reverse pid2 ≥0.80  

Seeds {6081,6091} trials 6. Budget ~20 min, hard cap 40 min.

## Prediction
🔮 LEAN PASS if retrain rebuilds after hard kill like E210 soft restore / E183 hard restore.

## RESULT
**PASS** (2026-07-26). B1=1.0 B2=1.0 B3=1.0. Hard kill L1 silences reverse pid2; reverse pid1 survives; retrain restores reverse pid2.
