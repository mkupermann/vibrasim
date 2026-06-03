# G94 — Localized maintenance: does feeding the engram restore persistence while control stays blank?

## Pre-registration (locked BEFORE run)
G93 proved persistence is blocked by ATOM EROSION: in the quiet substrate the engram's level>=4 atoms
lose ~74% of members by horizon (persist 0.26) and the bridges die with them. The implied fix is
SPATIALLY-SELECTIVE QUIET: keep the control region culled (blank) but feed the stim region a minimal
maintenance flux so its atoms survive. This is the proto-cell-membrane function (local flux retention)
applied to the memory engram.

Protocol: standard quiet+disconnected+refractory+consolidation, n=6 write. In POST, every tick cull
free vibrations on the CONTROL side (x>15) and, in the MAINT arm only, inject a minimal n=2
maintenance flux at the stim centre. Two arms:
- MAINT  : POST maintenance injection ON  (test the fix)
- NOMAINT: POST maintenance injection OFF (baseline; engram must still die → maintenance is the cause)

**Bars (locked):**
- G94a maintenance restores engram : MAINT atom_persist >= 0.6 AND bridge_persist >= 0.5 (both seeds)
- G94b control stays blank          : MAINT control strong-bridge persist <= 1 (both seeds) — negative control MUST hold
- G94c maintenance is the active ingredient: NOMAINT bridge_persist < 0.3 (both seeds) — dies without feeding
PASS = G94a AND G94b AND G94c. Else NULL/PARTIAL.

## Result
_(pending run)_
