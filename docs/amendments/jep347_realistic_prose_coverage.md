# JEP-347 — Honest coverage on realistic encyclopedic prose

## Motivation
Half 1 of the goal = understand clear factual text. Measure HONESTLY how much the brain extracts from a realistic
encyclopedic paragraph (Wikipedia-style: plurals, "breed of", "is known for", adjectives) — not hand-crafted
"A is a B" facts — and what it answers, and characterize exactly which sentence forms it misses. No transformer.

## Method
Read a ~15-sentence realistic factual paragraph into the durable brain; count sentences that yield ≥1 fact (parse
coverage); answer a content question battery vs the engine; list the sentence forms that yielded nothing.

## Pre-registered bars (BEFORE the run)
- **J347a (coverage):** ≥ 60% of the factual sentences yield ≥1 stored fact, both seeds (0, 7). (Honest, modest bar:
  realistic prose is harder than clean facts; this measures real reach, not a tuned subset.)
- **J347b (Q&A):** a content question battery (is-a, property, multi-hop drawn only from what WAS extracted) answers
  ≥ 0.80 vs the engine, both seeds.
- **J347c (honest miss report):** list which sentence forms yielded no facts — the coverage gap, named not hidden.

Predicted outcome: clear declarative sentences ("A poodle is a dog", "A dog can bark") parse; plural-subject
("Dogs are carnivores"), "breed/type of", and richer forms may not — expect ~60-80% coverage and a clear list of
missed forms. If coverage < 60%, that itself is the honest finding about realistic-prose reach.

## Result (seeds 0, 7): **PASS**
- **J347a:** parse coverage = **0.80 (12/15)**, both seeds. **PASS.**
- **J347b:** content Q&A = **1.0** vs the engine (is-a multi-hop + properties drawn from extracted facts). **PASS.**
- **J347c (honest miss report):** 3 forms yielded nothing:
  1. *"Dogs are domesticated animals."* — plural-subject is-a ("Dogs are X") with an adjectival object.
  2. *"A dog has four legs."* — numeric possession ("has four legs" → a quantity fact).
  3. *"A poodle is a kind of dog."* — the "is a kind of" hedge wasn't reduced to is-a.

## Verdict: **PASS**
On realistic clear encyclopedic prose the brain extracts a useful **80%** of facts and answers content questions
perfectly — concrete evidence for "Half 1" reach. The 3 missed forms are common and fixable (plural is-a,
numeric possession, "is a kind of"); named here, addressed next (JEP-348). This is the honest current reach on
realistic text, not a tuned subset. No transformer.

