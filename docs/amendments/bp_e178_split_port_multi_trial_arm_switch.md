# BP-E178 — Multi-trial split-port arm switch (kill c0 → c1 on → restore c0 → both)

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** E177 split-port arm-selective kill PASS  
**Discipline:** one train; hard kill R0; verify c1; restore pair_write c0; verify c0 and c1

## Hypothesis
Split ports as E177.  
1. After R0 hard kill: fire L1 → c1 select ≥0.80  
2. After restore c0 pair_write: fire L0 → c0 select ≥0.80  
3. After restore: fire L1 still c1 select ≥0.80  

## Bars
B1 post-kill c1 ≥0.80 · B2 restore c0 ≥0.80 · B3 c1 durable ≥0.80  

Seeds {4741,4751} trials 8. Budget ~20 min, hard cap 40 min.

## Prediction
🔮 LEAN PASS extending E177 multi-trial restore.

## RESULT
**PASS** (2026-07-26). B1=B2=B3=1.0. Multi-trial split-port arm switch: kill c0 → c1 on → restore c0 → both.
