# JEP-387 — Validation: a harder article exercising the whole construction sweep

## Motivation
JEP-380/382/384/385/386 each fixed one real-prose construction. This validates the CUMULATIVE pipeline on a harder
~20-sentence article that deliberately exercises all of them (passive voice, appositives, quantifiers, conjunctions-of-
clauses, relative clauses, "such as", definitions), measuring coverage, Q&A reliability (incl. multi-hop and a passive
query), honest abstention, AND a correctness gate: no junk multi-word entities polluting the store. No transformer.

## Method
Read a harder factual article via `Conversation.read_text` (auto-consolidates). Measure: coverage (sentences yielding
≥1 fact), Q&A accuracy on a fixed question set (is-a multi-hop, property, numeric, passive "what was X <verb> by?"),
OOD abstention, and junk rate (fraction of fact subjects/objects that are multi-word — should be ~0).

## Pre-registered PREDICTION + bars (BEFORE the run)
Prediction: with the full sweep, coverage is high (≥0.80), Q&A reliable (≥0.90 incl. multi-hop + passive), abstention
perfect, and junk ~0 (the quantifier/appositive fixes removed multi-word entities).

- **J387a (coverage):** ≥0.80 of factual sentences yield ≥1 fact, both seeds (0, 7).
- **J387b (Q&A incl. multi-hop + passive):** ≥0.90 accuracy on the fixed question set, with both multi-hop questions
  and the passive query correct, both seeds.
- **J387c (abstention + no junk):** OOD abstention ≥0.95 AND junk rate (multi-word entity names among stored facts)
  ≤ 0.05, both seeds.

If coverage or Q&A misses, report which construction still fails (the residual wall). If junk > 0.05, a handler still
leaks a multi-word entity — report it. Bars fixed; no retuning. No transformer.

## Result (seeds 0, 7): **PASS** (prediction HIT — the whole sweep validated)
- **J387a (coverage): PASS** — **0.90** (18/20 factual sentences captured), 33 facts. Both seeds.
- **J387b (Q&A incl. multi-hop + passive): PASS** — Q&A accuracy **1.0** (all 10 questions), including both multi-hop
  questions (dog→animal, lion→vertebrate via conjunction-of-clauses) AND the passive query ("what was the salmon eaten
  by?" → bear). Both seeds.
- **J387c (abstention + no junk): PASS** — OOD abstention **1.0** (robot, capital of Italy, rock — all correctly
  not-yes); junk rate **0.0** (zero multi-word entity names in the store). Both seeds.

## Verdict: **PASS — real encyclopedia prose captured cleanly and answered without mistakes**
A harder ~20-sentence article exercising passive voice, appositives, quantifiers, conjunction-of-clauses, relative
clauses, "such as", and definitions is read end-to-end: **90% coverage, 100% Q&A** (including multi-hop and a passive
query), **perfect abstention**, and **zero junk facts**. This validates the cumulative construction sweep
(JEP-380/382/384/385/386) on top of the within-domain reliability arc (367-378) and multi-day persistence (383): the
substrate now reads realistic factual prose and answers it without mistakes inside the captured domain, while abstaining
honestly outside it — no transformer. The open-domain knowledge-tail wall (JEP-362) remains the separate, standing
boundary.
