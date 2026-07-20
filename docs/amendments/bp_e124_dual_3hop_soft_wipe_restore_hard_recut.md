# BP-E124 — Dual 3-hop soft wipe both → full restore → hard re-cut path0

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E123 NULL (soft re-cut fails); E93/E98 hard re-cut after full restore doctrine  
**Discipline:** hard local kill re-cut after soft wipe-restore on dual 3-hop — not soft re-cut retune

## Hypothesis
Same geometry as E123 (y-sep=14). Soft dual-cut I0+I1; full restore both; **hard-cut** I0 only (r=8 kill).
1. Both initial ON ≥0.80  
2. Both after wipe-restore ON ≥0.80  
3. Hard re-cut path0: path0 OFF ∧ path1 ON ≥0.80  

## Bars
B1 both initial ≥0.80 · B2 both after wipe-restore ≥0.80 · B3 hard re-cut ≥0.80  

Seeds {3401,3411} trials 6. Budget ~10 min, hard cap 20 min.

## Prediction
🔮 LEAN PASS. Hard re-cut after full restore fixes soft collateral (E93-class).

## RESULT
**NULL** (2026-07-20). B1=1.0 B2=1.0 B3=0.0. Soft wipe-restore both OK; hard re-cut path0 after full restore also fails (same B3=0 as E123 soft re-cut). Dual 3-hop post-wipe-restore re-cut resists soft and hard local kill at I0.
