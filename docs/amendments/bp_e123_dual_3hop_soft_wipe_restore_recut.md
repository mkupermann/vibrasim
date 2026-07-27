# BP-E123 — Dual 3-hop soft dual-cut wipe → full restore both → soft re-cut path0

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E56 PASS (hard selective on dual 3-hop); port wipe-restore doctrine  
**Discipline:** soft wipe both 3-hop paths, full restore both, soft selective re-cut path0 only — y-sep > soft radius

## Hypothesis
Path0: L0-A0-B0-R0 (y=18). Path1: L1-A1-B1-R1 (y=32). I0 at path0 mid; I1 at path1 mid.  
1. After train: both paths ON ≥0.80  
2. Soft dual-cut I0+I1 then full restore both: both ON ≥0.80  
3. Soft re-cut I0 only: path0 OFF ∧ path1 ON ≥0.80  

## Bars
B1 both initial ≥0.80 · B2 both after wipe-restore ≥0.80 · B3 selective re-cut ≥0.80  

Seeds {3381,3391} trials 6. Budget ~10 min, hard cap 20 min.  
`fire_weaken_bridge_radius=8`; y-sep=14 > 8.

## Prediction
🔮 LEAN PASS if soft re-cut local like E94/E97 wide-sep doctrine on 3-hop dual.

## RESULT
**NULL** (2026-07-20). B1=1.0 B2=1.0 B3=0.0. Soft dual wipe + full restore both works; soft re-cut path0 after full restore fails path0 silence / isolation (B3). Soft re-cut after wipe-restore on dual 3-hop does not match E56 hard-selective success on pristine train.
