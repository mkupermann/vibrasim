# BP-E125 — Dual 3-hop **wide** soft wipe-restore + soft re-cut path0

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E123 NULL (y-sep=14 soft re-cut fails); E94/E97 wide-sep soft re-cut doctrine  
**Discipline:** widen y-sep to 24 (> soft r=8) — not bar retune; geometry mechanism for soft re-cut after wipe-restore

## Hypothesis
Path0 y=12, path1 y=36 (sep=24). Soft dual-cut; full restore both; soft re-cut I0 only.
1. Both initial ON ≥0.80  
2. Both after wipe-restore ON ≥0.80  
3. Soft re-cut path0: path0 OFF ∧ path1 ON ≥0.80  

## Bars
B1 both initial ≥0.80 · B2 both after wipe-restore ≥0.80 · B3 soft re-cut ≥0.80  

Seeds {3421,3431} trials 6. Budget ~10 min, hard cap 20 min. Box y ≥50 (use 60).

## Prediction
🔮 LEAN PASS if mid distance was the E123 soft re-cut failure mode; NULL if wipe-restore residual is not sep-limited.

## RESULT
**NULL** (2026-07-20). B1=1.0 B2=1.0 B3=0.0. Wide y-sep=24 does not unlock soft re-cut after wipe-restore on dual 3-hop. E123–E125 class closed NULL: soft/hard/wide re-cut after soft wipe-restore all fail path0 silence.
