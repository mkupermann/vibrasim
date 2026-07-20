# BP-E86 — Soft DEMUX dual-cut all arms then selective arm0 restore

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E57 soft DEMUX; E79 dual-cut restore  
**Discipline:** shared L fan-out three R; soft-cut all three arms; disarm; restore arm0 only

## Hypothesis
1. Soft-cut all arms → fire L → all R OFF ≥0.80  
2. Disarm; restore arm0 only → R0 ON, R1/R2 OFF ≥0.80  
3. Soft-cut arm0; restore arm1 → R1 ON, R0/R2 OFF ≥0.75  

## Bars
B1 all OFF ≥0.80 · B2 select0 ≥0.80 · B3 select1 ≥0.75  

Seeds {2561,2571} trials 6. Budget ~8 min, hard cap 16 min.

## Prediction
🔮 LEAN PASS. Miss if shared L residual bridges light wrong R after selective restore.

## RESULT
**PASS** (2026-07-20). B1=B2=B3=1.0. Soft DEMUX dual-cut all arms OFF; selective restore arm0 then arm1.
