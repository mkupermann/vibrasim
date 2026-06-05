# JEP-301 — Substrate-native cross-relation inheritance (compose is-a climb with a target relation)

## Motivation
JEP-300's named boundary: a single-relation climb can't do INHERITANCE — "a dog can bark, a poodle is a dog ⇒ a
poodle can bark", or "a heart is part of a dog, a poodle is a dog ⇒ a heart is part of a poodle". The engine does
this. Show the SUBSTRATE can too, natively: all facts (isa, partof, hasprop) already live in the persistent VSA
store; inheritance is a *composed query procedure* over them — climb the subject's is-a ancestors and probe the
target relation at each. No new representation, no transformer.

## Method (over the reloaded persistent store)
- `isa_ancestors(x)` = is-a gated climb from x, collecting {x, parent, grandparent, …}.
- `has_property_inh(x, p)` = ∃ a ∈ isa_ancestors(x): `contains(a, "hasprop", p)`.
- `part_of_inh(y, x)` = ∃ a ∈ isa_ancestors(x): the part-of climb from y reaches a.
Ground truth = engine `has_property` / `part_of`.

## Pre-registered bars (BEFORE the run)
- **J301a (property inheritance):** substrate matches engine `has_property` ≥ 0.90 on a balanced set —
  direct, 1-level-inherited, 2-level-inherited, and negatives — both seeds (0, 7).
- **J301b (part inheritance):** substrate matches engine `part_of` ≥ 0.90 on a balanced set — direct part-of,
  transitive part-of, inherited-across-is-a, and negatives — both seeds.
- **J301c (persists):** answers identical after a fresh reload, both seeds.
- **No-regression:** JEP-300 multi-relational bridge still PASS.

Predicted most-likely failure: the is-a store returns only the single best parent per node (not a set), so a
multi-parent (DAG) node would lose a branch and miss an inherited fact. The test taxonomy is a tree (single
parent), so this should not bite; if J301a/b fall short on a DAG case, the honest finding is "substrate is-a climb
needs set-valued parents for DAG inheritance" — reported, not tuned.

## Result (seeds 0, 7): **PASS** (after a diagnosed first-cut partial)
- **First cut:** property inheritance **1.0** (PASS) but part inheritance **0.76 / 0.82** (FAIL). Concrete demos
  (poodle→bark, poodle→breathe, heart∈poodle, cell∈poodle) were all correct, so the store was fine — the
  composition was wrong. Diagnosed two bugs in *my reasoning procedure* (NOT the substrate):
  1. false positives (e.g. "animal part_of poodle"): `partof_reaches(y, y)` returned True trivially, so an is-a
     ancestor of x equal to y counted — must require a **real** part edge.
  2. false negatives (e.g. "cell part_of animal"): the engine inherits part-of **both ways** along the holder's
     is-a chain (a dog's heart is also a *mammal's* part, since dog is-a mammal); I only climbed *down* to subtypes.
- **Corrected composition:** `part_of_inh(y,x)` = y is a PROPER part of some holder z, and z is in x's is-a chain
  in either direction (z ∈ supertypes(x), or x ∈ supertypes(z)). → property **1.0**, part **1.0**, both seeds.
- **J301c:** persists across reload. **J301a/b PASS. No-regression:** JEP-300 still PASS.

## Verdict: **PASS**
The substrate does cross-relation INHERITANCE natively by composing its is-a climb with a target-relation probe
over the persistent store — matching the engine on both property ("a poodle can bark/breathe", inherited 1–2
levels) and part ("a heart/cell is part of a poodle", inherited across is-a both ways). This closes the boundary
named in JEP-300. Honest discipline note (error-class #3): a failing composite test implicated the obvious
component (the substrate); the demos proved otherwise and the real bug was my reasoning procedure not matching the
engine's part-of semantics — fixed the method, not the bar. Single-best-parent is-a climb still assumes a tree;
set-valued parents for DAG taxonomies remain future work.

