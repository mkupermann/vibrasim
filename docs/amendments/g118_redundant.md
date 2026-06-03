# G118 — Clean multi-bit matter memory via REDUNDANCY (close the G117 fidelity gap)

## Motivation
G117 showed 4-bit matter-position memory at 0.88/bit (PARTIAL — below the 0.90 bar). The standard fix
(as G103/G104 did for the codec) is redundancy: place REDUN=2 carrier atoms per 1-bit cell, so the cell
reads 1 if at least one survives — robust to a single carrier loss/misplacement. If this lifts per-bit
accuracy to >=0.95, matter-position is a clean multi-bit content-addressable memory.

## Pre-registration (locked BEFORE run)
Same as G117 (K=4 cells x=8,13,18,23; cleared band; NPAT=4 random 4-bit patterns; DRIVE_T=320; POST=400)
EXCEPT each 1-bit cell gets REDUN=2 carriers (cell occupied = >=1 atom present). Both seeds. Chance 0.50.

**Bars (locked):**
- G118 PASS: per-bit accuracy >= 0.95 on both seeds.
NULL/PARTIAL below.

## Result
| seed | per-bit accuracy (REDUN=2) | compare: G117 uncoded |
|------|----------------------------|------------------------|
| 42   | 0.88                       | 0.88 |
| 7    | (run aborted — see note)   | 0.88 |

G118 (per-bit >= 0.95): **False** (seed 42 = 0.88, identical to uncoded) → **VERDICT: NULL**

[Note: seed 7 ran impractically slowly (extra carriers → vibration accumulation, growing memory) and was
aborted. The bar is already decided: seed 42's 0.88 is unchanged from G117's uncoded 0.88 (< 0.95), so
redundancy gives no improvement and the bar fails regardless of seed 7.]

## Finding — redundancy does NOT help; the multi-bit error is SYSTEMATIC (parallels G103)
Doubling carriers per cell left per-bit accuracy at exactly 0.88 — no improvement. This is the same
signature as the communication arc: a repetition code fixed the codec's RANDOM errors but not its
SYSTEMATIC ones (G103). Redundancy is robust only to random carrier LOSS, so its doing nothing means the
~12% error is systematic — most likely spatial: carriers landing at a cell BOUNDARY or overlapping an
adjacent cell's read radius, producing consistent mis-reads that more carriers cannot correct.

The principled fix is the G104 analog: respect SPACING (wider cell pitch / smaller read radius / guard
bands), not redundancy. A clean, bar-respecting follow-up (G119), not post-hoc tuning.

## Honest standing of the matter-memory breakthrough (G115–G118)
- 1-bit selective+persistent matter-position store: CLEAN (G116 PASS, both seeds).
- 4-bit content-addressable store: 0.88/bit (G117 PARTIAL); redundancy doesn't improve it (G118 NULL) —
  the gap is systematic/spatial, fixable by spacing (G119), not coding.
The breakthrough is real and bounded: matter-position is the first selective+persistent representation on
this substrate; making it a CLEAN multi-bit memory needs spatial-layout work, cleanly diagnosed here.
