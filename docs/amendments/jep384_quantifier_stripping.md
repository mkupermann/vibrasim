# JEP-384 — Strip leading quantifiers so subjects aren't polluted ("both frog", "most bird")

## Motivation
Mapping the construction wall (post-JEP-383 diagnostic) surfaced a correctness bug, not just a coverage gap: leading
quantifiers are absorbed into the entity name, creating WRONG facts — "Both frogs and toads are amphibians" →
("both frog", isa, amphibian); "Most birds can fly" → ("most bird", hasprop, fly). Junk facts are worse than misses
(they answer questions incorrectly). Fix: strip leading quantifier words (both/most/some/many/all/several/few/each/
certain) before normalizing, so the real subject is clean and routes to the right handler. ("A/an/the" are NOT
quantifiers and are handled elsewhere — leave them.) No transformer.

## Method
At the top of `_normalize_for_learning` (after the conjunction split), strip a leading quantifier token. "Both X and
Y are Z" then routes to the conjunction-subject handler; "Most/Many/Some X ..." to the plural is-a / property handler
with a clean subject.

## Pre-registered PREDICTION + bars (BEFORE the run)
Prediction: stripping leading quantifiers removes the junk-entity facts and yields the correct clean-subject facts,
without harming "A/an/the" forms or other constructions.

- **J384a (conjunction quantifier):** "Both frogs and toads are amphibians" → (frog, isa, amphibian) AND (toad, isa,
  amphibian), with NO "both frog" junk fact, both seeds (0, 7).
- **J384b (quantifier + plural/property):** "Most birds can fly" → (bird, hasprop, fly) with no "most bird"; "Many
  fish are predators" → (fish, isa, predator) with no "many fish"; both seeds.
- **J384c (no regression):** "A dog is a mammal" → dog→mammal; "Dogs are carnivores" → dog→carnivore; "A whale is not a
  fish" → whale not_isa fish; `pytest -m "not slow" tests/test_conversation.py` passes.

If stripping a quantifier mangles a real subject (e.g. a noun that legitimately starts with one of these words),
report it. Predicted clean. Bars fixed; no retuning. No transformer.

## Result (seeds 0, 7): **PASS** (prediction HIT — junk facts eliminated)
- **J384a (conjunction quantifier): PASS** — "Both frogs and toads are amphibians" → (frog, isa, amphibian) AND
  (toad, isa, amphibian), with **no** "both frog" junk. Both seeds.
- **J384b (quantifier + plural/property): PASS** — "Most birds can fly" → (bird, hasprop, fly) [no "most bird"];
  "Many fish are predators" → (fish, isa, predator) [no "many fish"]. Both seeds.
- **J384c (no regression): PASS** — "A dog is a mammal" → dog→mammal; "Dogs are carnivores" → dog→carnivore;
  "A whale is not a fish" → whale not_isa fish; `tests/test_conversation.py` **10 passed**. Both seeds.

## Verdict: **PASS — a correctness fix: leading quantifiers no longer pollute the store**
Stripping a leading quantifier (both/most/some/many/all/several/few/each/certain/every) before normalizing removes the
junk-entity facts the prior pipeline produced ("both frog", "most bird") and yields the correct clean-subject facts,
while "a/an/the" forms and all other constructions are unaffected and the suite stays green. This is a correctness
improvement (junk facts answer questions WRONG, worse than a miss) on top of the JEP-380/382 coverage fixes — bringing
more natural quantified prose into reliable knowledge. Established rule-based normalization; no transformer.
