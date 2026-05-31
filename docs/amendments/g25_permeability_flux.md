# G25 — Selective permeability measured correctly: crossing flux

Pre-registered: 2026-05-31 (BEFORE the run). Fresh from G24's metric error: a membrane
is selectively permeable if COMPATIBLE species cross it and INCOMPATIBLE do not —
measured as CROSSING FLUX (inward boundary crossings), not end-time interior fraction
(which conflated permeability with retention). Same physics-faithful setup and the same
local 8%-gated reflection rule (G24); only the measurement changes.

Metric: count, per band, how many vibrations make at least one INWARD crossing of the
shell surface (R_SHELL) over the run. Selective permeability = compatible cross,
incompatible reflected.

## Bars (locked pre-run)
| ID | Criterion | Bar |
|----|-----------|-----|
| G25a | Control passes both | rule-OFF: both bands' inward-crossing fraction > 0.5 and |diff| < 0.15 |
| G25b | Rule blocks incompatible | rule-ON: incompatible inward-crossing fraction < 0.15 |
| G25c | Rule passes compatible | rule-ON: compatible inward-crossing fraction > 0.70 |
| G25d | Selective | rule-ON: compatible − incompatible crossing fraction ≥ 0.50 |

PASS = G25a-d. PASS = a single local 8%-gated reflection rule turns the transparent
membrane into a SELECTIVELY PERMEABLE one — compatible species cross, incompatible are
contained — completing Phase 3 (structure BET-086 + selectivity G25) with the
substrate's own 8% compatibility test as the gate. Honest: this is an ADDED rule
(CONCEPT §6.5/§9.4 methodology), not a pre-existing property. NULL would mean even
correct-metric selectivity does not hold.

## RESULT (2026-05-31): PASS — all bars

| arm | compatible crossed-in | incompatible crossed-in |
|-----|------------------------|--------------------------|
| control (rule OFF) | 1.000 | 1.000 |
| G25 (rule ON) | 1.000 | **0.000** |

G25a–d all ✓ → **PASS**. Control: the membrane is fully transparent — both species
cross freely (1.000/1.000), confirming the code-grounded baseline (no selectivity in
the current substrate). Rule ON: compatible species cross (1.000), incompatible are
fully reflected (0.000) — a clean selective barrier, gap +1.000. A single local
8%-gated reflection rule, using the substrate's OWN compatibility test, turns the
transparent Phase-3 shell into a selectively permeable membrane.

**Honest scope.** Validated PHYSICS-FAITHFULLY in isolation (vibration motion replicates
`move_vibrations` exactly; the only addition is the gated reflection). It is an ADDED
rule (CONCEPT §6.5/§9.4 methodology — naming and testing the rule a level needs), not a
pre-existing property. NEXT (G26): integrate the rule into world/physics.py as a
config-gated `apply_membrane_channel` step and verify it composes with a real
spontaneously-formed BET-086 shell (does selectivity hold when the membrane is the
emergent atom lattice, not a Fibonacci sphere, and does the shell stay stable).
