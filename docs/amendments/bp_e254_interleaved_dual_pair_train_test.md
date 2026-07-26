# BP-E254 — Interleaved multi-trial dual pair train-test (no G12)

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** E16 selective recall; E20 peak partner; E253 concurrent dual recall PASS  
**Discipline:** multi-trial **interleaved train-test** — alternate train A / probe A / train B / probe B across trials; both pairs stay selective without G12/pattern tags. Not reverse cascade; not residual kill; not curriculum residual A→B re-probe (E252).

## Hypothesis

Two Y-separated L–R pair-links. For each outer trial cycle: train path0, fire L0 check R0; train path1, fire L1 check R1. Aggregate over cycles.

1. Path0 selective success rate across interleaved cycles ≥0.80  
2. Path1 selective success rate across interleaved cycles ≥0.80  
3. Both paths succeed in same cycle ≥0.70  

## Bars

| id | criterion | threshold |
|----|-----------|-----------|
| B1 | path0 selective rate | ≥0.80 |
| B2 | path1 selective rate | ≥0.80 |
| B3 | both in same cycle | ≥0.70 |

Seeds {7641,7651} trials 4 outer × 4 interleaved cycles. Budget ~20 min, hard cap 40 min.

## What is NOT claimed

Not G12. Not reverse cascade. Not free dual. Not concurrent dual re-probe alone (E253).

## Prediction

🔮 LEAN PASS if pair-links hold under interleaved multi-trial write/probe pressure without pattern tags.

## RESULT

**PASS** (2026-07-26). B1=1.0 B2=1.0 B3=1.0.  
Interleaved train/probe A then B multi-trial: both pairs stay selective without G12. Port multi-trial interleaved durability.

