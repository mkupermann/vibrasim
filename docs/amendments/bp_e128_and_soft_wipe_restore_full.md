# BP-E128 — Coincidence AND soft dual wipe both L inputs → full restore → dual fire ON

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** PRIM9-D0 PASS; E63 hard disable; E75 dual soft-cut AND restore  
**Discipline:** pure coincidence AND wipe-restore recovery (both arms) — not dual-3hop re-cut reopen

## Hypothesis
L1,L2 → gated M → R. Soft dual-cut I1+I2 at both L ports; disarm; restore both L1-M and L2-M; re-arm coincidence gate at M.
1. After train: dual fire L1+L2 → R ON ≥0.80; single L1 alone OFF ≥0.80  
2. After dual soft wipe (before restore): dual fire OFF ≥0.80  
3. After full restore both arms: dual fire ON ≥0.80  

## Bars
B1 dual AND initial ≥0.80 · B2 wipe silence dual ≥0.80 · B3 restore dual ON ≥0.80  

Seeds {3521,3531} trials 6. Budget ~8 min, hard cap 16 min.

## Prediction
🔮 LEAN PASS. E75/E77 hybrid class; pure AND dual restore after soft wipe.

## RESULT
**PASS** (2026-07-20). B1=B2=B3=1.0. Coincidence AND soft dual wipe both L inputs → silence dual; full restore both arms → dual fire ON. Pure AND wipe-restore recovery closed.
