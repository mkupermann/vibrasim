# JEP-365 — Teaching efficiency: you pay per TYPE, not per sentence (reframing the asymptote)

## Motivation
JEP-362 showed coverage over *sentences* asymptotes (Zipfian tail). JEP-364 showed the self-prompting loop teaches a
missing construction TYPE once, then covers all its instances. Put together, these reframe the pessimism: the cost of
reaching a domain is the number of distinct **types** you must teach, NOT the number of sentences — and each type is
taught exactly once via self-prompting. This experiment measures that efficiency, to give the honest *practical*
bottom line behind Michael's question: a bounded factual domain is reachable because teaching scales with types
(hundreds), not sentences (millions). No transformer.

## Method
Model a corpus as N sentences, each an instance of one of T construction types (types Zipfian-distributed; many
sentences per type). Run the self-prompting loop (JEP-364): when a sentence's type has not yet been taught, that is
ONE teaching event (the teacher supplies an example-set; the type is now covered for all its future instances);
otherwise it is parsed for free. Count teaching events and the coverage trajectory. Compare against rote per-sentence
teaching (one event per sentence).

## Pre-registered PREDICTION + bars (BEFORE the run)
Prediction: self-prompting teaching events == number of DISTINCT types that appear (each taught exactly once), which
is ≪ N; the sentences-per-teaching-event ratio grows with N (the saving compounds). Coverage of a held-out stream
equals the fraction of its sentences whose type was seen in training — so the only residue is the type tail (matching
362 but over TYPES, a far smaller set). The honest bottom line: a bounded domain is reachable because you pay per type.

- **J365a (pay per type, not per sentence):** number of self-prompting teaching events == number of distinct types
  encountered, and is < 25% of N for N=5000, T=200, both seeds (0, 7).
- **J365b (coverage = types-seen):** held-out coverage equals the fraction of held-out sentences whose type appeared
  in training, within 0.01; and exceeds 0.90 once ≥90% of type-probability-mass has been seen, both seeds.
- **J365c (the saving compounds):** the sentences-per-teaching-event ratio at N=5000 is strictly greater than at
  N=500 (more data amortizes the fixed type cost), both seeds.

Predicted surprise to watch: if types were as numerous as sentences (no reuse) the ratio would be ~1 and there'd be no
saving — but real language reuses constructions heavily, which is the honest model. If J365a/c fail, reuse is lower
than assumed; report it. No transformer.

## Result (seeds 0, 7): **PASS** (prediction HIT — all three bars)
- **J365a (pay per type, not per sentence): PASS** — self-prompting fired exactly **200 teaching events == 200
  distinct types** to cover **5000 sentences** (4% of N, well under the 25% bar); rote per-sentence teaching would
  need 5000. Both seeds.
- **J365b (coverage = types-seen): PASS** — held-out coverage = **1.0**, exactly the fraction of held-out sentences
  whose type was taught (all 200 types appeared in 5000 draws), with full type-mass seen. Both seeds.
- **J365c (the saving compounds): PASS** — sentences-per-teaching-event = **25.0 at N=5000** vs **~3.7–4.1 at N=500**:
  more data amortizes the fixed per-type cost. Both seeds.

### Honest caveat (the model's boundary)
This models a **finite, fixed** type set (T=200), so with enough sentences all types appear and coverage reaches 1.0.
Real language's *type* inventory itself has a tail — new construction types keep appearing — so coverage would NOT
reach 1.0; the residue is exactly that type tail (the same Zipfian shape as JEP-362, but over a far smaller, slower-
growing set than sentences). The claim proven here is the *efficiency*: cost scales with distinct types encountered,
each taught once, not with sentences. It does NOT claim the type set is finite. Stated plainly so the win isn't
oversold.

## Verdict: **PASS — you pay per type, and that's what makes a bounded domain reachable**
The asymptote from JEP-362 is over **sentences**; the self-prompting loop (JEP-364) converts the cost to **distinct
construction types**, each taught exactly once, then covering all its instances for free. The efficiency is large
(25× here) and *grows* with corpus size because constructions are reused heavily. This is the honest, *optimistic*
half of the answer to Michael that the asymptote alone misses: a bounded factual domain is genuinely reachable, not
because teaching is unlimited, but because teaching scales with **reusable abstractions (hundreds)**, not raw
sentences (millions). The only residue is the slow type tail — far more tractable than the sentence tail. Combined:
JEP-362 (sentence asymptote) + JEP-364 (self-prompting) + JEP-365 (per-type cost) = the substrate reaches a bounded,
teachable domain efficiently, but not open-domain. No transformer.
