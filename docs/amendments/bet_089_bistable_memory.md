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

## RESULT (2026-05-30): latch CONFIRMED, selective memory not at this scale

**The bistable latch works** (the core mechanism). v1 (absolute flux
drive): bridges climbed to the STRONG well (8.0) and STAYED there
through the POST phase after the stimulus stopped — clean hysteresis.
That is memory: a persistent state recording past flux.

But SELECTIVE latching (stimulated region strong, control weak) is not
cleanly achievable at this substrate scale:
- v1: everything latches (absolute drive >> high background density;
  every bridge crosses the barrier). frac_strong=1.0.
- v2 (relative-to-mean drive + low mobility): during STIM nothing
  crosses the barrier (drive ~0.15-0.3/step vs well pull ~0.16 —
  marginal); then late chaotic latching as flux distribution skews.

Failure modes both trace to the same root, shared with BET-087/088:
- Too few bridges (n=1-7) → noisy flux signal.
- Structure still drifts between measurement regions even at thermal 0.3.
- Barrier-crossing balance is fragile against noisy flux on few bridges.

T89a/b: latch confirmed in v1 but indiscriminate. T89c (selective):
not shown. T89d (bimodal): yes — strengths sit at low (1) or high (8),
never the middle. The double-well IS bimodal, as designed.

## Consolidated finding (BET-087, 088, 089)

The learning layer has all three required mechanisms, each verified in
isolation:
1. Stable structure — the membrane shell (BET-086, replicated 5/5).
2. Flux-driven plasticity — conserved redistribution, no saturation.
3. Bistable latch — hysteretic strength, persists after input stops.

What is NOT yet shown: these composing into demonstrable, selective,
content-addressable memory. The blocker is consistent across all three:
the spontaneous substrate produces ~10-25 atoms and a handful of mobile
bridges — too small and too mobile for a clean place-specific memory
read-out. This is a SUBSTRATE-SCALE limit, not a mechanism gap.

## Next direction

Make the substrate produce a LARGER, FIXED structure to host memory:
either many cells, or anchor a formed shell (freeze positions once
closed) so its bridges have stable identities. Then the three verified
mechanisms can be composed and tested. This is the honest next step,
not more parameter tuning.

## Not claimed

- Not recall (no read-out). The latched state is the memory substrate.
- Content-addressability (different stimulus → different stable pattern)
  is the follow-up once the latch is shown.
