# Pattern: the substrate AS the Understanding Engine's relational memory (JEP-232/233/234)

Michael's recurring question — "where is the substrate in the chain?" — answered for *relational knowledge*. The
Understanding Engine (`world/understanding.py`) keeps its facts in Python dicts + VSA fact-vectors. They can instead
live IN the energy-based substrate (`world.energy.EnergyNet`, a modular Hopfield/contrastive-Hebbian EBM), which
then performs storage, multi-hop inference, AND relation typing on its own dynamics. All three pieces are
ESTABLISHED methods (named as such — no novelty); the value is the demonstrated end-to-end connection + its envelope.

## The construction (single dense module, N=80: KEY=[0:40], VALUE=[40:80])
1. **Codes.** Each concept and each relation type → a fixed random ±1 vector of length 40.
2. **STORE a fact** `(subject, relation, object)` as the bipolar attractor
   `concat( subject_code ⊙ relation_code , object_code )`, where `⊙` is the Hadamard (element-wise ±1) product =
   VSA role-binding (the KEY is unique to the (subject, relation) pair). Train as attractors with `train_epoch`
   (contrastive-Hebbian, local, label-free). For a single relation type, drop the bind: KEY = `subject_code`.
3. **RETRIEVE** `(subject, relation)`: clamp KEY = `subject_code ⊙ relation_code`, `relax()` the VALUE slot, decode
   the settled value to the nearest concept code (argmax dot-product) = the object.
4. **CHAIN (transitive closure)**: re-present the retrieved object as the next KEY and retrieve again. Works with
   the raw settled bits (no clean-up) OR the decoded clean code — identical within capacity.

## What holds (measured, seeds 42 & 7)
- **Store** (J232): child→parent recall **1.00**, content-addressable from a **60% partial** cue, untrained control
  ≈ 1/K. Capacity is **sharp**: perfect to **K≈20 facts/module**, then a **catastrophic Hopfield blackout** at K≈22
  (1.00→0.34→0.04). Capacity ≈ **0.5 facts/value-unit** — *heteroassociative* (the key is fully clamped, only the
  value settles), ~3–4× the 0.14·N autoassociative bound. (Calibration: don't apply the autoassociative bound to a
  fully-cued key — see calibration_lessons error-class 10/11.)
- **Chain** (J233): 2- and 3-hop transitive inference = **1.00**, raw OR cleaned re-clamp; control 0.00. Within
  capacity the value slot sits exactly on the attractor, so the dynamics **self-correct each hop** — no error
  accumulation (that only bites near/above the cliff).
- **Type** (J234): is-a + part-of + causal in one net via the bind; recall 1.00, a wrong-relation query returns the
  right object only ~chance (the bind **discriminates**), every type equally served.

## When to reach for it / limits
- Use when you want symbolic relational facts to be carried + queried by the substrate's own energy dynamics
  (content-addressable, partial-cue-robust, multi-hop) rather than a dict — the substrate-grounded relational store.
- **Bounded by capacity**: ~20 facts/module. Scale by adding modules/units (linear), not a new mechanism. The
  engineered modular mask (`p_cross` small) that bounds percolation also throttles *cross-module* key→value binding,
  so keep a (subject, relation, object) fact WITHIN one dense module.
- Established throughout: Hopfield content-addressable memory + iterated associative recall + VSA Hadamard
  role-binding. No novelty claimed; the contribution is the connection and the measured envelope.
- Harnesses: `tools/run_jep232_relation_store.py`, `run_jep233_chaining.py`, `run_jep234_typed_relations.py`.
