# JEP-114 — naming self-discovered clusters from a few labels (semi-supervised), bridging structure->meaning

## Why
JEP-113 discovered STRUCTURE but the clusters were nameless (no MEANING). A human shown ONE labeled bird names the
whole kind. Bridge: cluster by observation, propagate a label from 1 labeled instance per cluster to the whole
cluster, so the discovered taxonomy becomes a NAMED one the engine reasons over with real words.

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 >=0.9: 1 labeled example per discovered cluster propagates its name; a NEVER-labeled instance then answers
  is-a queries with real names via the named chain. MOST-LIKELY MISS: a cluster lacking any label, or an impure
  cluster mixing labels.

## Acceptance
- PASS: >=0.9 of unlabeled instances correctly answer is-a (real-name category + supercategory) over the named,
  self-discovered taxonomy. Established (semi-supervised label propagation over clusters), named; no novelty.

## Result — PASS (HIT)
4 labeled exemplars (1 per discovered sub-cluster); 20 never-labeled instances tested. 1.00 of them correctly is-a
their NAMED category + supercategory (e.g. obj1 -> {dog, mammal}) over the self-discovered taxonomy. Prediction
HIT; tally 17/26; streak 109-114; 24 tests gated green. Combined with JEP-113 this is a human-like learning
pathway: observe -> cluster (STRUCTURE) -> one label per kind (MEANING) -> named taxonomy -> reason with REAL
concepts. HONEST: needs >=1 label per cluster + pure clusters (JEP-113 condition); a cluster with no label stays
nameless; impure clusters mislabel; this bridges structure->meaning ONLY with a labeling signal, not zero-shot.
Established (semi-supervised label propagation), named; no novelty. The residual frontier: zero-shot meaning
(grounding clusters to language without labels) and arbitrary/non-hierarchical structure (JEP-69/70).
