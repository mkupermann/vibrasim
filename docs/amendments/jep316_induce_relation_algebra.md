# JEP-316 — Inducing relation algebra (symmetry / transitivity) from the fact pattern, then auto-applying it

## Motivation
So far I hard-coded which reasoning a relation gets (is-a climbs, married-to is symmetric). The deeper "learns like a
brain" step: INDUCE a relation's algebraic type from its own stored facts, then apply the matching reasoning
automatically. Established relational-property induction (ILP-lite / closure statistics), named as such — no
transformer.

## Method
Over the durable store, for each relation compute two signals from `mem.facts`:
- **symmetry score** = rate at which a stored (a, rel, b) has its reverse (b, rel, a) also stored.
- **transitivity score** = over stored a→b and b→c, rate at which a→c is also stored.
Classify: symmetric if sym ≥ 0.7; transitive if trans ≥ 0.7; else neither. Then ANSWER queries using the detected
type (symmetric → both directions; transitive → accept composed pairs), and score vs ground truth.
(Transitive relations are materialized as their closure so the signal is present in the facts; symmetric relations
store both directions — both are detectable from the pattern alone.)

## Pre-registered bars (BEFORE the run)
- **J316a (induction):** classify 9 relations (3 symmetric: married_to/sibling_of/neighbor_of; 3 transitive:
  ancestor_of/bigger_than/located_in; 3 neither: eats/likes/owns) — per-relation type matches ground truth ≥ 0.90,
  both seeds (0, 7).
- **J316b (auto-apply):** answering with the INDUCED type matches ground-truth relation-holds ≥ 0.90 on a balanced
  query set (incl. reverse queries for symmetric, composed pairs for transitive), both seeds.
- **J316c (persists):** induction + answers identical after a fresh reload, both seeds.

Predicted most-likely failure: a transitive relation also looks partly symmetric if it has short cycles, or a
small sample makes a score noisy and flips a class. If J316a misclassifies, report which signal was ambiguous for
which relation (a feature-separability finding), don't move the 0.7 threshold post hoc.

## Result (seeds 0, 7): **PASS**
- **J316a:** classification = **1.0** — all 9 relations correctly typed (married_to/sibling_of/neighbor_of→sym;
  ancestor_of/bigger_than/located_in→trans; eats/likes/owns→neither), both seeds. **PASS.**
- **J316b:** auto-applied reasoning (reverse for symmetric, composed pairs for transitive) vs ground truth =
  **1.0**, both seeds. **PASS.**
- **J316c:** induction + answers identical after reload. **PASS.**

## Verdict: **PASS**
The substrate INDUCES a relation's algebraic type (symmetric / transitive / neither) from its own fact pattern —
symmetry from the reverse-presence rate, transitivity from the composition-closure rate — and then applies the
matching reasoning automatically, instead of the type being hard-coded. A step toward "learns the rules, not just
the facts." Established relational-property induction (closure statistics / ILP-lite), named as such. Honest scope:
transitive relations are detected when materialized as closure (the signal lives in the facts); a cover-only store
would need composed-query examples to induce transitivity — a supervised extension.

