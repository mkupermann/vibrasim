# BET-089 — Bistable Bridge Latch (Memory)

Pre-registered: 2026-05-30. Implements the mechanism BET-087/088 found
missing: bistable (hysteretic) bridge strength.

## Hypothesis

Bridges with double-well strength dynamics (stable WEAK and STRONG
states, unstable barrier between) latch: a flux pulse that pushes a
bridge past the barrier leaves it STRONG after the pulse stops. The
latched pattern is memory — a record of past flux, not a mirror of
present flux.

## Mechanism

ds/dt = -k*(s-low)*(s-mid)*(s-high) + flux_drive
low=1 (weak well), mid=3 (barrier), high=6 (strong well).
Localized slow-vibration stimulus drives flux in one region.

## Acceptance bars

| ID | Criterion | Bar |
|----|-----------|-----|
| T89a | Latch up | during stimulus, stimulated-region bridges reach STRONG (mean > mid=3) |
| T89b | Memory | >= 2000s AFTER stimulus stops, stimulated bridges stay STRONG (mean > mid) |
| T89c | Control stays weak | unstimulated-region bridges stay WEAK (mean < mid) throughout |
| T89d | Bimodal | strengths cluster near low OR high, not uniform middle |

## Time budget

Realistic: 8 min wall. Ceiling: 20 min.

## Not claimed

- Not recall (no read-out). The latched state is the memory substrate.
- Content-addressability (different stimulus → different stable pattern)
  is the follow-up once the latch is shown.
