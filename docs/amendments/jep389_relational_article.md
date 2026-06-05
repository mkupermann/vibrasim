# JEP-389 — Relational article capstone: taxonomy + part-of + causal, all queryable

## Motivation
JEP-388 added part-of querying and causal variants. This validates them in a full article alongside taxonomy: a
factual text mixing is-a, part-of, and causal sentences, read end-to-end, with all three relation types queryable, plus
abstention and a no-junk correctness gate. Confirms the substrate captures a real article's RELATIONSHIPS, not just its
taxonomy. No transformer.

## Method
Read a ~16-sentence factual article (is-a taxonomy + part-of + causal) via `read_text` (auto-consolidates). Measure
coverage, Q&A across all three relation types (is-a multi-hop, "is X part of Y?", "what causes X?"), OOD abstention,
and junk rate (multi-word entity names).

## Pre-registered PREDICTION + bars (BEFORE the run)
Prediction: high coverage, reliable Q&A across is-a/part-of/causal, perfect abstention, zero junk.

- **J389a (coverage):** ≥0.80 of factual sentences yield ≥1 fact, both seeds (0, 7).
- **J389b (multi-relation Q&A):** ≥0.90 accuracy on a fixed question set spanning is-a (incl. multi-hop), part-of, and
  causal, both seeds.
- **J389c (abstention + no junk):** OOD abstention ≥0.95 AND junk rate ≤0.05, both seeds.

If a relation type misses, report which (the residual). Bars fixed; no retuning. No transformer.

## Result (seeds 0, 7): **PARTIAL** (coverage + abstention + junk + is-a/part-of/most-causal pass; 2 real gaps)
- **J389a (coverage): PASS** — 0.812 (13/16). Both seeds.
- **J389c (abstention + no junk): PASS** — OOD abstention 1.0, junk rate 0.0. Both seeds.
- **J389b (multi-relation Q&A): NOT met (0.80) — two real gaps.** Passing: is-a multi-hop (car→vehicle→machine),
  part-of query (wheel/engine/tire), part-of negative, causal "what causes heat/expansion?". Failing:
  1. **"what causes accidents?"** — the source is "Worn brakes cause accidents", whose subject is an ADJECTIVE+NOUN
     ("Worn brakes"); the causal rule only handles a single-word subject, so it parses nothing. Adjectival noun-phrase
     subjects are the gap.
  2. **"how many wheels does a car have?"** — "A car has four wheels" stores (car, has_wheels, 4), but `how_many` is
     hardcoded to read `has_legs` only and the parser ignores the part name. So non-"legs" counts are unreachable.

## Verdict: **PARTIAL — relational capture works broadly; two concrete gaps to close**
A relational article (is-a + part-of + causal) is read at 81% coverage with perfect abstention and zero junk, and Q&A
works across multi-hop is-a, part-of (now queryable), and causal — except two honest gaps: (1) causal/relational
subjects that are adjective+noun phrases ("Worn brakes") aren't parsed; (2) `how_many`/`"how many X does Y have?"` is
hardcoded to legs and ignores the part name, so other part-counts ("how many wheels") are stored but unqueryable — the
same "stored-but-unreachable" class as the part-of gap JEP-388 fixed. The second is the cleaner, higher-value fix
(generalize `how_many` to any counted part), pre-registered as JEP-390. Bars not moved. No transformer.
