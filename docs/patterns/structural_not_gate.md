# Pattern: Structural NOT via bridge kill

## Source
PRIM12-D0 PASS · contrast latch-clear NOT CLOSED (E40/E41)

## Claim
Tagged emitter fire + `fire_kill_bridge_radius` destroys path bridges; later drive cannot re-light output without retrain.

## Use
Hard path disable / emergency cut. Prefer over latch-zero for durable NOT.

## Honesty
Engineered structural edit — not soft dynamics.
