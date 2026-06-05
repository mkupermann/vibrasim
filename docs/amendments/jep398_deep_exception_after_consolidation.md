# JEP-398 — Does a DEEP exception still win after consolidation flattens ancestor order?

## Motivation
JEP-396/397 revealed that closure consolidation materializes ALL ancestor is-a edges as direct edges, so `_ancestors`
no longer returns them strictly most-specific-first (the BFS visits all direct ancestors at one level, in arbitrary
cleanup order). `has_property` relies on most-specific-first to make exceptions win: it returns False on the first
`not_hasprop` and True on the first `hasprop`. If the order is scrambled, a property defined on a GENERAL ancestor
could be returned True before a `not_hasprop` exception on a MORE-SPECIFIC (but non-leaf) ancestor is seen — silently
giving the wrong answer. This tests the order-sensitive case directly. Honestly uncertain: it may already fail. No
transformer.

## Method
Build a 3-level chain where the exception is on a MID ancestor, not the leaf:
`baby_penguin → penguin → bird`; `bird` hasprop fly; `penguin` not_hasprop fly. After consolidation, ask
"can a baby_penguin fly?" — correct answer is NO (penguin's exception overrides bird's property), even though penguin
is not the leaf and not the root. Also the classic leaf case (penguin can't fly) and the positive inheritance
(sparrow can fly) as controls.

## Pre-registered PREDICTION + bars (BEFORE the run)
Prediction (genuinely uncertain): the deep/mid exception MAY fail after consolidation because `has_property` iterates
`_ancestors` in scrambled order. If it fails, `has_property` must order ancestors by specificity (depth) before
scanning — a real fix. If it passes, the leaf-first BFS start plus exception placement happens to preserve correctness.

- **J398a (leaf exception, control):** "can a penguin fly?" → No (penguin not_hasprop fly), both seeds (0, 7).
- **J398b (DEEP/mid exception):** "can a baby_penguin fly?" → No (penguin's exception wins over bird's property),
  both seeds — THIS is the order-sensitive bar.
- **J398c (positive inheritance, control):** "can a sparrow fly?" → Yes, both seeds.

All measured AFTER `consolidate()`. If J398b fails, that is the honest finding (consolidation breaks deep-exception
resolution); fix by sorting ancestors by depth in `has_property`. Bars fixed; no retuning. No transformer.

## Result (seeds 0, 7): **PASS** (the order-sensitive case works — and is now provably robust)
- **J398a (leaf exception): PASS** — "can a penguin fly?" → No. Both seeds.
- **J398b (DEEP/mid exception): PASS** — "can a baby_penguin fly?" → **No**: penguin's `not_hasprop fly` (a MID
  ancestor) overrides bird's `hasprop fly`, even after consolidation flattened the ancestor order. Both seeds.
- **J398c (positive inheritance): PASS** — "can a sparrow fly?" → Yes. Both seeds.

### Hardening (defensive, not bar-driven)
The first run passed, but correctness relied on cleanup order happening to surface the specific exception first — luck,
not a guarantee. Since exceptions are correctness-critical for "no mistakes", I hardened `has_property` to sort the
(flattened) ancestors by specificity (number of own ancestors; deeper = more specific) BEFORE scanning, so
most-specific-wins is provably correct regardless of cleanup order. JEP-398 still passes both seeds and the
conversation suite stays 10/10.

## Verdict: **PASS — deep exceptions resolve correctly after consolidation, now guaranteed**
Closure consolidation flattens `_ancestors` order, which in principle could let a general property beat a more-specific
exception. The test confirmed it currently resolves correctly, and the defensive depth-sort in `has_property` makes it
**provably** correct rather than cleanup-order-dependent — important because exceptions/defeasible reasoning underpin
the "no mistakes inside the domain" guarantee. No transformer.
