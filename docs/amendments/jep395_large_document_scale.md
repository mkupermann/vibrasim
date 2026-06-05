# JEP-395 — Does the real-prose pipeline hold at book-chapter scale?

## Motivation
The real-prose pipeline was validated on ~20-sentence articles. Michael wants to read whole texts/books. This stress-
tests SCALE: read increasing prefixes of a ~50-sentence connected factual document and measure the coverage and
multi-hop Q&A-accuracy CURVE vs document size — does reliability hold as the consolidated store grows to hundreds of
facts across multiple modules, or degrade? No transformer.

## Method
A ~50-sentence connected factual article (animal kingdom: nested taxonomy + properties + part-of + causal). Read
prefixes of 12 / 25 / 50 sentences; at each, consolidate and measure coverage (sentences yielding ≥1 fact) and Q&A
accuracy on a fixed question set (deep multi-hop is-a, property, part-of), plus OOD abstention and junk rate at full
size.

## Pre-registered PREDICTION + bars (BEFORE the run)
Prediction: coverage stays high and stable (~0.80+) across sizes; multi-hop Q&A stays reliable (≥0.90) because closure
consolidation + analog readout were proven to scale to hundreds of facts (JEP-378); abstention perfect, junk ~0. If
Q&A degrades with size, that is the honest scale ceiling for real prose.

- **J395a (coverage stable):** coverage ≥0.80 at ALL three sizes (12/25/50), both seeds (0, 7).
- **J395b (Q&A reliable at full scale):** Q&A accuracy ≥0.90 on the 50-sentence document, including ≥2 deep multi-hop
  questions, both seeds.
- **J395c (clean + abstaining at scale):** at 50 sentences, OOD abstention ≥0.95 AND junk rate ≤0.05, both seeds.

If Q&A drops below 0.90 at 50 sentences while holding at 12/25, report the size where it breaks (the honest curve).
Bars fixed; no retuning. No transformer.

## Result (seeds 0, 7): **PASS** (prediction HIT — holds at book-chapter scale)
- **J395a (coverage stable): PASS** — coverage **1.0 / 1.0 / 0.92** at 12 / 25 / 50 sentences (the 0.92 at full size is
  duplicate facts re-stated, not parse failures). Both seeds.
- **J395b (Q&A reliable at full scale): PASS** — Q&A **1.0** on the 50-sentence document (**120 base facts**,
  consolidated across multiple auto-grown modules), including all deep multi-hop questions: poodle→animal (4 hops),
  whale→vertebrate, salmon→vertebrate, bee→animal. Both seeds.
- **J395c (clean + abstaining at scale): PASS** — OOD abstention **1.0**, junk rate **0.0**. Both seeds.

## Verdict: **PASS — reading a real document end-to-end is reliable at scale**
The real-prose pipeline holds at book-chapter scale: a ~50-sentence connected article (nested taxonomy + properties +
part-of + causal) is captured at ~92–100% coverage, consolidated to 120+ facts across multiple modules, and answered at
**100% Q&A** including deep 4-hop multi-hop, with perfect abstention and zero junk. The closure-consolidation + analog-
readout reliability (JEP-378) and the construction sweep (379-392) compose without degradation as the document grows.
This substantiates the "read a real text/book" use case at realistic scale — no transformer. The open-domain knowledge-
tail wall (JEP-362) remains the separate, standing boundary.
