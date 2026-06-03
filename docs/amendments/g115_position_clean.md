# G115 — Clean test: is matter POSITION persistent? (short no-wrap drive, k_birth identity)

## Motivation
G114 was invalid (the drive lapped the periodic box; no identity tracking). G115 fixes both: drive a SHORT
distance (~7 units, no wrap), track each atom by its k_birth so slot-reuse cannot corrupt the reading, and
ask the core question — after the drive is released, does the atom HOLD its new position over a long POST?
A yes makes matter-position a persistent, non-activity store (a fresh angle on the memory deadlock).

## Pre-registration (locked BEFORE run)
Settle; lambda_gen=0. Record (index, k_birth, x_start) for the 6 leftmost level>=4 atoms. WRITE: drive +x
for DRIVE_T=70 ticks (~7 units, no wrap); record target_x. RELEASE k_vel=0. POST: 2000 ticks. A reading
is trusted only if k_birth is unchanged (same atom).

**Bars (locked):**
- sanity: the drive moved atoms (mean displacement > 2 units) — else INCONCLUSIVE.
- G115 PASS: for same-atom survivors, |post_x − target_x| < 2 on both seeds (position held).
NULL/PARTIAL if the position is not held (drift) or identity is lost.

## Result
_(pending run)_
