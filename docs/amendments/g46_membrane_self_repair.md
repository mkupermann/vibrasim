# G46 — Membrane self-repair: does a wounded membrane heal back to closure?

Pre-registered: 2026-06-02 (BEFORE the run). G44 showed FUNCTIONAL recovery (the interior
returns to set-point after a chemical perturbation). G46 tests the STRUCTURAL analog: wound the
membrane (remove a contiguous cap of shell atoms) and ask whether the rich substrate heals it —
new atoms forming and bridging into the gap restore the closed shell — vs a no-regeneration
control where the wound persists.

## Method
G30 membrane forms (largest bridged component → centre C, radius R, pre-wound size N0). Wound:
kill all component atoms in a polar cap ((x − Cx) > 0.3R), plus their bridges (~25–35% of the
shell). Then run a REPAIR window. Arms:
- **repair** (lambda_gen = 0.001, default): the substrate keeps forming free vibrations → atoms.
- **control** (lambda_gen = 0): no new vibrations, so no new atoms can heal the wound.
Track the largest bridged component size through the repair window. Seeds 42 & 7.

## Bars (locked pre-run)
| ID | Criterion | Bar |
|----|-----------|-----|
| G46a | Membrane forms | pre-wound component N0 ≥ 50 (both seeds) |
| G46b | Wound lands | immediately post-wound size ≤ 0.7 × N0 |
| G46c | Self-repair (regeneration on) | recovered size ≥ 0.9 × N0 by end of the repair window |
| G46d | Repair needs regeneration (control fails) | control (lambda_gen=0): recovered size ≤ 0.75 × N0 (wound persists) |

PASS = G46a–d → the membrane actively SELF-REPAIRS: a wounded shell heals back to closure via
ongoing substrate formation, and does not heal without it. A striking cell-precursor property
(structural homeostasis). NULL: if G46c fails the wound does not heal (the membrane is static,
not self-maintaining); if G46d also "heals" the recovery is a measurement artifact (component
re-counts existing atoms, not new growth). Honest either way. No post-hoc threshold tuning.

## RESULT (2026-06-02): NULL — the membrane is persistent but STATIC (no self-repair)

| seed | N0 | post-wound | REPAIR recovered | CONTROL recovered |
|------|----|-----------|------------------|-------------------|
| 42 | 112 | 24 (0.21) | 24 (0.21) | 24 (0.21) |
| 7 | 110 | 33 (0.30) | 33 (0.30) | 33 (0.30) |

G46a ✓, G46b ✓ (wound landed — harder than designed: killing the cap + its bridges fragmented
the remainder, dropping the largest component to 0.21–0.30 N0), G46c ✗ (recovered = post,
no healing), G46d ✓. **Verdict: NULL — the membrane does NOT self-repair.**

Recovered ≡ post-wound ≡ control, exactly, both seeds: the wounded shell stays open whether or
not the substrate keeps forming atoms. New ambient atoms do not preferentially bridge into the
gap or re-connect the fragments.

**Honest boundary (a real difference from living cells).** `fusion_bond_block` confers
PERSISTENCE (committed valence → bonded atoms don't break) — but that same commitment means
they don't readily form NEW bonds to bridge a wound, and there is no mechanism targeting new
atoms to the damage site. So the membrane is persistent and FUNCTIONAL but STATIC: it
maintains and regulates, it does not self-renew. (The no-heal conclusion is robust to the
oversized wound, since recovered ≡ post ≡ control regardless of wound size.)

## Proto-cell thread complete (G30→G46) — capabilities AND boundaries
**Has:** forms (G30) · selective permeability (G32) · maintained interior gradient (G43) ·
active regulation to set-point (G44) · hosts an interior chemistry (G45b).
**Lacks:** channel-gated interior synthesis (G45c) · structural self-repair (G46).
A persistent, self-regulating but NON-self-renewing membrane compartment — a genuine
cell precursor, honestly bounded. Consolidated in docs/amendments/PROTOCELL_SUMMARY.md.
