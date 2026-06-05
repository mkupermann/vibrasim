# JEP-402 — Correctness guards: miss rather than capture wrong (protect "no mistakes")

## Motivation
JEP-401 found dense prose breaks "never wrong capture": ('heart','isa','fist') from an appositive whose phrase ends in
a comparative modifier ("a muscular organ roughly the size of a fist"), and ('because they','hasprop','warm-blooded')
from a subordinate clause. Wrong facts undermine the "no mistakes" guarantee far more than misses do. Add guards that
REJECT suspicious parses — better to miss than to be wrong. No transformer.

## Method
- **Appositive guard:** only accept "X, a Y, <rest>" when Y is a short simple noun phrase (≤2 words, no preposition
  of/than/by/from/with/in/on/at/to/for). A long/prepositional Y means the "head = last word" heuristic is unreliable →
  skip the rewrite (miss).
- **Bad-subject/object guard:** reject any extracted fact whose subject or object is, or contains, a pronoun
  (they/it/he/she/we/i/you) or a subordinating conjunction (because/although/though/while/since/if/when/despite) — a
  global validity filter applied to all learned facts.

## Pre-registered PREDICTION + bars (BEFORE the run)
Prediction: the two wrong captures disappear (the sentences are missed, not mis-captured), CLEAN appositives still work,
and dense-prose junk rate goes to 0 — while clean-article capture is unaffected.

- **J402a (no heart→fist):** "The heart, a muscular organ roughly the size of a fist, pumps blood." does NOT produce
  (heart, isa, fist) (nor any X→fist), both seeds (0, 7).
- **J402b (no subordinate-subject junk):** "Because they are warm-blooded and breathe air, whales must surface." does
  NOT produce any fact with a "because"/"they" subject, both seeds.
- **J402c (clean appositive intact + dense junk=0 + no regression):** "The lion, a large cat, is a predator." still →
  (lion, isa, cat) AND (lion, isa, predator); re-running JEP-401 the junk rate is **0.0** with coverage still ≥0.25
  (good facts kept); `pytest -m "not slow" tests/test_conversation.py` passes; both seeds.

If a guard rejects a legitimate parse (e.g. a clean appositive), report it. Predicted clean. Bars fixed; no retuning.
No transformer.

## Result (seeds 0, 7): **PARTIAL** (correctness goal MET; the coverage sub-bar was my over-estimate)
- **J402a (no heart→fist): PASS** — "The heart, a muscular organ roughly the size of a fist, pumps blood" no longer
  produces (heart, isa, fist) (the appositive guard rejects the long/prepositional Y phrase). Both seeds.
- **J402b (no subordinate-subject junk): PASS** — "Because they are warm-blooded and breathe air, whales must surface"
  no longer produces a "because they" fact (the leading subordinating-conjunction strip → "they are warm-blooded…" →
  the pronoun subject is rejected). Both seeds.
- **J402c (clean appositive + junk=0 + suite): correctness met, coverage sub-bar NOT met.** Clean appositive intact
  ("The lion, a large cat, is a predator" → lion→cat AND lion→predator); dense-prose **junk rate = 0.0** (zero wrong
  captures); suite **10 passed**. BUT dense coverage dropped to **0.188** (< my 0.25 guess) — because removing the two
  WRONG facts correctly left only the 3 genuinely-simple sentences ("A dog is a mammal", "Smoking causes cancer", "A
  salmon is a fish"). The drop IS the guards working; my ≥0.25 bar over-estimated how much *correct* content the dense
  paragraph contains.

## Verdict: **PARTIAL — "never wrong capture" RESTORED; coverage bar was a misprediction (not moved)**
The guards achieve their real purpose: zero wrong captures on dense prose (no heart→fist, no subordinate-clause
subject), clean appositives unaffected, suite green. The "no mistakes" guarantee — which "never wrong capture"
underpins — now holds on dense prose too: the pipeline MISSES hard sentences rather than fabricating facts from them.
The only unmet clause is my coverage≥0.25 guess: the honest *correct-only* coverage on this deliberately-dense
paragraph is 0.188 (it simply contains few parseable-without-error sentences), and the drop from 0.312 is precisely the
two junk facts being correctly rejected. Bar not moved (cf. JEP-393). Net: dense prose now yields fewer facts, but
every fact it yields is correct. No transformer.
