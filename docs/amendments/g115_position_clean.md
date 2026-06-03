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
All 12 atoms (6 per seed): driven exactly 7.0 units (no wrap), same_atom=True (k_birth identity stable),
and held position over the 2000-tick POST:
```
seed 42 drifts: 0.83, 0.95, 1.03, 0.59, 0.53, 0.47   (all < 2)
seed 7  drifts: 0.52, 0.41, 1.34, 0.07, 0.07, 0.60   (all < 2)
```
sanity (drive moved atoms): True · G115 (position held, both seeds): **True** → **VERDICT: PASS**

## Finding — matter POSITION is a persistent store (the first in the programme)
Every driven atom holds its written position to within ~1 unit over 2000 ticks after the drive is
released, with its identity (k_birth) intact. This is a clean, two-seed positive and the FIRST persistent
store the substrate has yielded. It is fundamentally different from the failed activity-based memory:
- ACTIVITY stores (bridge strength, firing, charge) FAIL — they spread and leak on write
  ("write=leak"), and quieting erodes them ("maintenance=contamination"); persistence and selectivity are
  coupled and both go wrong (G88–G96).
- A POSITION store does not spread (localized matter), does not need sustaining activity (a released atom
  is quasi-stationary, G110/G111), and persists with stable identity (G115).

**Scope / honesty:** G115 demonstrates the PERSISTENCE horn only — a written position holds. It does NOT
yet demonstrate a full content-addressable, SELECTIVE memory (write location A, leave B empty, read back
A≠B after a delay, low cross-talk). That is the natural next test (G116): localized matter should give
selectivity for free (an atom at A does not affect B), which is exactly what the activity stores could
never achieve. If G116 confirms selectivity, matter-position would be the first selective+persistent store
on this substrate — a genuine breakthrough on the memory deadlock via a NEW representation (position, not
activity), enabled by the driven-matter discovery (G110–G113). Claimed cautiously and multi-seed
(G37→G38 discipline): persistence is solid; selectivity is pre-registered but unproven.
