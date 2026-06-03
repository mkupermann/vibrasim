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
_(pending run)_
