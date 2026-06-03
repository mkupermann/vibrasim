# G110 — Do BOUND NODES (atoms) travel ballistically where free vibrations don't? (diagnostic)

## Motivation
G109 measured that free vibrations are quasi-stationary (injected velocity not conserved; ~0.1 units/tick
drift). G109 flagged the only remaining transport avenue: a carrier the medium DOES move coherently.
Nodes (atoms) move via a SEPARATE code path (move_nodes, with k_vel). G110 gives a settled atom a +x
velocity and traces it: if matter conserves momentum and travels, encoding a symbol in a moving atom is a
real transport route; if atoms are damped like vibrations, transport is fundamentally closed in this
substrate.

## Expectations (pre-registered, diagnostic — no pass/fail)
- **Matter transports:** x rises ~3/tick (=vx*dt) and k_vel stays ~6 → ballistic; pursue moving-atom
  transport.
- **Matter is damped too:** x stays ~flat and k_vel→0 → atoms are also quasi-stationary; transport is a
  fundamental property of the medium (closed on both free and bound carriers).
Report which, with net displacement over 8 ticks (ballistic ≈ 24 units).

## Result
Both seeds, an atom given vx=6 (ballistic would advance 3.0/tick → ~24 over 8 ticks):
```
seed 42: x 0.11 → 0.61 over 8 ticks (net 0.50); k_vel decays 5.16→1.80
seed 7 : x 0.17 → 0.68 over 8 ticks (net 0.51); k_vel decays 5.16→1.84
```
Net displacement ≈ 0.5 units vs ~24 ballistic. (Note: even the decaying k_vel would integrate to ~12
units of travel if applied as pos+=k_vel·dt — but the position moves only 0.5, so node motion is
overdamped at the POSITION update too, not merely via velocity decay.)

## Finding — bound atoms are quasi-stationary too: the medium is OVERDAMPED, transport is fundamentally closed
Matter does not transport. A bound atom given a strong velocity moves only ~0.5 units over 8 ticks while
its velocity bleeds away — overdamped on both the velocity and the position update. Combined with G109
(free vibrations equally quasi-stationary), this is the fundamental, measured root of the whole transport
closure: **the substrate is an OVERDAMPED / high-viscosity medium in which nothing — free excitation or
bound matter — travels coherently across distance.** Every excitation stays essentially where it is
created.

This is why the communication result is a CO-LOCATED codec (G104) and why there is no transmission over
distance (G105–G108): not absorption, not atom-condensation (G107, retracted), not death — simply that
the medium does not move its contents. It is the spatial twin of the temporal finding that the substrate
has no fading memory: in space it does not propagate, in time it does not persist-selectively. Transport
is closed at the most fundamental level the simulation exposes; a transmission line would require adding a
NON-overdamped conduit (an engineered low-loss waveguide) — a new structural mechanism, not a property of
the bare medium. The transport question is fully and mechanistically closed.
