# JEP-305 — Negation & defeasible exceptions in the durable substrate (penguin cannot fly)

## Motivation
The engine handles exceptions: "a bird can fly" + "a penguin is a bird" + "a penguin cannot fly" ⇒ a penguin
canNOT fly (the specific exception beats the general rule), and explicit negative is-a ("a whale is not a fish").
Show the durable substrate does the same, natively: store negative facts as their own roles (`not_hasprop`,
`not_isa`) and resolve queries by **most-specific-explicit-wins** defeasible inheritance over the VSA store. No
transformer.

## Method
Bridge `properties`→hasprop, `not_properties`→not_hasprop, `parents`→isa, `neg_isa`→not_isa. Then over the
reloaded store:
- `has_property_def(x, p)`: walk is-a ancestors from x (most specific first); at the FIRST ancestor with an
  explicit `not_hasprop p` → False, or explicit `hasprop p` → True; else False.
- `is_a_def(x, y)`: if `contains(x, "not_isa", y)` → False; else the gated is-a climb.

## Pre-registered bars (BEFORE the run)
- **J305a (defeasible property with exceptions):** on a set mixing inherited-true (robin→fly), exception-false
  (penguin→fly), specific-overrides-general (bat can fly though mammal cannot), and negatives, the substrate
  matches the engine's `has_property` ≥ 0.90, both seeds (0, 7).
- **J305b (explicit negative is-a):** `is_a_def` matches the engine's `is_a` on a set including explicit negatives
  (whale≠fish) ≥ 0.95, both seeds.
- **J305c (persists):** answers identical after a fresh reload, both seeds.
- **No-regression:** JEP-301 (positive inheritance) still PASS.

Predicted most-likely failure: ordering — if the ancestor walk isn't strictly most-specific-first, a general rule
could beat a specific exception (bat-can-fly lost to mammal-cannot-fly). If J305a misses on the bat/penguin cases,
that's the diagnosis (walk order), reported not tuned.

## Result (seeds 0, 7): **PASS**
- **J305a:** defeasible property vs engine = **1.000**, both seeds. **PASS.**
- **J305b:** explicit negative is-a vs engine = **1.000**, both seeds. **PASS.**
- **J305c:** identical after reload. **PASS.** **No-regression:** JEP-301 still PASS. **PASS.**
- Demos (reloaded store): penguin can fly = **False** (exception beats "bird can fly"); robin = **True**
  (inherits); **bat = True** (specific "bat can fly" overrides "mammal cannot fly"); dog = **False** (inherits
  mammal's negative); whale is fish = **False** (explicit negative); whale is animal = **True**.

## Verdict: **PASS**
The substrate resolves negation and **defeasible exceptions** by most-specific-explicit-wins over its persistent
store, matching the engine — including the hard specificity case (a bat flies even though mammals don't). Negative
facts are just additional roles (`not_hasprop`, `not_isa`); the override is the ancestor-walk order. With JEP-301
this gives full defeasible inheritance (inherit by default, exceptions win) durably and natively. The reasoning
suite over the durable substrate now spans is-a, part-of, causal, property, open relations, inheritance, DAG, and
negation/exceptions.

