# G116 — SELECTIVE + persistent memory via matter position? (test on the central deadlock)

## Motivation
G115 showed matter POSITION persists (a written position holds, identity stable). That cracks the
PERSISTENCE horn. G116 tests the SELECTIVITY horn that defeated every activity-based store (write=leak):
in a cleared band, WRITE cell A by driving a carrier atom there and leave cell B empty; after a long POST,
A should be occupied, B empty, and a no-write CONTROL should leave A empty too. Localized matter should
give selectivity for free (an atom at A cannot populate B), exactly what bridge/firing/charge stores
never could.

## Pre-registration (locked BEFORE run)
Settle; lambda_gen=0. Maintain a cleared band (|y-15|<4): each tick clear background atoms in the band
EXCEPT the tracked carriers. WRITE arm: drive 4 carriers to cell A (x=15, stop on arrival), release,
POST=1500 ticks. CONTROL arm: identical but NO carriers driven. Cells are 2.5-radius boxes at A(x=15) and
B(x=22), row y=15.

**Bars (locked):**
- G116a: WRITE cell A occupied (>=1 atom) after POST, both seeds.
- G116b: WRITE cell B empty (0 atoms) after POST, both seeds (no spread/cross-talk).
- G116c: CONTROL cell A empty (0 atoms) after POST, both seeds (occupancy is caused by the write).
PASS = G116a AND G116b AND G116c → SELECTIVE + PERSISTENT store via matter position, the first on this
substrate. PARTIAL = A written + control-clean but B contaminated. NULL otherwise.

## Result
_(pending run)_
