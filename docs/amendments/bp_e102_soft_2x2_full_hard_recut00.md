# BP-E102 — Soft 2×2 full restore then hard re-cut arm 00

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E101 NULL (soft re-cut 00 fails)  
**Discipline:** not E101 soft retune — after dual-cut full restore, **hard kill arm 00** only

## Hypothesis
Same wide 2×2 geometry as E101. Soft dual-cut all; restore all; hard I at 00 mid, `fire_kill_bridge_radius=8`.
1. After full restore: L0 fan-out R0 and R1 ON ≥0.80  
2. Hard-cut 00: L0 → R0 OFF, R1 ON ≥0.80  
3. L1 → R0 and R1 ON ≥0.80  

## Bars
B1 L0 fan-out ≥0.80 · B2 hard cut00 ≥0.80 · B3 L1 both ≥0.80  

Seeds {2901,2911} trials 6. Budget ~10 min, hard cap 20 min.

## Prediction
🔮 LEAN PASS (E98/E93 doctrine on 2×2). Miss if hard kill at M00 hits M01.

## RESULT
**NULL** (2026-07-20). B1=1.0 B2=0.0 B3=1.0.  
Hard re-cut 00 also fails to silence L0→R0 after full restore (same failure mode as soft E101). 2×2 single-arm re-cut after full fan-out restore not reliable under this layout.
