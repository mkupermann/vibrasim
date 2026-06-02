# G40 — Modular independence: two engineered port compartments, no cross-talk

Pre-registered: 2026-06-02 (BEFORE the run). PIVOT from the recall thread (closed as a
robust negative, G39). The one robustly-working new capability is the engineered specular
port wall (firing containment 175–330× every seed). This BET uses it constructively: build
TWO engineered compartments in one substrate and show each fires ONLY in response to its
own stimulus, with no cross-talk — the CONCEPT §4.8 modular-port building block. This needs
only ACTIVITY containment (which the wall robustly delivers), not selective memory (which
the plasticity layer cannot support).

## Method
BET-099 substrate (box 30³, neuron_dynamics ON). Two compartments A (x=7.5) and B (x=22.5),
each radius 6, `compartment_mode='mirror'`, raised at STIM start. Inject a localized stimulus
into ONE compartment for the STIM window; tally firing in the A-core and B-core (|x−cx|<3).
Arms:
- **A-wall**: stim A, walls on.  - **B-wall**: stim B, walls on.  - **A-nowall**: stim A, walls off (cross-talk control).

## Bars (locked pre-run)
| ID | Criterion | Bar |
|----|-----------|-----|
| G40a | A responds to its own stim, isolated | A-wall: A_fire / B_fire ≥ 10× |
| G40b | B responds to its own stim, isolated | B-wall: B_fire / A_fire ≥ 10× |
| G40c | No-wall control shows cross-talk | A-nowall: A_fire / B_fire < 3× (emissions leak to B) |
| G40d | Structure survives the walls | A-wall: both A-core and B-core retain ≥ 3 atoms through STIM |

PASS = G40a–d → two engineered compartments are modularly INDEPENDENT (each driven only by
its own input, no cross-talk), and the wall is what creates the independence (no-wall leaks).
A positive building block for modular substrate computation per CONCEPT §4.8. NULL: if G40a/b
fail the wall does not isolate activity at two sites simultaneously; if G40c passes (no
cross-talk even without walls) the regions were already independent (walls unnecessary at
this separation). Either reported honestly. No post-hoc threshold tuning.

## RESULT (2026-06-02): NULL — the containment wall is a ONE-WAY valve; it makes cross-talk worse

| arm | A_fire | B_fire | ratio | A/B atoms (min) |
|-----|--------|--------|-------|------------------|
| A-wall | 205 | 62 | A/B = 3.3 | 21 / 22 |
| B-wall | 86 | 204 | B/A = 2.4 | 23 / 12 |
| A-nowall | 171 | 30 | A/B = **5.7** | 13 / 6 |

G40a ✗ (3.3 < 10), G40b ✗ (2.4 < 10), G40c ✗ (no-wall 5.7 ≥ 3), G40d ✓. **Verdict: NULL.**

**The decisive surprise:** walls made cross-talk WORSE, not better — with A stimulated, B
fired MORE with walls (62) than without (30); the no-wall ratio (5.7) beats the walled ratio
(3.3). **Diagnosis:** the G33 containment wall reflects only OUTBOUND vibrations (keeps a
region's own emissions in). When A's leaked emissions ENTER B (moving inward toward B's
centre — not an outbound crossing, so not reflected), B's wall then TRAPS them inside B,
where they drive extra B firing. The wall is a **one-way valve**: correct for single-region
containment (G33–G39, 259–330×), wrong for multi-compartment isolation.

**Fix (G41):** a TWO-WAY sealed boundary — reflect inbound-from-outside AND outbound-from
-inside at each compartment surface, so foreign emissions bounce OFF (cannot enter) and own
emissions stay in. Add `compartment_mode='seal'` and re-test the same bars. This is a
specific, principled correction of the identified defect, not a tuning.
