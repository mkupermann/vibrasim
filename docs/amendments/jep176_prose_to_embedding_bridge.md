# JEP-176 — bridge learn-from-prose (symbolic) to the JOINT-EMBEDDING pillar

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 the bridge works mechanically, but per JEP-52 (geometric is_a weak <50 concepts) the geometric reasoning is
  UNRELIABLE on a small prose-learned taxonomy — symbolic closure wins at this scale; learned-embedding pays off
  only at scale. RISK: the embedding better than expected on tiny clean taxonomies.

## Result — MISS (better than predicted); the bridge is validated
Read a multi-passage document -> inverted engine.parents into a {parent:children} taxonomy (24 concepts, 23 edges)
-> fit the ConceptReasoner joint-embedding -> compared geometric is_a to the symbolic closure (ground truth) on
64 positive + 64 sampled negative ancestor pairs:
- symbolic closure: 1.00 (it IS the ground truth)
- joint-embedding (poincare): recall 0.97, specificity 0.92, balanced-acc 0.95
- joint-embedding (order): recall 1.00, specificity 0.98, balanced-acc 0.99
PREDICTION MISS: I predicted the embedding would be UNRELIABLE at 24 concepts; it was RELIABLE (order 0.99). DIAGNOSIS:
I conflated IN-SAMPLE reconstruction (reliable even when small — the embedding was trained on these edges) with
HELD-OUT generalization (the actual JEP-52 weakness at <50 concepts). I tested in-sample reconstruction, where small
scale is fine. So the honest result is STRONGER than predicted: the BRIDGE between learn-from-prose (symbolic) and
the joint-embedding pillar WORKS, and the learned embedding faithfully reproduces the symbolic is_a reasoning — the
two halves of the programme connect (prose -> taxonomy -> joint-embedding -> geometric reasoning that agrees with
symbolic closure). The embedding's ADDED value over symbolic closure is HELD-OUT generalization at SCALE (interpolate
unstated edges, JEP-28/52) — the regime not re-tested here and the genuine reason to use the learned pillar. Durable
lesson: distinguish in-sample reconstruction from held-out generalization when citing an embedding-accuracy caveat.
Prediction MISS; tally 67/92. Established (joint-embedding / order embeddings, taxonomy embedding); named; no novelty.
