# G122 — Maintenance decomposition: is FORMATION-suppression alone enough? (toward a lighter/static memory)

## Pre-registration (locked BEFORE run)
G121: empty-cell repopulation ~56% drift-in + 44% new formation. G122 tests whether suppressing FORMATION
alone maintains the memory: scaffold-free POST except culling FREE VIBRATIONS in the band each tick (the
formation source), with NO atom clearing. Pattern [1,0,1]; both seeds.

**Bars (locked):**
- G122 PASS: pattern [1,0,1] recovered exactly with formation-suppression-only maintenance, both seeds.
NULL/PARTIAL if cells still fill (drift-in dominates → atom-level clearing or a barrier still needed).

## Result
| seed | readout | target | exact |
|------|---------|--------|-------|
| 42   | [1,0,1] | [1,0,1]| Yes   |
| 7    | [1,0,1] | [1,0,1]| Yes   |

**VERDICT: PASS** — pattern held with formation-suppression-only maintenance, both seeds.

## Finding — the maintenance is LIGHT and NON-INVASIVE (formation suppression, carriers untouched)
Culling free vibrations in the readout band (suppressing NEW atom formation) is SUFFICIENT to keep the
empty cells empty — full atom-level clearing is NOT needed, and the drift-in atoms G121 counted in the
broader band do not actually populate the smaller CELLS. So the G120 "maintained, not static" bound is
real but the maintenance is minimal: keep the readout region free of vibration churn; the written carrier
atoms are NEVER touched.

This sharpens the breakthrough's honest standing. The matter-position memory is:
- WRITE: drive carriers to cells (persists intrinsically, G115).
- HOLD: a light, non-invasive refresh — cull free vibrations in the readout band so no new atoms form
  there (G122). Carriers untouched; empty cells stay empty.
- READ: presence-by-cell (clean multi-bit, G119c).
The refresh is cheap and, crucially, NON-DESTRUCTIVE to the stored bits — the decisive break from the
activity deadlock (where any maintenance contaminated the store). A maintained selective+persistent
multi-bit memory with a minimal, stored-bit-safe refresh is the honest final characterization.
