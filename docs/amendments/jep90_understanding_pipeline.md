# JEP-90 — end-to-end understanding on SIMPLE language: the developmental path (answer to "Boole first or English first?")

## Why (Michael's strategy question)
JEP-89: understanding mechanisms work GIVEN structure, but Boole's prose can't be parsed into structure by classic
methods. Recommendation: build the understanding machinery on SIMPLE parseable language FIRST, prove it end-to-end,
THEN scale to hard text. This rung proves the machinery works where the parse is tractable — contrasting with the
Boole failure (JEP-89) to establish "simple -> hard", not "Boole-first".

## Setup
- Controlled mini-English: IS-A facts ("A poodle is a dog", "A dog is an animal", ...) + SVO facts ("the dog
  chases the cat"). Parse is reliable on this grammar (unlike Boole).
- Pipeline: parse -> (s,rel,o) -> IS-A parent graph (transitive closure, JEP-84) + VSA-bound SVO facts (JEP-88).
- Comprehension battery: (A) same-bag SVO true/false ("dog chases cat" vs "cat chases dog"); (B) multi-hop IS-A
  never stated ("is a poodle a living thing?").
- Baseline: bag-of-words (word-sum) matching - expected to fail both (ties on A, no inference on B).

## Pre-registration (locked BEFORE run)
- PASS: structured pipeline >= 0.90 on BOTH (A) and (B), AND bag-of-words <= 0.6 on (A) and <= 0.6 on (B). Proves
  the understanding machinery works end-to-end on tractable language where bag-of-words cannot.
- HONEST BOUND up front: works because the language is SIMPLE enough to parse reliably; scaling the PARSE to
  Boole-level prose is the open gate (JEP-89); and it is text-only, NOT grounded in perception (symbol-grounding
  gap, JEP-54..63). Established (VSA/HRR, transitive closure), named; no novelty. The point is the PATH.

## Result — PASS
| comprehension | structured pipeline | bag-of-words |
|---------------|--------------------|--------------| 
| (A) same-bag SVO true/false | **1.00** | 0.00 |
| (B) multi-hop IS-A (unstated) | **1.00** | 0.50 (chance) |

**VERDICT: PASS.** The understanding machinery (parse -> VSA-bind + transitive closure) works END-TO-END on simple
parseable language, answering same-bag truth and multi-hop inference where bag-of-words cannot. This is the
evidence for the strategy answer to "Boole first or English first?": develop the understanding machinery on SIMPLE
language where the parse is tractable, prove it, THEN scale difficulty. The SAME pipeline recovered nothing from
Boole (JEP-89) — Boole is the final exam, not the primer. HONEST BOUND: works because the language is simple enough
to parse reliably (the parse, not the mechanism, is the gate at scale); and it is TEXT-ONLY, not grounded in
perception (the symbol-grounding gap, JEP-54..63, is the deeper requirement for human-level/25yo understanding).
Established (VSA/HRR, transitive closure), named; no novelty.

## Strategy answer (recorded)
Neither "teach full English first" (that IS the goal, not a precursor) nor "train with Boole first" (backwards —
Boole presupposes ~20 years of grounded experience). The path is DEVELOPMENTAL: build parse->bind->infer->ground
on simple language, prove each rung (this), scale gradually; Boole is the final exam. Human-level (25yo)
understanding additionally needs GROUNDING in experience, not just text — the open multi-year frontier under the
no-transformer constraint.
