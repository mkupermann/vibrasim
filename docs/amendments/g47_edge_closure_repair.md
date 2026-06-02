# G47 — Self-repair with edge-closure: do free-valence edges re-close a wound?

Pre-registered: 2026-06-02 (BEFORE the run). G46 found the membrane does not self-repair —
recovered ≡ post-wound ≡ control. Diagnosed cause: nothing targets new bonding to the wound,
and committed valence (fusion_bond_block) prevents existing atoms forming new bonds. But the
substrate HAS a wound-targeting mechanism that G46 left off: `edge_closure_k` — "edge atoms
(free valence) attract each other, curling sheets toward closed shells." After a wound, the
atoms around the hole have freed valence (their bridges were cut), so edge-closure should pull
them together and re-close the gap. G47 tests this specific fix.

## Method
G46 wound protocol (form membrane → kill a polar cap of shell atoms + their bridges →
repair window, regeneration ON). Two arms, both with regeneration:
- **repair**: `edge_closure_k = 1.0` (wound edges attract → re-close).
- **control**: `edge_closure_k = 0.0` (G46 condition).
Track the largest bridged component through the repair window. Seeds 42 & 7.

## Bars (locked pre-run)
| ID | Criterion | Bar |
|----|-----------|-----|
| G47a | Membrane forms | pre-wound N0 ≥ 50 (both seeds) |
| G47b | Wound lands | post-wound size ≤ 0.7 × N0 |
| G47c | Meaningful self-repair | recovered ≥ post + 0.3·(N0 − post) — heals ≥ 30% of the damage (both seeds) |
| G47d | Attributable to edge-closure | recovered(edge-closure ON) ≥ 1.3 × recovered(control) (both seeds) |

PASS = G47a–d → edge-closure drives genuine membrane self-repair (wound edges re-close,
attributable to the mechanism): the proto-cell becomes self-renewing, completing the structural
ladder. NULL: if G47c fails the wound still does not heal (edge-closure does not re-close at
this scale); if G47d fails healing is not edge-closure's doing. Honest either way. No post-hoc
threshold tuning.

## RESULT (2026-06-02): NULL — no healing; persistence and self-repair are in TENSION

| seed | N0 | post | edge-ON recovered (peak) | healed-of-damage | control recovered |
|------|----|------|--------------------------|------------------|-------------------|
| 42 | 112 | 24 | 24 (peak 24) | 0.00 | 24 |
| 7 | 110 | 33 | 33 (peak 33) | 0.00 | 33 |

G47c ✗, G47d ✗ → **NULL.** With edge-closure ON the component NEVER grew (peak ≡ post), same as
control. Edge-closure does not re-close the wound.

**Mechanistic explanation — persistence ⊥ self-repair.** The same `fusion_bond_block` valence
commitment that makes the membrane PERSIST (bonded atoms resist breaking → longevity, G30/G43)
is exactly what prevents HEALING: committed atoms cannot form the NEW bonds a wound requires,
so edge-closure (which only adds an attractive force) has no free valence to bond with. The
substrate cannot have both longevity and self-repair through this mechanism — a genuine
trade-off, not a tunable.

**Honest caveat on the wound.** Killing cap atoms + ALL their bridges over-fragments the
remainder (largest component → 24/33, not a clean ~73-atom hole). But the conclusion is robust
to wound shape: zero regrowth (peak ≡ post) regardless — the persistent membrane simply does
not add atoms to heal.

**Testable prediction (G48):** relax the valence commitment (lower fusion_bond_block) → the
membrane should HEAL (free valence available for new wound bonds) but LOSE persistence (atoms
turn over). If confirmed, the persistence⊥repair trade-off is established as the mechanism.
