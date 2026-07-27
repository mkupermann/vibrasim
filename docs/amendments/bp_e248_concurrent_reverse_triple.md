# BP-E248 — Concurrent reverse triple-path drive

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** E230 concurrent dual reverse PASS; E232 concurrent forward  
**Discipline:** multi-trial **triple concurrent reverse** — fire R0+R1+R2 same prop window; all three L targets light. Not dual concurrent re-probe alone; not mid-kill.

## Hypothesis

Three Y-separated L–M–R cascades. Train all three. Concurrent fire all three R ports.

1. Concurrent: peak L0 ≥1.0 ≥0.80  
2. Concurrent: peak L1 ≥1.0 ≥0.80  
3. Concurrent: peak L2 ≥1.0 and all three lit in trial ≥0.70  

## Bars

| id | criterion | threshold |
|----|-----------|-----------|
| B1 | concurrent L0 lit | ≥0.80 |
| B2 | concurrent L1 lit | ≥0.80 |
| B3 | concurrent all three L lit | ≥0.70 |

Seeds {7421,7431} trials 6. Budget ~24 min, hard cap 48 min.

## What is NOT claimed

Not dual concurrent re-probe only. Not free dual. Not mid-kill.

## Prediction

🔮 LEAN PASS if Y-isolation scales to three concurrent reverse paths.

## RESULT

**PASS** (2026-07-26). B1=1.0 B2=1.0 B3=1.0.  
Concurrent fire R0+R1+R2 lights all three L reverse targets. Triple concurrent reverse scales under Y-isolation.

