# BP-E93 — Soft DEMUX full restore then hard re-cut arm0

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E92 NULL (soft re-cut collaterals)  
**Discipline:** not E92 soft retune — after full soft-wipe+restore, **hard kill** arm0 only (endpoint-local)

## Hypothesis
Same E92 geometry (y=12,25,38). Soft dual-cut all; restore all three; hard I at arm0 I with `fire_kill_bridge_radius=8`.
1. After full restore: fire L → all three R ON ≥0.80  
2. Hard-cut arm0 → R0 OFF, R1 and R2 ON ≥0.80  
3. L still drives R1 and R2 ≥0.80  

## Bars
B1 all ON after full ≥0.80 · B2 selective hard cut0 ≥0.80 · B3 R1&R2 still ON ≥0.80  

Seeds {2701,2711} trials 6. Budget ~10 min, hard cap 20 min.

## Prediction
🔮 LEAN PASS if hard r=8 is more local than soft r=10. Miss if hard kill at I0 still hits M1.

## RESULT
**PASS** (2026-07-20). B1=B2=B3=1.0. After soft dual-cut + full restore, **hard** re-cut arm0 silences R0 only; R1/R2 stay ON. Closes E92 soft-recut collateral with hard endpoint-local kill.
