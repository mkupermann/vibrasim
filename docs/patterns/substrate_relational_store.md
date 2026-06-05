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
   the raw settled bits (no clean-up) OR the decoded clean code — identical within capacity. **STOP at roots with the
   ENERGY GATE, not value-overlap** (JEP-243/244): a leaf at the top of a chain has no outgoing edge, but `hop(root)`
   still returns a clean spurious node — value-overlap can't tell (the value always settles to an attractor), so the
   chain OVERRUNS into spurious nodes and breaks negatives/leak-guards. Continue a hop only if its settled energy ≤
   `0.7 × median(stored-pattern energies)` (the same JEP-237 detector). This is the SAME "stored vs untrained key"
   check as the DAG empty-slot gate — use the energy detector at EVERY such check, not just where it first surfaced.

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

## Multi-parent DAGs (JEP-235/236/237)
A bare key→value store is a FUNCTION: one attractor per key, so a multi-parent node (`poodle→dog` AND `poodle→pet`)
loses an edge (JEP-235d). Fix:
5. **SLOT-BIND multiplicity**: store edge *i* of a child under a distinct key `child_code ⊙ slot_i_code` (a few fixed
   role codes). Recover all parents by querying each slot.
6. **GATE empty slots by ENERGY, not overlap**: an untrained slot still relaxes to *some* clean parent code (the value
   slot's only attractors ARE parent codes), so value-overlap can't reject it — but a TRAINED (key,value) pair is a
   DEEP minimum (≈ −90) while a spurious slot is shallow (≈ −40). Accept a slot iff settled `energy ≤ 0.7 × median(
   stored-pattern energies)` (threshold from the training patterns only). This gives 0 false-accept / 0 false-reject
   and DAG transitive closure = 1.00, matching the symbolic engine. BFS the multi-parent ancestor set over gated
   retrieval. (Lesson: to detect "was this key trained?", measure the key→value BINDING energy, not value cleanliness.)

## When to reach for it / limits
- Use when you want symbolic relational facts to be carried + queried by the substrate's own energy dynamics
  (content-addressable, partial-cue-robust, multi-hop) rather than a dict — the substrate-grounded relational store.
- **Bounded by capacity**: ~20 facts/module. Scale by adding modules/units (linear), not a new mechanism. The
  engineered modular mask (`p_cross` small) that bounds percolation also throttles *cross-module* key→value binding,
  so keep a (subject, relation, object) fact WITHIN one dense module.
- Established throughout: Hopfield content-addressable memory + iterated associative recall + VSA Hadamard
  role-binding. No novelty claimed; the contribution is the connection and the measured envelope.
- Harnesses: `tools/run_jep232_relation_store.py`, `run_jep233_chaining.py`, `run_jep234_typed_relations.py`.
