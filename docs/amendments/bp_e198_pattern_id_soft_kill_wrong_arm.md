# BP-E198 — Soft-kill wrong-arm pattern endpoints; correct arm survives under G12

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** E194–E197 G12 class; E180 split-port soft kill  
**Discipline:** train-time tag c0/c1; soft kill R-lo (c1 partner) only; pid1 select still works; pid2 select fails

## Hypothesis
Train-time tagged dual assoc. Soft weaken at PORT_R among R-lo only (freq < F_MID).  

1. active_pattern_id=1; fire L-lo → R-hi select ≥0.80  
2. active_pattern_id=2; fire L-hi → R-lo select **fails** ≥0.70  
3. Pre-kill: pid2 select works ≥0.80 (sanity)  

## Bars
B1 pid1 post-kill ≥0.80 · B2 pid2 post-kill fail ≥0.70 · B3 pre pid2 ≥0.80  

Seeds {5501,5511} trials 8. Budget ~20 min, hard cap 40 min.

## Prediction
🔮 LEAN PASS if soft kill on R-lo endpoints silences c1 path only (spatial+freq local).

## RESULT
**NULL** (2026-07-26). B1=0.0 B2=1.0 B3=1.0. Soft kill R-lo silences pid2 (intended) but also kills pid1 select (B1 fail). Shared PORT_R spatial locality — soft weaken spills to both R bands (E176-class shared-port limit). Wrong-arm soft surgery needs split ports or finer targeting.
