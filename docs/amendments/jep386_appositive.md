# JEP-386 — Appositive handling ("The lion, a large cat, is a predator")

## Motivation
The construction-wall diagnostic showed appositives mis-parse: "The lion, a large cat, is a predator" →
(lion, isa, predator) [correct] + ("large cat", isa, predator) [JUNK] and MISSES (lion, isa, cat). An appositive
"X, a Y, <predicate>" asserts both X<predicate> AND X is a Y. Fix: rewrite it into those two clauses (mirroring the
existing "X, which is a Y, <rest>" relative-clause handler), eliminating the junk and capturing the missed is-a. No
transformer.

## Method
Add an appositive rule to `_normalize_for_learning`: "(The/A) X, a/an Y, <rest>" → "A X is a <head-of-Y>." + "A X
<rest>." Placed with the relative-clause handler; guarded so it does not fire on "such as" or "which is" forms.

## Pre-registered PREDICTION + bars (BEFORE the run)
Prediction: the appositive yields both is-a facts and no junk entity.

- **J386a (appositive both facts):** "The lion, a large cat, is a predator" → (lion, isa, cat) AND (lion, isa,
  predator), with NO ("large cat", isa, predator) junk, both seeds (0, 7).
- **J386b (generalizes):** "A robin, a small bird, eats worms" → (robin, isa, bird) [and the rest clause handled
  without a "small bird" junk subject], both seeds.
- **J386c (no false-fire + no regression):** "The lion, which is a large cat, is a predator" still works via the
  relative-clause rule (lion→cat, lion→predator); "Amphibians, such as frogs and toads, live ..." still routes to the
  such-as handler (frog/toad→amphibian, no junk); `pytest -m "not slow" tests/test_conversation.py` passes.

If the appositive rule swallows a "such as"/"which" sentence, report it. Predicted clean. Bars fixed; no retuning. No
transformer.

## Result (seeds 0, 7): **PASS** (prediction HIT — junk eliminated, missed is-a captured)
- **J386a (appositive both facts): PASS** — "The lion, a large cat, is a predator" → (lion, isa, **cat**) AND (lion,
  isa, predator), with **no** "large cat" junk entity. Both seeds.
- **J386b (generalizes): PASS** — "A robin, a small bird, eats worms" → (robin, isa, bird), no junk subject. Both seeds.
- **J386c (no false-fire + no regression): PASS** — "The lion, which is a large cat, is a predator" still works via the
  relative-clause rule (lion→cat, lion→predator); "Amphibians, such as frogs and toads, live ..." still routes to the
  such-as handler (frog/toad→amphibian, no junk); `tests/test_conversation.py` **10 passed**. Both seeds.

## Verdict: **PASS — appositives captured correctly; the construction-wall sweep is comprehensive**
The appositive "X, a Y, <rest>" now rewrites to "X is a <head-of-Y>" + "X <rest>", capturing the previously-missed is-a
(lion→cat) and eliminating the junk entity ("large cat"→predator), without disturbing the relative-clause or such-as
handlers. Together with JEP-380 (conjunction-of-clauses), 382 (relative-clause head), 384 (quantifier stripping), and
385 (passive voice), the common real-prose constructions surfaced by the post-JEP-383 diagnostic are now handled
correctly — more natural encyclopedia prose becomes reliable, junk-free knowledge. Established rule-based
normalization; no transformer.
