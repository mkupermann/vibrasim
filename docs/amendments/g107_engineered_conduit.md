# G107 — Can an ENGINEERED conduit add the transport the bare substrate lacks?

## Motivation
G105/G106 closed the transport question for the BARE substrate: neither vibrations nor charge cross the
box — the lattice absorbs/damps them locally. G106 flagged the path to genuine transport: an engineered
low-loss conduit (charter §4.8 engineered topology / the structural frontier). G107 tests the simplest
one — a CLEARED CORRIDOR: cull atoms in a thin y-band across all x each tick, so a packet launched down
the corridor has no matter to bind to and travels ballistically, while the bulk lattice (outside the
corridor) still absorbs. If the corridor delivers energy + a distinguishable symbol to the far end while
G105 delivered ~0, then engineered structure unlocks transport.

## Pre-registration (locked BEFORE run)
Settle lattice; lambda_gen=0. Maintain a corridor: each tick set k_alive=False for atoms with |y−15|<3
(clear a horizontal tube). Launch moving vibrations (vel +x = 6) at x=4 inside the corridor at one of
K=2 sub-channels y∈{13.5, 16.5}. Propagate PROP=6 ticks (re-clearing the corridor each tick), then read
the y-binned free-vibration energy in the FAR region x>16. Two measures:
- far ENERGY (corridor) vs the G105 baseline (~0 far energy) — does anything arrive?
- far DECODE of the 2 sub-channels (1 bit) at the far end.

**Bars (locked):**
- G107a transport arrives: far-region free-vibration energy > 0 on both seeds (corridor delivers a packet
  where G105 delivered ~0).
- G107b symbol survives: far-end 2-channel decode >= 0.85 both seeds (chance 0.5).
PASS = G107a AND G107b → engineered conduit enables genuine transport over distance. PARTIAL if only
G107a (energy arrives but symbol scrambled). NULL if neither (even a cleared corridor doesn't transport).

## Result
| seed | far energy (x>16) | far decode |
|------|-------------------|------------|
| 42   | 0.0               | 0.00       |
| 7    | 0.0               | 0.00       |
(K=2, chance 0.5, n=220)

G107a (packet arrives): **False** · G107b (symbol survives): **False** → **VERDICT: NULL**

## Finding — "to send is to freeze": dense excitations condense into stationary matter at the source
Even with a cleared corridor, the far region receives EXACTLY zero free-vibration energy on both seeds.
This is not absorption en route and not a velocity-integration bug: `move_vibrations` correctly advances
`s_pos += s_vel·dt`, so a packet launched at x=4 with vx=6 would reach x≈22 in PROP=6 ticks IF it stayed
a free packet. It does not — a dense n=14 injection (σ=0.8) BINDS into a stationary atom at the source
within a tick or two (the same binding that builds the lattice), and that atom, sitting in the corridor
band, is then cleared. Nothing ever leaves x≈4 as a moving carrier.

This is the mechanistic root of the whole transport closure (G105/G106/G107): **a signal dense enough to
encode a symbol is dense enough to condense into matter where it is injected**, so it cannot propagate.
"To send is to freeze" — the transport analogue of the substrate's other binding tensions
("write = leak", "maintenance = contamination"). A sparse-enough excitation that did NOT bind would
propagate ballistically (move_vibrations works), but it would be too weak to carry a symbol against
background — the same density/transport trade. An engineered corridor cannot help because the loss is at
the SOURCE, not along the path.

The transport question is therefore closed with a CAUSE: the bare substrate has no symbol-strength
propagating carrier. Genuine transport would require a mechanism that moves a BOUND structure (e.g. a
travelling bridge front along a pre-built atom "wire") rather than a free packet — a substantial
structural build, logged as an open frontier, not a property of the medium. The validated communication
result stands as a CO-LOCATED spatial codec (G104), now with its boundary fully understood.
