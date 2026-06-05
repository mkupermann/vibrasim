# JEP-319 — Inducing two-relation COMPOSITION rules (grandparent = parent∘parent), applied over the store

## Motivation
JEP-316/318 induced single-relation algebra (symmetry, transitivity) and inverse pairs. The next step in "learns the
rules": induce that a target relation is the COMPOSITION of two base relations — grandparent_of = parent_of ∘
parent_of; aunt_of = sibling_of ∘ parent_of — from a few labeled examples, then answer held-out target queries by
composing base-relation retrievals (no target facts stored). Established ILP-style path/rule induction, named as
such. No transformer.

## Method
Base relations (parent_of, sibling_of) stored. For a target T with K labeled (a,c) examples, search base-relation
pairs (R1,R2): coverage = rate over examples that ∃x with (a R1 x) and (x R2 c). Induce the rule = the (R1,R2) with
coverage ≥ 0.8. Apply: T(a,c) ⇔ ∃x ∈ `query_all(a,R1)` with c ∈ `query_all(x,R2)` over the persistent store.

## Pre-registered bars (BEFORE the run)
- **J319a (induce the rule):** for grandparent_of and aunt_of, the induced (R1,R2) equals the true composition,
  both seeds (0, 7).
- **J319b (apply to held-out):** answering HELD-OUT target queries (not in the labeled set, never stored) by
  composing base retrievals vs ground truth ≥ 0.90, both seeds.
- **J319c (negative + persists):** a scrambled target (random (a,c) pairs) yields NO covering rule (coverage <0.8
  for all pairs); induction + answers identical after reload.

Predicted most-likely failure: multi-child branching means `query_all(a,R1)` returns several x; if the gate drops
one needed intermediate, a true composed pair reads false (recall miss). JEP-303/307 set-retrieval+routing should
hold; if J319b misses, report whether it's a dropped-intermediate (gate) or a wrong-rule (induction) error.

## Result (seeds 0, 7): **PASS**
- **J319a:** induced rules exact — grandparent_of=(parent_of, parent_of), aunt_of=(sibling_of, parent_of), both
  seeds. **PASS.**
- **J319b:** held-out target queries answered by composing base retrievals over the store vs ground truth = **1.0**,
  both seeds. **PASS.**
- **J319c:** a scrambled target yields NO covering rule (coverage <0.8); induction persists after reload. **PASS.**

## Verdict: **PASS**
The substrate induces that a target relation is the COMPOSITION of two base relations from a couple of labeled
examples, and answers held-out target queries by composing base-relation retrievals (`query_all` ∘ `query_all`)
over the persistent store — no target facts stored. With JEP-316/317/318 the system now learns single-relation
algebra (symmetry, transitivity), relation structure (inverses), AND two-relation composition rules from data, and
applies them all over the durable store. Established ILP-style rule induction, named as such; no transformer.

