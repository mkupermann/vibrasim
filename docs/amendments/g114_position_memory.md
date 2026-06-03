# G114 — Is MATTER POSITION a persistent store? (new angle on the memory deadlock)

## Motivation
The memory programme is a closed negative for ACTIVITY-based stores: every bridge/firing/charge write
spreads and leaks (write=leak), and quieting erodes the engram (maintenance=contamination). The
driven-matter discovery (G110-G113) suggests a different representation: an atom DRIVEN to a location and
then RELEASED should STAY there (G110: undriven velocity decays → the atom halts) and, being localized
matter rather than spreading activity, should not contaminate elsewhere. G114 tests whether matter
POSITION is a persistent store — a representation the activity-based deadlock never had.

## Pre-registration (locked BEFORE run)
Settle; lambda_gen=0. WRITE: drive the 4 leftmost atoms +x for DRIVE_T=220 ticks; record each written x.
RELEASE: set their k_vel=0. POST: run POST_T=3000 ticks with NO drive. Read final position.

**Bars (locked):**
- G114a survival: a majority of written atoms are still alive after the 3000-tick POST (both seeds).
- G114b position held: surviving atoms drift < 2 units from their written x over the POST (both seeds).
PASS = G114a AND G114b → matter-position is a persistent, stable store (a new, non-activity memory
representation). PARTIAL = survive but drift. NULL = written atoms decay.

## Result
_(pending run)_
