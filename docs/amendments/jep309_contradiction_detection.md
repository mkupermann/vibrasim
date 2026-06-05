# JEP-309 — Contradiction detection in the durable substrate (vs defeasible exceptions)

## Motivation
The reasoning suite handles defeasible exceptions (JEP-305: a penguin inherits "fly" but a specific "cannot fly"
wins — CONSISTENT). The missing piece is detecting genuine CONTRADICTIONS: a node that DIRECTLY asserts both a
thing and its negation ("a penguin can fly" AND "a penguin cannot fly"; "a whale is a fish" AND "a whale is not a
fish"). The engine resolves these silently (its `consistency_audit` returns []), so ground truth is GENERATED: inject
known contradictions among consistent facts + exceptions, and require the substrate to flag exactly the injected
ones — and crucially NOT flag the exceptions. No transformer.

## Method
`SubstrateMemory.detect_conflicts(gate)`: candidate pairs are nodes holding both a positive and negative DIRECT
edge for the same target (`hasprop`∩`not_hasprop`, `isa`∩`not_isa`), confirmed via `contains()`. Because
`contains()` sees only DIRECT edges, an inherited property + explicit negative (an exception) is NOT flagged —
only a direct double-assertion is.

## Pre-registered bars (BEFORE the run)
- **J309a (exact detection):** on a store with C injected contradictions (direct hasprop+not_hasprop and
  isa+not_isa) among consistent facts, `detect_conflicts` flags EXACTLY the injected set — precision = recall =
  1.0, both seeds (0, 7).
- **J309b (exception ≠ contradiction):** a node that INHERITS a property and has an explicit negative (a JEP-305
  exception, e.g. penguin) is NOT flagged; a node that DIRECTLY asserts both IS flagged. Zero false positives on
  exceptions, both seeds.
- **J309c (persists):** the same conflicts are detected after a fresh reload, both seeds.
- **No-regression:** JEP-305 (defeasible inheritance) still PASS.

Predicted most-likely failure: if I keyed detection off inherited membership instead of direct edges, exceptions
would be mis-flagged as contradictions (J309b fails). Direct-edge `contains()` should prevent this; if J309b shows
false positives on exceptions, that's the diagnosis (membership vs direct edge), reported not tuned.

## Result (seeds 0, 7): **PASS**
- **J309a:** precision = recall = **1.0** — flagged exactly the 3 injected contradictions
  {dog hasprop growl, robin hasprop swim, salmon isa bird}, both seeds. **PASS.**
- **J309b:** the penguin exception (inherits fly, explicit not-fly) was **NOT** flagged — direct-edge `contains()`
  separates a contradiction from a defeasible exception. **PASS.**
- **J309c:** identical after reload. **PASS.** **No-regression:** JEP-305 still PASS. **PASS.**

## Verdict: **PASS**
The substrate detects genuine contradictions (a node DIRECTLY asserting both X and not-X) while leaving defeasible
exceptions (inherited positive + explicit specific negative) untouched — durably. The distinction is structural:
`contains()` sees only direct edges, so an inherited property never collides with an explicit negative. This
completes the reasoning suite over the durable substrate: is-a, part-of, causal, property, open relations,
inheritance, DAG, negation, abduction, and now contradiction detection — all surviving restart and scaling via
module routing (JEP-307).

