# BP-E212 — Split-port reverse hard-kill L1; reverse pid1 survives

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** E209 reverse soft-kill PASS; E177 forward hard kill  
**Discipline:** split L0/R0 pid1 + L1/R1 pid2; train-time tags; reverse fire R→L; **hard kill L1** (not soft). Complements E209 soft path.

## Hypothesis
1. Pre: pid2; fire R1 → L1 reverse ≥0.90  
2. Hard kill L1: fire R1 → L1 reverse **fails** ≥0.70  
3. Hard kill L1: pid1; fire R0 → L0 reverse ≥0.80  

## Bars
B1 pre reverse pid2 ≥0.90 · B2 post reverse pid2 fail ≥0.70 · B3 reverse pid1 survives ≥0.80  

Seeds {6041,6051} trials 6. Budget ~20 min, hard cap 40 min.

## Prediction
🔮 LEAN PASS if hard kill isolates reverse arm like soft E209 / forward E177.

## RESULT
**PASS** (2026-07-26). B1=1.0 B2=1.0 B3=1.0. Hard kill L1 silences reverse pid2; reverse pid1 survives under G12+split.
