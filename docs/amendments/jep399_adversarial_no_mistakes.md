# JEP-399 — Adversarial "no mistakes" audit: can we make it assert a falsehood?

## Motivation
The core guarantee is "no mistakes inside the captured domain + honest abstention outside". This adversarially
stress-tests it: construct tricky read-prose scenarios designed to elicit a WRONG answer (a confident falsehood, the
worst failure) — negation, exception chains, ambiguous "is X Y", multi-parent DAGs, contradictions, untaught probes,
and is-a DIRECTIONALITY. The bar is that the brain NEVER asserts a falsehood: every answer is correct or an honest "I
don't know". If it does assert a falsehood, that is a critical finding. No transformer.

## Method
Read each scenario via `read_text` (auto-consolidates), then probe with questions whose ground truth is known. Classify
each answer as CORRECT, ABSTAIN (honest "don't know"/no), or FALSEHOOD (confident wrong assertion). Scenarios:
- negation: "A whale is a mammal. A whale is not a fish." → whale fish? no; whale mammal? yes
- exception: "Birds can fly. A penguin is a bird. A penguin cannot fly." → penguin fly? no; sparrow (a bird) fly? yes
- directionality: "A dog is a mammal." → is a mammal a dog? NO (is-a is one-way)
- multi-parent DAG: "A platypus is a mammal. A platypus is an egg-layer." → both yes
- ambiguous is-X-Y: "A dog is warm-blooded." → dog warm-blooded? yes; is a dog a cat? no
- untaught: "is a whale a planet?" → abstain/no (not a confident yes)

## Pre-registered PREDICTION + bars (BEFORE the run)
Prediction: zero confident falsehoods; high correct rate; directionality respected. (Genuinely adversarial — a
falsehood would be a critical bug.)

- **J399a (no falsehoods):** ZERO confident-falsehood answers across all scenarios, both seeds (0, 7).
- **J399b (correct rate):** ≥0.85 of the should-answer questions are CORRECT, both seeds.
- **J399c (directionality):** "is a mammal a dog?" → no (is-a is not symmetric), both seeds.

If any falsehood appears, report the scenario and the wrong answer (critical). Bars fixed; no retuning. No transformer.

## Result (seeds 0, 7): **PASS** (zero falsehoods under adversarial probing)
- **J399a (no falsehoods): PASS** — **0 confident falsehoods** across all six scenarios (negation, exception chains,
  directionality, multi-parent DAG, ambiguous is-X-Y, untaught probes). Both seeds.
- **J399b (correct rate): PASS** — **13/14 = 0.929** correct; the single non-correct is an honest ABSTAIN on a true
  fact (a missed yes, not a wrong assertion), which is the safe failure mode. Both seeds.
- **J399c (directionality): PASS** — "is a mammal a dog?" → **no** (is-a is one-way; the directed binding from JEP-298
  keeps it asymmetric). Both seeds.

Highlights: negation correction held (whale not a fish), the deep exception held (penguin can't fly, sparrow can),
multi-parent DAG both-true (platypus is a mammal AND an egg-layer), ambiguous "is a dog warm-blooded?" → yes (property)
while "is a dog a cat?" → no, and untaught probes ("is a whale a planet/vegetable?") correctly abstained.

## Verdict: **PASS — the "no mistakes" guarantee holds under adversarial probing**
Deliberately tricky read-prose scenarios designed to elicit a confident falsehood produced ZERO — every answer was
either correct or an honest "no/don't know", is-a directionality was respected, and the only imperfection was a safe
abstain on a true fact (never a wrong assertion). This is the strongest evidence yet for the core guarantee Michael
asked about: inside the domain it has read, the substrate does not lie — it answers correctly or admits it doesn't
know. Composes the negation/exception/directed-binding/abstention machinery validated across the programme. No
transformer. (The open-domain knowledge-tail wall, JEP-362, remains separate and standing.)
