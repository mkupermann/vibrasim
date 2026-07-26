# BP-E155 — Port dual-side decade specialisation soft wipe + ILW restore

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E154 PASS  
**Discipline:** **port content wipe-restore** — soft dual wipe of L/R ports then re-ILW dual decade; not free talent; not circuit routing farm

## Hypothesis
Wall ON. Soft dual-cut weaken at L and R ports after initial dual decade write; idle; re-ILW L-low R-high.  
1. After initial dual decade write: ordered ≥0.90  
2. After soft dual wipe + idle: ordered fails in ≥0.70 of trials (disruption rate)  
3. After re-ILW restore: ordered ≥0.90  

## Bars
B1 initial ordered ≥0.90 · B2 post-wipe disruption rate ≥0.70 · B3 post-restore ordered ≥0.90  

Seeds {4141,4151} trials 8. Budget ~8 min, hard cap 16 min.

## Prediction
🔮 LEAN PASS if soft weaken disrupts port content; LEAN NULL if decade nodes survive soft wipe without bridge-like kill.

## RESULT
**NULL** (2026-07-20). B1=1.0 B2=0.0 B3=1.0. Soft dual wipe of port regions does **not** disrupt dual decade specialisation (ordered survives). Soft bridge-weaken is not a content-wipe for decade nodes.
