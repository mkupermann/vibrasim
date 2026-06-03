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
_(pending run)_
