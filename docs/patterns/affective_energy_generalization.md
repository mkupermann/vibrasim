# Pattern — Affective energy generalization (learned valence over feature-clouds)

**Surfaced:** JEP-425→437 (2026-06-05). **Status:** built, durable, in the live conversational store.

## The mechanism
Give the substrate an affective "energy" (bright +1 / dark −1) per concept, and make it GENERALIZE
to concepts it was never told about — using only established methods (VSA bundles + a reservoir
readout), no transformer.

1. **Energy cloud = feature bundle.** A concept's representation for affect is the normalized
   superposition of its property-value hypervectors (`SubstrateMemory.entity_cloud`). Concepts with
   similar properties get similar clouds, so affect transfers across them.
2. **Learn online.** Each taught valence calls `learn_valence(entity, v)`, which (a) stores the exact
   value for direct recall and (b) feeds `(entity_cloud, v)` to a `ValenceReservoirLearner` — random
   nonlinear features φ(x)=tanh(Rx+b) + an online recursive-least-squares readout (no backprop).
3. **Predict the unseen.** `predict_valence(entity)` returns the taught value if known, else the
   reservoir's generalized prediction from the entity's cloud.

## Why it works (and its honest boundary)
- The reservoir's random features make low-order AND balanced higher-order (parity-like) affect rules
  learnable from the cloud (JEP-433: balanced parity over unseen real clouds at 0.88–0.91; raw-linear
  at chance).
- **Boundary:** low-order affect over VSA clouds is already *linearly* readable (feature presence is a
  linear projection); the reservoir's non-linearity is only needed for genuinely balanced
  higher-structure rules. And the high-order residual (rules needing many interacting features) still
  costs features that grow with interaction order — the open "principled non-linear feature discovery"
  problem (JEP-429), unsolved here.

## Wiring (where it lives)
- `world/substrate_memory.py` — `entity_cloud`, `learn_valence`, `predict_valence`; `self.energy`
  carried through `consolidate_closure`/`compact` (only when D unchanged) and persisted in
  `save`/`load` (store readout `w`,`P`; re-seed projection `R`,`b` from `energy_seed`).
- `world/conversation.py` — affective-word tagging calls `learn_valence`, so the model trains as the
  teacher talks.
- `world/brain_query.py` — `"what is the energy of X?"` answers untaught concepts via the prediction,
  honestly tagged `(generalized)` vs a taught value.

## Reuse
Any time the substrate must assign a graded scalar (affect, salience, reward-prior, confidence) to
NOVEL items from their features, this is the shape: bundle the item's features into a cloud, train a
reservoir+RLS readout online from labelled examples, predict the rest. Established (VSA/HRR —
Plate/Kanerva; reservoir/ELM — Rahimi-Recht/Huang; RLS); the value is the substrate-native assembly
and durable integration, not the methods. Never dress it as novel.
