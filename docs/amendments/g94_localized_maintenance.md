# G94 — Localized maintenance: does feeding the engram restore persistence while control stays blank?

## Pre-registration (locked BEFORE run)
G93 proved persistence is blocked by ATOM EROSION: in the quiet substrate the engram's level>=4 atoms
lose ~74% of members by horizon (persist 0.26) and the bridges die with them. The implied fix is
SPATIALLY-SELECTIVE QUIET: keep the control region culled (blank) but feed the stim region a minimal
maintenance flux so its atoms survive. This is the proto-cell-membrane function (local flux retention)
applied to the memory engram.

Protocol: standard quiet+disconnected+refractory+consolidation, n=6 write. In POST, every tick cull
ALL free vibrations (substrate quiet everywhere — control blank by construction) and, in the MAINT
arm only, inject a minimal n=2 maintenance pulse at the stim centre AFTER the cull (a tiny bounded
local flux while the rest stays silent). [Method note: an initial control-side-only cull caused
unbounded stim-side vibration accumulation and was replaced, BEFORE any result was read, with
cull-all-then-pulse; the bars below are unchanged.] Two arms:
- MAINT  : POST maintenance injection ON  (test the fix)
- NOMAINT: POST maintenance injection OFF (baseline; engram must still die → maintenance is the cause)

**Bars (locked):**
- G94a maintenance restores engram : MAINT atom_persist >= 0.6 AND bridge_persist >= 0.5 (both seeds)
- G94b control stays blank          : MAINT control strong-bridge persist <= 1 (both seeds) — negative control MUST hold
- G94c maintenance is the active ingredient: NOMAINT bridge_persist < 0.3 (both seeds) — dies without feeding
PASS = G94a AND G94b AND G94c. Else NULL/PARTIAL.

## Result
| arm     | seed | atoms→persist | atom_persist | bridges→persist | bridge_persist | ctrl_persist |
|---------|------|---------------|--------------|-----------------|----------------|--------------|
| MAINT   | 42   | 23 → 7        | 0.30         | 6 → 3           | 0.50           | 4            |
| MAINT   | 7    | 27 → 5        | 0.19         | 10 → 0          | 0.00           | 18           |
| NOMAINT | 42   | 23 → 6        | 0.26         | 6 → 0           | 0.00           | 2            |
| NOMAINT | 7    | 27 → 7        | 0.26         | 10 → 2          | 0.20           | 9            |

G94a False · G94b False · G94c True → **VERDICT: NULL**

## Finding — maintenance does not give selective persistent memory; the deeper blocker is exposed
1. **Atom erosion is not rescued by a weak local pulse.** atom_persist stays 0.19–0.30 in every arm,
   MAINT included. The n=2 maintenance pulse is too small to sustain the level>=4 atom population, and
   raising it would be post-hoc tuning (forbidden) — and would worsen point 3.
2. **Maintenance helps bridges only erratically.** seed 42 bridge_persist 0.50 (MAINT) vs 0.00
   (NOMAINT) — a real effect; but seed 7 is 0.00 (MAINT) vs 0.20 (NOMAINT) — maintenance made it
   WORSE. Not a reproducible rescue (fails the two-seed gate, G37→G38 discipline).
3. **The real blocker: consolidation is NON-SELECTIVE.** Control carries 2–18 persistent strong
   bridges in EVERY arm, including NOMAINT (ctrl 2, 9) with no feeding at all. Bridges that consolidate
   in the control region during the STIM self-ignition cascade get re-pinned to `high` every tick and
   self-sustain via `apply_bridge_atom_propagation` (strong bridge → charge → atom firing → survival),
   independent of free-vibration flux. The maintenance pulse INCREASES this (seed 7 ctrl 18 MAINT vs 9
   NOMAINT) — more flux, more cascade, more control bridges.

This is the "write = broadcast = leak" tension at the persistence layer: **the mechanism that makes a
write persistent (consolidation lock + bridge-atom self-propagation) makes the contamination
persistent too.** Consolidation does not distinguish engram bridges from cascade-seeded control
bridges. Atom erosion (G93) is real but secondary; the dominant barrier is that persistence in this
substrate is indiscriminate. This re-closes the memory deadlock (reopened at G88) at a sharper level:
selective WRITE is achievable, but PERSISTENCE and SELECTIVITY are coupled through consolidation and
cannot be separated by maintenance, refractory, disconnection, or quieting.

Next direction (G95): stop trying to make non-selective bridge-persistence selective. Store the bit in
a STRUCTURE that is intrinsically stable and intrinsically local — the presence/absence of a closed
membrane compartment (proto-cell thread, G30–G46, membranes shown stable) — so persistence comes from
structural closure and selectivity from spatial nucleation, not from a graded synaptic latch.
