# JEP-238 — the relation-INTERACTION matrix through the substrate (part-of × is-a, with leak guard)

Pre-registered 2026-06-05 (BEFORE the run). JEP-232..237 put the engine's relations (is-a, typed, DAG) IN the
substrate. The Understanding Engine's HALLMARK is the relation-INTERACTION matrix — distinct relation types compose
with taxonomy under specific rules (docs/patterns/relation_interactions.md). This BET tests the part-of × is-a UP
interaction THROUGH the substrate: "a heart is part of a dog; a dog is an animal ⟹ a heart is part of an animal",
WITH the leak guard ("a heart is NOT part of a cat" — the whole's siblings don't inherit the part).

## Method (no transformer; composition of two substrate retrievals)
- Two substrate stores (each the JEP-232 key→value attractor net): a PART-OF store (part_code → whole_code) and an
  IS-A store (child_code → parent_code), both read FROM PROSE via the engine.
- Query `part_of_super(part, super)`: (1) retrieve the part's WHOLE `w` from the part-of store; (2) chain `w`'s is-a
  ancestors through the is-a store (JEP-233); (3) return `super ∈ {w} ∪ ancestors`. Forward + single-valued — no
  reverse, no multi-value (clean composition).
- Compare to the engine's symbolic `part_of(part, super)` (which encodes the interaction). Seeds 42 & 7.

## Bars (locked pre-run)
| ID | Criterion | Bar |
|----|-----------|-----|
| J238a | UP interaction holds | substrate says heart part-of animal (and heart part-of mammal) = True, matching symbolic (both seeds) |
| J238b | Leak guard holds | substrate says heart part-of cat = False (the whole's sibling), matching symbolic (both seeds) |
| J238c | Battery match | over a battery of part_of_super queries (positives up the is-a chain + sibling/negatives) substrate vs symbolic ≥ 0.90 (both seeds) |
| J238d | Above an untrained control | untrained nets: battery match ≤ 0.60 (both seeds) |

PASS = J238a–d → the substrate reproduces the engine's part-of × is-a interaction, leak guard included: compositional
cross-relation reasoning runs on the substrate. NULL (honest): J238a fails → the composition desyncs (part-of or
is-a retrieval wrong); J238b fails → the leak guard breaks (substrate over-generalizes the part up-then-down). No
post-hoc threshold tuning.

## Prediction (locked BEFORE run) [predict-calibrate]
🔮 PASS. Both sub-retrievals are 1.00 within capacity (J232/233), and `part_of_super` is forward + single-valued
(a part has one whole; the whole has one is-a chain), so the composition reproduces the symbolic interaction: J238a
True (heart→dog→…→animal), J238b False (cat is not on dog's is-a chain → the leak guard is automatic, the substrate
never visits cat), J238c ≥ 0.90 (~1.00), J238d control fails (~0.50). RISK (in-rung): the is-a ancestor walk must
stop at the root (SIM/energy gate from JEP-235/237) so a top-of-chain spurious retrieval doesn't add a false super;
and the battery must include genuine NEGATIVES (a super NOT on the chain, and a sibling) or J238c is uninformative.
Established (composition of content-addressable retrievals + transitive closure), named; no novelty — the value is
showing the engine's signature INTERACTION reasoning, not just flat facts, runs on the substrate.

## RESULT (2026-06-05): PASS — all 4 bars; the interaction (incl leak guard) runs on the substrate

| seed | UP (heart→animal & mammal) | leak guard (NOT cat/feline) | battery match | control |
|------|----------------------------|-----------------------------|---------------|---------|
| 42 | True | True | 1.00 | 0.33 |
| 7  | True | True | 1.00 | 0.33 |

- **J238a ✓** — composing a part-of retrieval (heart→dog) with the is-a chain (dog→canine→mammal→animal) yields
  `heart part-of animal` AND `heart part-of mammal` = True, matching symbolic.
- **J238b ✓** — the LEAK GUARD is automatic: cat/feline are not on dog's is-a chain, so the substrate never visits
  them → `heart part-of cat` = False. The whole's siblings don't inherit the part — exactly the engine's semantics.
- **J238c ✓** — battery (every concept as a candidate super for 'heart') matches symbolic **1.00**, both seeds.
- **J238d ✓** — untrained control 0.33.

**FINDING:** the engine's HALLMARK — the relation-INTERACTION matrix — runs on the substrate, not just flat facts.
A cross-relation compositional query (part-of × is-a UP) is reproduced by COMPOSING two content-addressable substrate
retrievals (part's whole, then the whole's is-a closure), leak guard included for free (the chain simply never
reaches the sibling). With JEP-232..237 this means the substrate carries the engine's relational MEMORY and performs
its STORAGE, CHAINING, TYPING, DAG closure, AND interaction reasoning — the full relational engine, within the
~20-edge/module capacity. Established (composition of content-addressable retrievals + transitive closure), named;
no novelty — the value is that the engine's signature reasoning, not only its facts, lives in the energy substrate.
Verdict: **PASS** (predict-calibrate HIT — all 4 bars as forecast, incl. the automatic leak guard).
