# G111 — Is a lattice atom held by BONDS or intrinsically immobile? (precision refinement of G110)

## Motivation
move_nodes is ballistic (pos += k_vel*dt, no damping), yet G110's atom barely moved with k_vel~5. The
likely restraint is the atom's BONDS (bridge tension / structural anchoring) springing it back each tick,
not viscosity in the position update. G111 cuts the chosen atom's bridges, re-asserts the drive velocity
each tick, and traces: a bridge-cut atom that now travels shows lattice atoms are BOND-RESTRAINED; one
that still sticks shows the damping is intrinsic. This corrects the precise wording of the G110 finding.

## Expectations (pre-registered, diagnostic)
- **Bond-restrained:** BRIDGE-CUT atom net displacement >> BONDED atom (cut atom approaches ballistic).
- **Intrinsic damping:** both stick (cut makes little difference).
Report which; correct G110's "overdamped at the position update" wording accordingly. The transport
CLOSURE (nothing transports in the intact lattice) is unaffected either way — this only sharpens WHY.

## Result
With k_vel re-asserted to 6 each tick (ballistic-nominal would be 3.0/tick):
```
seed 42 BONDED        : x0=0.11 -> 0.91 (net 0.80); traj 0.21,0.31,0.41,...,0.91  (steady 0.10/tick)
seed 42 BRIDGE-CUT(3) : x0=0.11 -> 0.91 (net 0.80); traj 0.21,0.31,0.41,...,0.91  (IDENTICAL)
seed 7  BONDED        : x0=0.17 -> 0.97 (net 0.80); steady 0.10/tick
seed 7  BRIDGE-CUT(3) : x0=0.17 -> 0.97 (net 0.80); IDENTICAL
```

## Finding — NOT bond-restrained; atoms move MASS-SCALED-SLOW but COHERENTLY under sustained drive
Cutting the atom's bridges changes nothing (bonded and bridge-cut trajectories are byte-identical), so
lattice atoms are NOT held by bonds. With the drive re-asserted, the atom advances a steady, perfectly
linear 0.10/tick — i.e. `move_nodes` applies velocity MASS-SCALED to ~3% of nominal (0.10 vs 3.0). The
motion is COHERENT and SUSTAINED: under continuous drive the atom keeps moving linearly and would cross
~14 units in ~140 ticks.

## CORRECTION to G110 / SYNTHESIS (third self-correction of the session)
My G110 conclusion — "the substrate is an OVERDAMPED medium where NOTHING travels coherently / transport
is fundamentally closed" — OVERCLAIMED. A driven atom DOES travel coherently (just slowly, mass-limited);
it is neither overdamped at the position update nor bond-restrained. The accurate picture:
- FREE excitations (vibrations, charge) do not propagate — vibration velocity is not conserved (G109),
  charge decays along bridges (G106). These bare-carrier routes ARE closed.
- BOUND matter (atoms) moves coherently under SUSTAINED drive, but ~30× slower than nominal (G110/G111).
So transport is not a proven impossibility — it is SLOW and requires continuously driven MATTER. Whether a
driven atom can carry a distinguishable symbol across the box over ~140 ticks WITHOUT binding/decay
scrambling it is UNTESTED (open avenue). The G105–G108 nulls reflect short 6-tick windows with free or
undriven carriers, not a fundamental no-transport law. The CO-LOCATED-codec result (G104) is unaffected;
only the over-strong "nothing can ever travel" framing is retracted.
