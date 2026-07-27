# BP-E188 — Cascade mid-hop kill + restore multi-trial

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** E187 mid-hop kill (if PASS); E186 cascade  
**Discipline:** hard kill M0; path1 on; restore path0 L-M-R links; path0 select returns; path1 durable

## Hypothesis
1. After M0 kill: fire L1 → path1 select ≥0.80  
2. After restore path0 pair_writes: fire L0 → path0 select ≥0.80  
3. After restore: fire L1 still path1 ≥0.80  

## Bars
B1 post-kill p1 ≥0.80 · B2 restore p0 ≥0.80 · B3 p1 durable ≥0.80  

Seeds {5081,5091} trials 8. Budget ~22 min, hard cap 44 min.

## Prediction
🔮 LEAN PASS if E187 mid-kill works and restore re-links cascade.

## RESULT
**PASS** (2026-07-26). B1=B2=B3=1.0. Mid-hop kill + restore multi-trial: path1 on after M0 kill; path0 restore returns select; path1 durable.
