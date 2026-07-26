# BP-E251 — Concurrent reverse+forward triple-path mixed drive

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** E240 concurrent forward+reverse dual PASS; E248 concurrent reverse triple PASS  
**Discipline:** multi-trial **mixed-direction triple** — fire L0 (fwd→R0), R1 (rev→L1), L2 (fwd→R2) in one prop window; all three targets light. Not pure reverse triple re-probe; not dual mix re-probe alone.

## Hypothesis

Three Y-separated L–M–R cascades. Train all three.

1. Concurrent mixed drive: peak R0 ≥1.0 ≥0.80  
2. Concurrent mixed drive: peak L1 ≥1.0 ≥0.80  
3. Concurrent mixed drive: peak R2 ≥1.0 and all three in trial ≥0.70  

## Bars

| id | criterion | threshold |
|----|-----------|-----------|
| B1 | concurrent R0 lit (fwd p0) | ≥0.80 |
| B2 | concurrent L1 lit (rev p1) | ≥0.80 |
| B3 | concurrent all three targets | ≥0.70 |

Seeds {7521,7531} trials 6. Budget ~24 min, hard cap 48 min.

## What is NOT claimed

Not pure reverse triple (E248). Not dual mix only (E240). Not mid-kill. Not free dual.

## Prediction

🔮 LEAN PASS if Y-isolation supports mixed-direction concurrent drive across three paths.

## RESULT

**PASS** (2026-07-26). B1=1.0 B2=1.0 B3=1.0.  
Concurrent mixed drive L0(fwd)+R1(rev)+L2(fwd) lights R0, L1, R2. Mixed-direction triple concurrent works under Y-isolation.

