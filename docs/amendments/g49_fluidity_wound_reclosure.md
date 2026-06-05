# G49 — Does reducing positional rigidity enable wound re-closure? (tests G48's corrected diagnosis)

Pre-registered: 2026-06-05 (BEFORE the run). G48 FALSIFIED the persistence⊥commitment trade-off and
**corrected** the diagnosis of why the proto-cell membrane is static (no self-repair, G46/G47): it is
not `fusion_bond_block` (block=0 and block=2 behaved identically — both persist 1.00, both heal 0.00).
The corrected blocker is **positional RIGIDITY** (`curvature_k` + `atom_repulsion_k` fix the shell's
shape so wound edges hold position instead of migrating to re-close) **+ no wound-targeting** (new
ambient atoms form elsewhere, untargeted to the gap).

G49 tests the RIGIDITY half directly and falsifiably: if rigidity is what blocks healing, then
*relaxing* it during the repair window should let the wound edges migrate together and the gap
re-close. If even a fluid membrane does not heal, rigidity is NOT the blocker and the sole cause is
lack of wound-targeting — which the next BET would isolate.

## Method
G46/G47 protocol, identical formation in every arm (G43 `cfg`, block=2, SETTLE=250) so the SAME rigid
membrane exists at t0. Then for the post-formation window, scale rigidity by factor `f`:
`curvature_k *= f`, `atom_repulsion_k *= f`. Two measurements per `f`, seeds 42 & 7:

- **Healing H(f)** — wound (polar cap + its bridges), then REPAIR=250 ticks at scaled rigidity;
  `H = (recovered − post) / (N0 − post)` (fraction of damage re-closed; the G47c metric).
- **Persistence P(f)** — NO wound, PERSIST=250 ticks at scaled rigidity; `P = end_component / N0`
  (does the membrane still stand at this fluidity, or does low rigidity just collapse it?).

Sweep `f ∈ {1.0 (rigid control = G46/G47), 0.5, 0.25, 0.0 (no shape-holding force)}`.

## Bars (locked pre-run)
| ID | Criterion | Bar |
|----|-----------|-----|
| G49a | Membrane forms (sanity) | N0 ≥ 50 (both seeds) |
| G49b | Rigid control reconfirms no-heal | H(f=1.0) < 0.10 (both seeds) |
| G49c | Reduced rigidity HEALS | H(some f<1) ≥ 0.30 (both seeds) |
| G49d | Healing is real re-closure, not collapse | at that same f: P(f) ≥ 0.70 (membrane stands unwounded) AND recovered > post (both seeds) |

## Verdicts (pre-registered, no post-hoc tuning)
- **PASS** (G49a–d): reducing positional rigidity enables genuine wound re-closure → confirms G48's
  corrected "rigidity blocks repair" diagnosis AND demonstrates the first self-repairing proto-cell
  membrane (a fluidity mechanism within substrate primitives). The structural breakthrough G46/G47
  could not reach.
- **PARTIAL** (G49c holds but G49d fails): low-f "heals" but also collapses/reforms when unwounded →
  the regrowth is reformation, not targeted repair; the two cannot be distinguished at this fluidity.
- **NULL** (G49c fails): even a fluid membrane does not heal → rigidity is NOT the blocker. The sole
  remaining cause is **no wound-targeting** (mobile edges still don't find the gap; new atoms form
  elsewhere). Sharpens the diagnosis to a single mechanism for the next BET to isolate. Honest either
  way.

Caveat (carried from G47): the wound over-fragments the remainder (largest component → ~24/33, not a
clean ~73-atom hole). Held constant across all arms so the rigidity contrast is clean; if fluidity
heals even this fragmented wound, the effect is strong. No post-hoc threshold tuning.

## RESULT (2026-06-05): NULL — rigidity is NOT the blocker; the cause is bond-graph solidity + no targeting

| seed | N0 | post | healed @ f=1.0 | healed @ f=0.5 | healed @ f=0.25 | healed @ f=0.0 | P @ f=0.0 |
|------|----|------|---------------|----------------|-----------------|----------------|-----------|
| 42 | 112 | 24 | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 |
| 7 | 110 | 33 | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 |

G49a ✓ (N0 112/110), G49b ✓ (rigid no-heal 0.00 < 0.10), **G49c ✗** (no f<1 heals — all 0.00),
G49d ✗ → **NULL.** A prior independent G49 attempt reached the identical verdict (a✓ b✓ c✗ d✗),
corroborating.

**The decisive observation: at f=0.0 the membrane still persists FULLY (P=1.00).** With curvature_k
and atom_repulsion_k both zeroed — no shape-holding force at all — the formed component neither heals
(0.00) nor collapses (1.00). So:

1. **Persistence is NOT from curvature/repulsion forces** (falsifies G48's correction), and **NOT from
   valence commitment** (G48 already falsified that). It comes from the **bond graph itself**: bonded
   atoms hold their relative positions because the bonds constrain them, immune to both forces (G49)
   and the `fusion_bond_block` setting (G48).
2. **Reducing rigidity does NOT enable healing.** Wound edges still do not migrate to re-close, even
   with zero positional force — because it is the *bonds*, not a force field, that lock their
   positions. Removing the force does not unlock the lattice.

**Triangulated diagnosis across G46→G47→G48→G49 (a chain of falsified hypotheses, each sharpening):**
- G46: membrane does not heal a wound.
- G47: hypothesis = valence commitment blocks new wound bonds; edge-closure force does not fix it → NULL.
- G48: FALSIFIES valence commitment (block 0 ≡ block 2: both persist 1.00, both heal 0.00). Re-attributes
  to curvature/repulsion rigidity + no targeting.
- G49: FALSIFIES curvature/repulsion rigidity (f=0.0 still P=1.00, still heals 0.00). Re-attributes to
  **bond-graph solidity + no wound-targeting.**

**Settled finding (robust to 3 falsified mechanisms): the proto-cell membrane is a covalent SOLID.** Its
persistence is a property of the bond topology — it survives removal of every tunable force and every
valence setting. It cannot self-repair for two reasons now precisely located: (a) bonded atoms are
positionally locked **by their bonds** (not by forces), so wound edges cannot migrate to re-close; and
(b) nothing targets new-atom generation to the wound, so regeneration repopulates elsewhere. Self-repair
would require **bond turnover** (bonds breaking + reforming at the wound to fluidize the edge) or
**spatially-targeted regeneration** — neither is present in the substrate. This is a clean NEGATIVE
boundary for the proto-cell structural thread: the substrate builds a stable container, not a living
self-renewing membrane.

**Testable next (G50):** of the two remaining levers, **bond turnover** is the purely-diagnostic one
(it adds no new aiming mechanism, only lowers existing bond-lifetime knobs `pair_decay_time` /
`triad_decay_time` so the lattice can locally re-flow). Prediction: faster turnover → the membrane
fluidizes and the wound re-closes, but persistence drops (turnover ⇒ the component churns). If
confirmed, **bond rigidity ⊥ self-repair** becomes the established trade-off (the real one G47 reached
for at the wrong level: it is the BOND graph, not valence commitment or forces).
</content>
