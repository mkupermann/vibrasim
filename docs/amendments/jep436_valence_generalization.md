# JEP-436 — Integrate the energy model: the substrate predicts the valence of UNTAUGHT concepts

## Motivation
JEP-433 showed the valence-reservoir generalizes affect over real VSA clouds; JEP-434/435 showed the
useful payoff is *generalization to the unseen*, not recall-disambiguation. JEP-436 wires that into
the live store: `SubstrateMemory` currently returns ONLY taught valence (`self.valence[entity]`),
abstaining on everything else. This BET adds `entity_cloud` / `learn_valence` / `predict_valence`
(world/substrate_memory.py) so the brain predicts the affect of concepts it was NEVER told the
valence of, from their feature-cloud — Michael's energy model made useful inside the real substrate.
Established methods (VSA/HRR + reservoir/ELM + RLS), named — NOT new science; the contribution is the
integration. No transformer.

## Method (`tools/run_jep436_valence_generalization.py`)
- **Entities with feature facts.** 5 "dark" features + 5 "bright" features. Each entity gets K=5
  features stored as real facts via `sm.add_fact(entity, "has", feature)`. Affect rule = MAJORITY:
  dark(−1) if more dark features than bright, else bright(+1). `entity_cloud` (the bundle of an
  entity's feature vectors) is the energy model's input.
- **Teach then predict.** Call `sm.learn_valence(entity, valence)` on 200 TRAIN entities, then call
  `sm.predict_valence` on 100 HELD-OUT entities whose valence was NEVER taught (facts present, novel
  identities + feature combos).
- Compare to a shuffled-valence training control. Seeds 0 and 7.

## Pre-registered PREDICTION + bars (BEFORE the run)
- **J436a (valence generalizes to untaught concepts):** sign(`predict_valence`) on held-out untaught
  entities matches the rule ≥ 0.80, both seeds.
- **J436b (no regression on taught):** `predict_valence` returns the EXACT taught value for taught
  entities (accuracy 1.0), both seeds.
- **J436c (it is the learned rule):** shuffled-valence training → held-out accuracy ≤ 0.60, both seeds.

Predicted PASS: the integrated energy model predicts the affect of untaught concepts from their
feature-cloud (≥0.80), returns taught values exactly, and a shuffled control fails. This makes the
substrate's "what is the energy of X?" answerable for concepts it was never explicitly told about.
NULL if J436a < 0.80 (the feature-cloud does not carry the rule through the real store). Bars locked;
no retuning. No transformer.

## RESULT (2026-06-05): **PASS** (prediction HIT)

| seed | held-out untaught | taught exact | shuffled control |
|------|-------------------|--------------|------------------|
| 0 | 0.980 | 1.000 | 0.480 |
| 7 | 0.990 | 1.000 | 0.490 |

J436a ✓ (≥0.80), J436b ✓ (taught exact 1.0), J436c ✓ (control ≈ chance) → **PASS, both seeds.**

## Verdict: the energy model is now USEFUL inside the live substrate
`SubstrateMemory` gained `entity_cloud` / `learn_valence` / `predict_valence`. The brain now predicts
the affect (+bright / −dark) of concepts it was **never told the valence of** at 0.98–0.99, from the
bundle of their feature facts — while still returning taught values exactly (no regression) and
failing under a shuffled-valence control (it is the learned rule, not an artifact). This realizes
Michael's energy model where it matters: the substrate generalizes affect across its real
distributed representation, not just looking up stored labels. Established methods (VSA/HRR +
reservoir/ELM + RLS), named — NOT new science; the contribution is the integration into the live
store. No transformer.

**Known follow-up:** the learner (`self.energy`) is in-memory; persisting it across save/load (seed +
w + P + n_features, R/b re-seeded) is a small, tracked enhancement so the generalization survives a
reload like taught valence already does.
