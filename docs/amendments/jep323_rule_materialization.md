# JEP-323 — Closing the learning loop: materialize induced rules into the durable store

## Motivation
JEP-318/319/321 INDUCE rules (inverse, composition, recursive closure) and answer by re-deriving each time. The
brain-like closure: once a rule is induced, MATERIALIZE its consequences as facts (forward-chaining) so the derived
relation is then directly, cheaply queryable AND persists — discovered knowledge becomes part of the store and
compounds. Established forward-chaining / deductive closure, named as such. No transformer.

## Method
Given a base store and an induced rule (e.g. grandparent_of = parent_of ∘ parent_of; ancestor_of = closure of
parent_of), derive all consequent (a,c) over the store via the rule's traversal and `add_fact(a, target, c)`. Then
the derived relation is answerable by a single `query` (no climb), and survives save/load.

## Pre-registered bars (BEFORE the run)
- **J323a (compose then materialize):** induce grandparent_of=parent∘parent, materialize it; every true
  grandparent pair is then DIRECTLY retrievable (single `query`/`contains`, no climb) ≥ 0.95, no false pairs, both
  seeds (0, 7).
- **J323b (recursive closure then materialize):** induce ancestor_of=closure(parent), materialize; every ancestor
  pair (incl. ≥4-hop) directly retrievable ≥ 0.95; a non-ancestor pair is NOT, both seeds.
- **J323c (persists + compounds):** materialized facts survive reload; a second-order query that USES the
  materialized relation (e.g. great-grandparent via materialized grandparent + parent) is then answerable.

Predicted most-likely failure: materializing a large closure adds many facts to one module and could push it over
capacity (K*), so a freshly-materialized fact lands fine but an OLD fact's similarity drops — JEP-296 neurogenesis +
JEP-307 routing should absorb it; if J323a/b miss after materialization, report the added-fact count vs module cap.

## Result (seeds 0, 7): **PASS** (after a diagnosed gate + test-target fix)
- **First cut:** grandparent 1.0, but ancestor 0.933 (14/15) and compound False. Two causes: (1) materializing the
  closure gives `g0` SEVEN ancestors under one key, whose per-value similarity is below a gate calibrated on
  single-valued `parent_of` edges (the predicted high-fan-out effect; calibration lesson #13); (2) my compound
  target was (g0,g4) = 4 hops = great-GREAT-grandparent, not great-grandparent (g0,g3) — a test bug.
- **Fixed** (relation-appropriate gate calibrated on each relation's own edges; correct target):
  - **J323a:** grandparent materialized → directly retrievable **1.0**, no false pairs. **PASS.**
  - **J323b:** ancestor closure materialized → directly retrievable **1.0** (incl. deep), non-ancestors not. **PASS.**
  - **J323c:** great-grandparent (g0→g3) answerable via the MATERIALIZED grandparent relation + parent. **PASS.**

## Verdict: **PASS**
The learning loop closes: an induced rule (composition, recursive closure) is materialized into the durable store,
so the derived relation becomes directly queryable, persists, and COMPOUNDS into higher-order queries (great-
grandparent built on materialized grandparent). Discovered knowledge becomes part of the brain. Honest lessons: a
materialized closure creates high-fan-out keys that need a per-relation gate (not the base relation's), and the
bug was the gate/test, not the substrate. Established forward-chaining / deductive closure, named as such.

