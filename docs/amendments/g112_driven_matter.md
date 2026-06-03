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
_(pending run)_
