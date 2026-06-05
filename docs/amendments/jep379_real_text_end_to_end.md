# JEP-379 — End-to-end on REAL prose: how much of a bounded domain becomes reliably answerable?

## Motivation
The within-domain reasoning arc (367→378) made deep Q&A error-free on SYNTHETIC taxonomies. The honest test is real
encyclopedia-style prose with the messy constructions that hit the parsing wall (plurals, relative clauses,
conjunctions, "kind of", "such as" lists). Read a real paragraph into the live brain, auto-consolidate, and measure how
much becomes reliably answerable — and whether it still abstains (no hallucination) on what the text never said. This
grounds the "reachable bounded domain" claim on real input, not engineered facts. No transformer.

## Method
A short factual paragraph (encyclopedia register) mixing clean and messy constructions:
"Dogs are mammals. Mammals are animals that are warm-blooded. A poodle is a kind of dog. Dogs and cats are carnivores.
A dog has four legs. Salmon are fish, and fish are animals. Birds such as sparrows can fly. The dog, which is a
domesticated animal, can bark."
Read it via `Conversation.read_text` (auto-consolidates). Then ask, via `Conversation.say()`:
- IN-TEXT questions (answers stated or derivable, incl. multi-hop): is-a (poodle→animal, sparrow→animal, salmon→animal),
  property (dog can bark, mammal warm-blooded), numeric (dog legs), negative (poodle is a fish?).
- OUT-OF-DOMAIN questions (never stated): is a tiger an animal?; what is the capital of France? — must abstain / "no".

## Pre-registered PREDICTION + bars (BEFORE the run)
Prediction: the messy constructions cost some parse coverage, so a minority of in-text questions may be unanswerable;
the multi-hop taxonomy core works (consolidation); abstention is perfect (no hallucination). Honest expectation:
in-text accuracy ~0.85 (borderline), OOD abstention 1.0, core multi-hop PASS.

- **J379a (in-text answerable):** ≥ 0.80 of in-text questions answered correctly via `say()`, both seeds (0, 7).
- **J379b (honest abstention):** 100% of out-of-domain questions abstain / answer "no" — zero hallucination, both seeds.
- **J379c (multi-hop from real prose):** the deep multi-hop questions (poodle→animal, sparrow→animal) are both correct,
  both seeds.

If in-text accuracy misses 0.80, the gap is the PARSING wall (a dropped fact makes its question unanswerable) — report
which sentences failed to parse; that is the honest measure of how much real prose the substrate captures. Bars fixed;
no retuning. No transformer.

## Result (seeds 0, 7): **PARTIAL** (one real parse gap + one ground-truth error of mine; abstention perfect)
As-run: in-text accuracy **0.75** (6/8), OOD abstention **1.0**, multi-hop flag False. Diagnosing the two in-text
"failures":
- **`is a sparrow an animal?` — my GROUND-TRUTH ERROR, substrate correct.** The text never states "birds are animals"
  (only "Birds such as sparrows can fly"), so sparrow→animal is NOT derivable. The substrate correctly answered "no"
  (honest abstention on a non-stated fact). I mislabeled it expected-yes. The substrate behaved correctly; my bar input
  was wrong (cf. JEP-361 misprediction).
- **`is a salmon an animal?` — a REAL parse-wall gap.** "Salmon are fish, and fish are animals" parsed to **zero
  facts** — the conjunction-of-clauses form "X are Y, and Y are Z" is not handled by `_normalize_for_learning`. This
  dropped both salmon→fish and fish→animal, so the multi-hop is unanswerable. The honest finding.
- **OOD abstention: PASS** — "is a tiger an animal?" → no, "capital of France?" → abstains. Zero hallucination, both
  seeds. (And note sparrow→animal is the SAME correct abstention behavior.)

What DID parse correctly (the real-prose win): `poodle→dog→mammal→animal` multi-hop from a PLURAL ("Dogs are mammals")
+ a RELATIVE CLAUSE ("Mammals are animals that are warm-blooded") + "a kind of"; `sparrow→bird` from a "such as" list;
dog properties (bark) and legs. The taxonomy core of real encyclopedia prose was captured and reasoned over.

## Verdict: **PARTIAL — real-prose taxonomy works; the honest gap is the conjunction-of-clauses construction**
Reading real encyclopedia prose end-to-end: the substrate captured most of a bounded domain and answered multi-hop
is-a over it (poodle→animal through plural + relative-clause + "kind of"), with PERFECT honest abstention on anything
the text did not state (tiger, France, and correctly sparrow→animal). The literal bar J379a (≥0.80) reads 0.75 as-run,
but exactly ONE of the two misses is a genuine substrate gap — the conjunction "X are Y, and Y are Z" parses to nothing
(dropping salmon→fish→animal); the other miss was my mislabeled ground truth (the substrate was right to abstain). Bar
**not** moved. The single real gap is a concrete, fixable parsing target — add conjunction-of-clauses handling to
`_normalize_for_learning` — pre-registered as JEP-380. No transformer.
