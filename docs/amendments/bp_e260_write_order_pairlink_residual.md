# BP-E260 — Write-order residual with pair-link ON (novel metric class)

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** E168 write-order gap residual (pair_link OFF); E167 temporal-gap residual  
**Discipline:** multi-trial **write-order residual** with `ilw_pair_link_enabled=True` — L-first vs R-first dual-port curriculum; residual R high after L-only probe. Not residual kill farm; not reverse cascade; not dual decade multislot re-probe.

## Hypothesis

Shared midplane L–R ports. Pair-link ON, multislot OFF (match E168 scaffold + pair_link).

1. L-first train: after L-only probe, R residual high (≥ F_MID) ≥0.80  
2. R-first train: after L-only probe, R residual high ≥0.80  
3. Abs delta between L-first and R-first residual rates ≤0.25  

## Bars

| id | criterion | threshold |
|----|-----------|-----------|
| B1 | L-first residual R high | ≥0.80 |
| B2 | R-first residual R high | ≥0.80 |
| B3 | abs(B1−B2) ≤0.25 | ≤0.25 |

Seeds {7881,7891} trials 6. Budget ~18 min, hard cap 36 min.

## What is NOT claimed

Not soft/hard residual kill. Not free dual. Not E168 re-probe without pair_link (pair_link is the new mechanism).

## Prediction

🔮 LEAN PASS if pair-link preserves bidirectional residual co-presence independent of write order (like E168 side residual).

## RESULT

*(filled after run)*
