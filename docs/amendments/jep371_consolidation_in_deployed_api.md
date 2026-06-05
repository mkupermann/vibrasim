# JEP-371 — Wire closure consolidation into the deployed memory (and prove the live API benefits)

## Motivation
JEP-370 proved closure materialization restores deep within-domain reasoning, but only in the test harness. To make it
a real capability, it is now a method on the durable store: `SubstrateMemory.consolidate_closure()` (the relational
analogue of dream consolidation G15/G18). This experiment proves the DEPLOYED API benefits — the normal
`BrainQuery.is_a` (multi-hop) path becomes reliable on deep chains after consolidation, negations stay respected,
consolidation is idempotent, and the full test suite stays green. No transformer.

## Method
Build the JEP-368 taxonomy at ~360 facts. Measure deployed `BrainQuery.is_a` on deep chains and on negative
(non-ancestor) probes BEFORE consolidation; call `mem.consolidate_closure(("isa",))`; measure AFTER on a fresh
`BrainQuery` over the consolidated store. Check idempotency (consolidate twice → identical fact set) and run the fast
test suite.

## Pre-registered PREDICTION + bars (BEFORE the run)
Prediction: after consolidation the deployed `is_a` deep-chain accuracy jumps to ≥0.95 (the direct ancestor edges make
the existing `is_a` resolve in one hop), negatives stay correct, consolidation is idempotent, and no test regresses.

- **J371a (live API restored):** deployed `BrainQuery.is_a` deep-chain accuracy ≥0.95 AFTER consolidation AND strictly
  higher than BEFORE, both seeds (0, 7).
- **J371b (negations respected):** non-ancestor probes still return False at ≥0.95 after consolidation (closure adds
  only true edges; a node that denies an ancestor via not_isa is not bridged), both seeds.
- **J371c (idempotent + no regression):** `consolidate_closure` applied twice yields the same fact set as once; and
  `pytest -m "not slow" tests/test_substrate_memory.py tests/test_conversation.py` passes.

If any bar misses (e.g. consolidation introduces a false ancestor through an exception), report it — that is a real
correctness bug to fix, not to tune around. Bars fixed. No transformer.

## Result (seeds 0, 7): **PARTIAL** (capability fully demonstrated; one bar clause was a misprediction)
- **J371a (live API restored): literal bar NOT met, capability YES.** Deployed `BrainQuery.is_a` deep-chain accuracy
  AFTER consolidation = **1.0 / 1.0** (both seeds, ≥0.95 ✓). BEFORE = 0.9 (seed 0) / **1.0 (seed 7)**. The bar also
  required *strictly > before*, which fails for seed 7 because its before-sample was **already 1.0** — there was no
  headroom to improve. Seed 0 improved 0.9→1.0 as predicted. So the capability holds (after ≥0.95 both seeds); the
  ">before" clause was a misprediction: at exactly N=360/D=8192 the un-consolidated walk is borderline (0.9–1.0), not
  reliably broken, so a given seed's 40-sample can already be perfect. (Same kind of miss as JEP-361's tie-break — the
  mechanism is sound, my literal guess about the baseline was wrong.)
- **J371b (negations respected): PASS** — non-ancestor probes stay ≥0.95 (0.95–0.975) after consolidation, and
  **no edge was bridged through a not_isa exception** (the denied root-most ancestor was never materialized). Both seeds.
- **J371c (idempotent + no regression): PASS** — `consolidate_closure` twice yields the identical fact set; the fast
  suite (`tests/test_substrate_memory.py` + `tests/test_conversation.py`) is **23 passed**. Both seeds.
- Storage cost as expected: 363 → ~2300 facts (materialized closure of a depth-8 taxonomy).

## Verdict: **PARTIAL — the capability is real and shipped; one pre-registered clause mispredicted the baseline**
`SubstrateMemory.consolidate_closure()` is now a method on the durable store (the relational analogue of dream
consolidation G15/G18). The DEPLOYED `BrainQuery.is_a` reaches 1.0 on deep chains after consolidation, exceptions are
respected (no false ancestor bridged through `not_isa`), it is idempotent, and the test suite stays green. The only
miss is the literal "strictly improves over before" clause, which seed 7 could not satisfy because its
un-consolidated baseline was already perfect on that sample — a misprediction about the noisy baseline, not a failure
of the mechanism. Bar **not** moved (honest PARTIAL, per JEP-361 precedent). The within-domain reliability fix from
JEP-370 is now a reusable capability of the deployed brain, available to `talk.py` / `Conversation`. No transformer.
