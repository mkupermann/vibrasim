# JEP-177 — held-out is-a generalization needs REDUNDANT structure (DAG), not just scale

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 the joint-embedding infers held-out is-a edges from geometry at above-chance but modest accuracy (scale-limited
  at ~24 concepts per JEP-52), while symbolic closure returns 0 (can't derive untold). RISK: near-chance at small scale.

## Result — MISS (the reason is STRUCTURAL, not scale); a genuine insight
Attempted to show the learned-embedding's added value (held-out generalization symbolic closure can't do). Holding
out edges of a TREE taxonomy revealed the test is ILL-POSED on trees: every non-root concept has exactly ONE parent
edge, so holding it out ISOLATES the concept (no other path), and NEITHER symbolic closure NOR the embedding can
place/infer it. The 24-concept run left only 2 testable pairs (embedding 0.50, symbolic 0.00 — underpowered);
scaling to ~120 concepts did not help because the structural problem is independent of size: a TREE has NO REDUNDANCY.
THE REAL VARIABLE IS STRUCTURE, not scale (my prediction blamed scale — MISS): held-out is-a generalization is only
well-posed when there is REDUNDANT structure — a DAG (multi-parent), sibling-cluster regularity, or features — that
lets the geometry infer an unstated relation from OTHER kept relations. This is exactly the regime where embeddings
were shown to generalize (JEP-28/52, real multi-parent WordNet taxonomies at scale). DEEP CONNECTION: generalization,
like ROBUST INFERENCE (the compounding/aggregation theme JEP-138/140), needs REDUNDANCY — on a tree (single path,
no redundancy) you can neither error-correct a noisy chain NOR infer a held-out edge; a DAG (many paths) enables
both. So the JEP-176 bridge stands (prose -> taxonomy -> embedding reproduces symbolic is_a in-sample), and the
embedding's GENERALIZATION payoff is real but requires DAG redundancy + scale (established, JEP-28/52), not testable
on a prose-learned tree. Durable lesson: check a test is WELL-POSED for the structure before predicting an accuracy.
Prediction MISS; tally 67/93. Established (order/poincare embeddings, transitive-closure generalization); named; no novelty.
