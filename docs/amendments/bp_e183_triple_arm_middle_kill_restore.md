# BP-E183 — Triple-arm middle kill + restore (multi-trial K=3 surgery)

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** E182 middle kill PASS; E178 dual-arm restore  
**Discipline:** hard kill R1; verify c0+c2; restore c1 pair_write; verify all three select

## Hypothesis
1. After R1 kill: fire L0 → c0 select ≥0.80  
2. After restore c1: fire L1 → c1 select ≥0.80  
3. After restore: fire L2 still c2 select ≥0.80  

## Bars
B1 post-kill c0 ≥0.80 · B2 restore c1 ≥0.80 · B3 c2 durable ≥0.80  

Seeds {4901,4911} trials 8. Budget ~26 min, hard cap 52 min.

## Prediction
🔮 LEAN PASS extending E182+E178 to K=3 restore.

## RESULT
**PASS** (2026-07-26). B1=B2=B3=1.0. Triple-arm middle kill + restore: c0 survives kill; c1 restores; c2 durable. K=3 multi-trial surgery closed.
