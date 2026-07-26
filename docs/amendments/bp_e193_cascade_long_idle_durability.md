# BP-E193 — Content cascade fire-select durability after long idle

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** E186 cascade PASS; E184 one-hop fire-select long-idle PASS  
**Discipline:** dual cascade train; idle T=400; fire-select both paths — multi-hop durability (not mid-hop kill farm)

## Hypothesis
Train dual L→M→R content cascades. Idle 400 ticks. Clear charge/latch.  
1. Fire L0 → path0 select ≥0.80  
2. Fire L1 → path1 select ≥0.80  
3. Both ≥0.70  

## Bars
B1 path0 ≥0.80 · B2 path1 ≥0.80 · B3 both ≥0.70  

Seeds {5261,5271} trials 8. Budget ~20 min, hard cap 40 min.

## Prediction
🔮 LEAN PASS if multi-hop bridges persist like E184 one-hop. NULL if mid-hop decays faster.

## RESULT
**PASS** (2026-07-26). B1=B2=B3=1.0. Dual content cascade fire-select durable after T_IDLE=400 without retrain (multi-hop parity with E184 one-hop).
