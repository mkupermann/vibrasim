# BP-E209 — Split-port reverse soft-kill L1; reverse pid1 survives

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** E199 forward split soft-kill; reverse+G12 CLOSED E205–E208  
**Discipline:** split L0/R0 pid1 + L1/R1 pid2; train-time tags; reverse fire R→L; soft kill **L1** (reverse target of pid2). New vs closed reverse+G12.

## Hypothesis
1. Pre: pid2; fire R1 → L1 reverse select ≥0.90  
2. Soft kill L1: fire R1 → L1 reverse **fails** ≥0.70  
3. Soft kill L1: pid1; fire R0 → L0 reverse select ≥0.80  

## Bars
B1 pre reverse pid2 ≥0.90 · B2 post reverse pid2 fail ≥0.70 · B3 reverse pid1 survives ≥0.80  

Seeds {5921,5931} trials 6. Budget ~20 min, hard cap 40 min.

## Prediction
🔮 LEAN PASS if spatial split isolates reverse soft kill on L1 like E199 on R1.

## RESULT
**PASS** (2026-07-26). B1=1.0 B2=1.0 B3=1.0. Soft kill L1 silences reverse pid2; reverse pid1 survives under G12+split.
