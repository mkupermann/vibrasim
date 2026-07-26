# BP-E255 — Dual pair-link selective recall after long idle

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** E253 concurrent dual recall PASS; E254 interleaved train-test PASS; E184 fire-select long idle (shared port)  
**Discipline:** multi-trial **Y-separated dual pair durability** — train both pairs, long idle without retrain, sequential selective recall both still work. Not reverse cascade; not interleaved re-probe alone; not E184 shared-port residual.

## Hypothesis

Two Y-separated L–R pair-links. Train both. Idle T_IDLE=400. Then sequential fire L0 / L1.

1. After idle: fire L0 → selective R0 ≥0.80  
2. After idle: fire L1 → selective R1 ≥0.80  
3. Both sequential arms succeed in same trial ≥0.70  

## Bars

| id | criterion | threshold |
|----|-----------|-----------|
| B1 | post-idle rev/sel p0 | ≥0.80 |
| B2 | post-idle sel p1 | ≥0.80 |
| B3 | both in same trial | ≥0.70 |

Seeds {7681,7691} trials 6. Budget ~22 min, hard cap 44 min.

## What is NOT claimed

Not reverse cascade. Not free dual. Not interleaved train-test re-probe (E254). Not residual kill.

## Prediction

🔮 LEAN PASS if pair-link structure holds through long idle like E184 fire-select durability.

## RESULT

**NULL** (2026-07-26). B1=0.0 B2=0.0 B3=0.0.  
After T_IDLE=400 (full), dual pair selective recall fails both paths. Smoke (T_IDLE=100) was PASS-shaped — long idle erodes dual Y-pair selective recall under this scaffold. Finding: dual pair durability does **not** match E184 fire-select long-idle at T_IDLE=400.

