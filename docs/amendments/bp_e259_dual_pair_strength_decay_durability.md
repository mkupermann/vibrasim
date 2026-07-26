# BP-E259 — Dual pair selective recall under ilw_strength_decay

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** E253 concurrent dual recall PASS; E254 interleaved PASS; E255 long idle NULL; E252 curriculum decay NULL  
**Discipline:** multi-trial **Y-separated dual pair durability under strength decay** — train both pairs with `ilw_strength_decay_tau>0`, idle, sequential selective both still work. Not reverse cascade; not long-idle T=400 re-probe (E255); not curriculum residual re-probe.

## Hypothesis

Two Y-separated L–R pair-links. `ilw_strength_decay_tau=30`. Train both. Idle T_IDLE=120. Sequential fire L0 / L1.

1. After decay idle: fire L0 → selective R0 ≥0.80  
2. After decay idle: fire L1 → selective R1 ≥0.80  
3. Both in same trial ≥0.70  

## Bars

| id | criterion | threshold |
|----|-----------|-----------|
| B1 | post-decay sel p0 | ≥0.80 |
| B2 | post-decay sel p1 | ≥0.80 |
| B3 | both in same trial | ≥0.70 |

Seeds {7841,7851} trials 6. Budget ~20 min, hard cap 40 min.

## What is NOT claimed

Not E255 long idle without decay. Not free dual. Not residual kill. Not curriculum A→B residual.

## Prediction

🔮 LEAN NULL if strength decay erodes pair-link selective recall over T_IDLE=120 (like E255 long idle collapse). Or LEAN PASS if short decay idle preserves structure.

## RESULT

*(filled after run)*
