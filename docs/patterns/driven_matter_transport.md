# Pattern — Driven-matter transport (slow transmission over distance)

## What it is
Free excitations in the substrate do not travel (vibrations are diffusive — injected velocity is not
conserved, G109; charge decays along bridges, G106). But a BOUND atom does: if its velocity is
re-asserted every tick (a sustained drive), it moves coherently in that direction at ~3% of nominal speed
(mass-scaled; ~0.10 units/tick for k_vel=6), carrying its transverse coordinate (a symbol) intact. This is
the ONLY transport mode the bare substrate offers — slow, but real (G112: atoms traverse >20 units alive,
y-drift <0.4, both seeds).

## When to use
Any task that must move information across DISTANCE in the substrate (as opposed to the co-located codec,
docs/patterns/parallel_spatial_channel.md, which reads at the injection site). Use driven matter; do NOT
expect free vibrations or charge to carry a signal across the box.

## How (recipe)
1. Settle a lattice; `lambda_gen=0`.
2. Pick the atom(s) to send (e.g. the leftmost level>=4 atoms). The transverse coordinate (y) IS the
   symbol; keep channels >= the G97 crosstalk-free pitch (~3) apart.
3. EACH tick, re-assert the drive: `world.k_vel[idx, 0] = VX` BEFORE `tick(...)` — velocity is not
   conserved, so a one-shot impulse decays (G110); only continuous drive sustains motion.
4. Read arrival when `k_pos[idx,0]` crosses the far threshold; the atom's y is the decoded symbol.
   Budget ~200 ticks per ~20 units (mass-scaled speed).

## Evidence
- G110/G111: an atom driven at k_vel=6 advances a steady ~0.10/tick; NOT bond-restrained (cutting its
  bridges changes nothing); velocity decays without re-drive.
- G112: 8/8 driven atoms (2 seeds) reached x>20 alive (~tick 199) with y preserved to <0.4.

## Caveats / honesty
- SLOW: ~30x slower than nominal velocity. A transmission line on this is low-bandwidth.
- Beware periodic wrap when measuring traversal — flag the first far-threshold crossing, not the final
  wrapped position (G112 atoms continued past the box edge and wrapped).
- This mechanism was found only AFTER retracting three wrong claims ("condenses into an atom" G107;
  "overdamped, nothing travels" G110; "transport closed"). Direct tracing (G109–G112), not inference,
  established it — a reminder to MEASURE the trajectory rather than reason about the mechanism.
