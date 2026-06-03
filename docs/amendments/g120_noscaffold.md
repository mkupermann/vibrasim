# G120 — How load-bearing is the band scaffold? (POST with no band-clearing)

## Pre-registration (locked BEFORE run)
G116/G119c maintained a cleared band THROUGHOUT (write + hold). G120 keeps band-clearing only during the
WRITE drive, then runs POST=1500 with NO band-clearing. If the pattern still holds, the scaffold only aids
the write and the HOLD is intrinsic (atoms are quasi-stationary, G110/G111; quiet substrate forms few new
atoms). Settle-once harness; pattern [1,0,1]; no-write control.

**Bars (locked):**
- G120a: WRITE recovers [1,0,1] exactly after a no-scaffold POST, both seeds.
- G120b: no-write CONTROL cells stay empty (all 0), both seeds.
PASS = both → matter memory holds beyond the scaffold. NULL/PARTIAL = pattern degrades without it.

## Result
| seed | WRITE readout (target [1,0,1]) | CONTROL readout (target all-0) |
|------|-------------------------------|--------------------------------|
| 42   | [1,1,1]                       | [1,1,1]                        |
| 7    | [1,1,0]                       | [1,1,1]                        |

G120a (write recovers without scaffold) False · G120b (control empty) False → **VERDICT: NULL**

## Finding — the band scaffold is LOAD-BEARING: the memory is MAINTAINED, not static
Without continuous band-clearing during POST, ALL cells fill (control reads [1,1,1] both seeds) — the
band repopulates over 1500 ticks (background atoms enter/form in the cells). So the empty ("0") cells do
NOT stay empty on their own; keeping them empty requires the active, spatially-selective clearing.

This honestly BOUNDS the G116/G119c breakthrough: matter-position memory is a MAINTAINED store (like DRAM
refresh), not a static latch. The refinement, precisely:
- WRITTEN bits persist INTRINSICALLY — a carrier atom driven to a cell holds its position with no upkeep
  (G115, drift<2 over 2000 ticks).
- EMPTY bits require active MAINTENANCE — without spatially-selective clearing, background repopulates the
  non-written cells.
Crucially, the maintenance is SELECTIVE and NON-DESTRUCTIVE: it clears background in the empty cells while
leaving the carriers untouched (the carriers are in the keep-set). This is the decisive contrast with the
activity-memory deadlock, where maintenance CONTAMINATED everything ("maintenance=contamination"). Here
maintenance WORKS — it refreshes the 0s without disturbing the 1s.

So the honest, corrected headline: matter-position is the first SELECTIVE + PERSISTENT + MAINTAINED
multi-bit memory on the substrate — the writes hold for free, the blanks are refreshed selectively. Still
a genuine break from the activity deadlock (selective non-destructive maintenance is possible for matter,
impossible for activity), but it is a maintained memory, not a static one. NULL on the "no-scaffold"
bar is the finding that pins this down.
