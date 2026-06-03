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
_(pending run)_
