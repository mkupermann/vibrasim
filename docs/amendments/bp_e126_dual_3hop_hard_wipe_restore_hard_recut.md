# BP-E126 — Dual 3-hop **hard** wipe both → full restore → hard re-cut path0

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E123–E125 CLOSED NULL (soft wipe then re-cut fails); E56 hard selective pristine  
**Discipline:** **new base** = hard dual wipe (not soft wipe) then hard re-cut — not reopening soft-wipe class

## Hypothesis
Same geometry as E123 (y-sep=14). Hard dual-cut I0+I1; full restore both; hard re-cut I0 only.
1. Both initial ON ≥0.80  
2. Both after hard wipe-restore ON ≥0.80  
3. Hard re-cut path0: path0 OFF ∧ path1 ON ≥0.80  

## Bars
B1 both initial ≥0.80 · B2 both after wipe-restore ≥0.80 · B3 hard re-cut ≥0.80  

Seeds {3441,3451} trials 6. Budget ~10 min, hard cap 20 min.

## Prediction
🔮 LEAN PASS if soft-wipe residual blocked re-cut; hard wipe may leave cleaner structure for hard re-cut. LEAN NULL if dual 3-hop re-cut after any wipe-restore is blocked.

## RESULT
**NULL** (2026-07-20). B1=1.0 B2=1.0 B3=0.0. Hard dual wipe + full restore both OK; hard re-cut I0 still fails path0 silence. Soft wipe base is not the sole cause — hard wipe base same failure mode.
