# BP-E210 — Reverse split soft-kill L1 then retrain-restore reverse pid2

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** E209 PASS reverse soft-kill; E200 forward soft-kill restore  
**Discipline:** multi-trial reverse curriculum under G12+split: soft kill L1 silences reverse pid2; reverse pid1 survives; retrain L1↔R1 restores reverse pid2.

## Hypothesis
1. Soft kill L1: fire R1 → L1 reverse **fails** ≥0.70  
2. Soft kill L1: pid1; fire R0 → L0 reverse ≥0.80  
3. Retrain L1–R1 (pid2): fire R1 → L1 reverse ≥0.80  

## Bars
B1 post soft reverse pid2 fail ≥0.70 · B2 reverse pid1 survives ≥0.80 · B3 restore reverse pid2 ≥0.80  

Seeds {5961,5971} trials 6. Budget ~20 min, hard cap 40 min.

## Prediction
🔮 LEAN PASS if retrain rebuilds reverse path like E200 forward restore.

## RESULT
**PASS** (2026-07-26). B1=1.0 B2=1.0 B3=1.0. Soft kill L1 silences reverse pid2; reverse pid1 survives; retrain restores reverse pid2.
