# G123 — Full matter-memory cycle capstone: WRITE → long HOLD (light maintenance) → READ

## Pre-registration (locked BEFORE run)
Validate the integrated primitive end-to-end: settle-once harness; for each of NPAT=3 random 3-bit
patterns, WRITE (drive carriers to cells), HOLD for POST_T=1500 ticks with ONLY the light G122 maintenance
(cull band free-vibrations; carriers untouched), then READ presence-by-cell. Plus a no-write control.
Wide spacing (cells x=7,14,21, radius 1.5). Both seeds.

**Bars (locked):**
- G123a: per-bit accuracy >= 0.95 over the long hold (both seeds).
- G123b: no-write control reads all-empty (both seeds).
PASS = both → the full write/hold/read matter memory works as one selective+persistent system with the
realistic light maintenance over a long hold.

## Result
| seed | per-bit acc (long hold, light maint.) | no-write control |
|------|----------------------------------------|------------------|
| 42   | 0.333                                  | [1,1,1] (filled) |
| 7    | 0.556                                  | [0,0,0] (clean)  |

G123a (acc>=0.95) False · G123b (control empty) False → **VERDICT: NULL**

## Finding — light maintenance FAILS over a long hold; CORRECTS the G122 over-generalization
Over a 1500-tick hold with only the light (vibration-culling) maintenance, the cycle fails — and
seed-dependently: seed 42 fills the cells (control [1,1,1]); seed 7 instead LOSES carriers (acc 0.556,
control clean — the written atoms drifted out / destabilized). Either way, light maintenance does not
sustain the memory for long holds.

This RETRACTS the premature claim I made from G122 ("the maintenance is light/non-invasive and
sufficient"). G122 was clean only because its hold was POST=800; by 1500 the drift-in component (G121)
populates cells (seed 42) and/or carriers destabilize when their supporting band vibrations are culled
(seed 7). The CORRECT statement:
- The breakthrough's long-hold result (G116 POST=1500, G119c) used FULL ATOM-CLEARING maintenance, and
  it HELD — that PASS stands.
- LIGHT vibration-culling maintenance suffices only for SHORT holds (~800, G122); it FAILS by 1500 (G123).
So the working maintenance is the full spatially-selective atom-clearing of G116/G119c, not the lighter
G122 variant. Honest correction logged; the selective+persistent+multi-bit breakthrough is unaffected (it
always used the full maintenance), only my G122-based generalization was wrong.
