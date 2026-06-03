# G112 — Can slow driven MATTER carry a symbol across distance? (resolves the G111 avenue)

## Motivation
G111 showed a bound atom moves coherently under SUSTAINED drive (~0.10 units/tick, mass-scaled, not
bond-restrained) and flagged driven-matter transport as an open, untested avenue. G112 tests it: drive
the leftmost atoms in +x (re-asserting k_vel each tick) for up to 260 ticks and check whether they reach
the far side (x>20) ALIVE with their y (the symbol coordinate) preserved.

## Pre-registration (locked BEFORE run)
Settle; lambda_gen=0. Drive the 4 leftmost level>=4 atoms at k_vel_x=6 (re-asserted each tick) for
MAXT=260 ticks. Record per atom: reached x>20 (and at which tick), alive at end, |y - y_start|.

**Bars (locked):**
- G112a transport occurs: at least one driven atom reaches x>20 ALIVE within 260 ticks (either seed).
- G112b symbol survives: on arrivals, y-drift < 3 (the y coordinate that would encode the symbol is
  preserved through transit).
PASS = G112a AND G112b → slow driven-matter transport is real (restores a slow transmission avenue).
PARTIAL = arrives but y scrambled. NULL = atoms bind/decay/stall before arriving.

## Result
All 8 driven atoms (4 per seed) reached x>20 ALIVE, around tick ~192–199, with y preserved:
```
seed 42: 4/4 arrived (tick 192–199), y-drift 0.18–0.38
seed 7 : 4/4 arrived (tick 195–199), y-drift 0.14–0.30
```
(Note: final reported xf≈4 is the PERIODIC WRAP — at 0.10/tick the atom passes x=20 near tick ~199, then
continues to ~26 units by tick 260 and wraps 30→0→~4. The arrived_tick flag, set when x first exceeds 20,
is the evidence of traversal; the small y-drift confirms the symbol coordinate survived.)

G112a (reached far side alive): **True** · G112b (y/symbol preserved, drift<3): **True** → **VERDICT: PASS**

## Finding — slow driven MATTER DOES transport a symbol across distance
Continuously driven atoms traverse >20 units (≈ tick 199 at 0.10/tick) while staying alive and holding
their y coordinate to within 0.4 units. Since the crosstalk-free y-pitch is ~3 (G97), several y-channels
would remain distinguishable on arrival — so driven matter can carry a multi-symbol code across the box,
just slowly (~200 ticks per ~20 units).

**This is the positive that the honesty corrections uncovered.** Had the programme stopped at the wrong
G110 conclusion ("overdamped medium, nothing travels"), this capability would have been missed. The
corrected, COMPLETE transport picture:
- FREE carriers (vibrations, charge) do NOT transport — diffusive / decaying (G105–G109).
- BOUND matter (driven atoms) DOES transport, coherently and with symbol preserved, at ~3% nominal speed
  (G110–G112).
So the substrate supports BOTH a fast CO-LOCATED codec (G104) AND a slow driven-MATTER transmission line
(G112) — two distinct communication modes, no LLM. The earlier "transport closed" framing is fully
retracted; transport is OPEN via driven matter, bounded by speed, not possibility.
