# JEP-381 — Scale on a realistic article: how much of natural factual prose is captured?

## Motivation
JEP-379/380 worked on an 8-sentence paragraph partly shaped to the parser. The honest scale test is a longer article
(~28 sentences) of natural factual prose with constructions NOT optimized for the substrate (appositives, passive
voice, multi-clause, definitions, lists), to measure the TRUE capture rate and whether within-domain reliability +
abstention hold at that volume. This grounds the "read a real text" use case with an honest coverage number — what
fraction of natural encyclopedia prose becomes reliable knowledge, and what is the residual (the parsing wall). No
transformer.

## Method
A ~28-sentence factual article on the animal kingdom (natural register, mixed constructions). Read via
`Conversation.read_text` (auto-consolidates). Measure:
- **Coverage:** fraction of declarative factual sentences that yield ≥1 stored fact.
- **Q&A reliability:** a fixed set of questions whose answers are stated in CLEAR sentences (is-a incl. multi-hop,
  property, numeric) — accuracy via `say()`.
- **Abstention:** questions about entities never mentioned — must abstain / "no" (no hallucination).

## Pre-registered PREDICTION + bars (BEFORE the run)
Prediction: natural prose costs real coverage (passive/appositive/complex sentences won't parse), so coverage ~0.55–0.75;
BUT what is captured is answered reliably (consolidation), incl. multi-hop; abstention perfect. The honest message:
the reachable domain is the clearly-stated subset, reasoned over reliably, with honest "I don't know" elsewhere.

- **J381a (coverage):** ≥ 0.55 of declarative factual sentences yield ≥1 stored fact, both seeds (0, 7).
- **J381b (Q&A reliability):** ≥ 0.90 accuracy on the fixed clear-fact question set (incl. ≥2 multi-hop), both seeds.
- **J381c (abstention):** ≥ 0.95 of out-of-domain questions abstain / answer "no" (zero hallucination), both seeds.

If coverage is below 0.55, report which construction types dominate the misses (the honest wall map). If Q&A on
clearly-stated facts misses 0.90, that is a reliability regression to investigate. Bars fixed; no retuning. No transformer.

## Result (seeds 0, 7): **PARTIAL** (coverage excellent + abstention perfect; a real relative-clause parse bug found)
- **J381a (coverage): PASS — and far above prediction** — **0.963** (26/27 factual sentences captured), 53 facts.
  Natural prose captured much better than the predicted 0.55–0.75: the plural/conjunction/relative/"such as"/appositive
  handlers cover most of the article. Both seeds.
- **J381c (abstention): PASS** — OOD abstention **1.0** ("is a robot an animal?", "capital of japan?", "is a banana a
  mammal?" all correctly not-yes). Zero hallucination. Both seeds.
- **J381b (Q&A reliability): NOT met (0.833) — a REAL parse bug.** Failures: `is a dog an animal?` and `is a poodle an
  animal?` (the dog→mammal→animal chain). Diagnosed: "Mammals are animals that are warm-blooded" is normalized by the
  plural is-a rule to "A mammal is a **warm-blooded**." — it takes the LAST word of the object as the head, so the
  relative clause "that are warm-blooded" hijacks the head, giving `mammal→warm-blooded` instead of `mammal→animal`.
  The chain breaks. (Notably `salmon→vertebrate` and `salmon→animal` PASS — "Fish are animals that live in water"
  doesn't end in "s" so it bypasses the buggy rule and the engine parses `fish→animal` correctly. Same construction,
  opposite outcome, exposing the bug.)

## Verdict: **PARTIAL — high real-prose coverage + perfect abstention, with one real relative-clause bug**
At article scale (~28 natural sentences) the substrate captured **96%** of factual sentences and abstained perfectly on
everything unmentioned — strong evidence the real-prose pipeline holds up. The one real defect: the plural is-a rule
"X are Y that ..." grabs the wrong head noun when the object carries a relative clause, mis-storing the is-a and
breaking multi-hop chains through it. This is a concrete, fixable parser bug (strip the relative clause before taking
the head) — pre-registered as JEP-382. Coverage and abstention bars met; the Q&A miss is this single bug, not a
reliability regression. Bars not moved. No transformer.
