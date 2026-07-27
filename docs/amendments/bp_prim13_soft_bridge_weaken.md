# PRIM13 — Soft bridge weaken on fire (reversible inhibit)

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** PRIM12 structural kill PASS; soft reversible cut open  
**Discipline:** not latch-zero; not kill-alive farm

## Primitive
`fire_weaken_bridge_radius: float = 0` (0=off)  
`fire_weaken_bridge_frac: float = 1.0` (1=zero strength)  
When `k_weaken_bridge_emitter[i]=1` fires, for bridges with an endpoint within radius:  
`b_strength *= (1 - frac)` (floor 0). Bridge stays **alive**.

## PRIM13-D0 bars
L–M–R; I near M is weaken-emitter, frac=1, radius covers M.
| ID | Criterion | thr |
|----|-----------|-----|
| B1 | Fire L: end R ≥1.0 | ≥0.90 |
| B2 | Fire I then L: end R ≤0.25 (prop_min blocks) | ≥0.90 |
| B3 | Soft restore: N_write/2 pair events on M–R only, then L: end R ≥1.0 | ≥0.85 |

Seeds {1351,1361} trials 10. prop_min=0.5 so strength 0 blocks.

## Prediction
🔮 PASS: zero strength blocks prop; re-strengthen restores without full L–M retrain.

## RESULT
**NULL** (2026-07-20). B1=**1.0**, B2=**1.0**, B3_restore=**0.0**.  
Soft silence works (I zeros strength → L silent). M–R-only re-strengthen insufficient (I also weakens L–M).
