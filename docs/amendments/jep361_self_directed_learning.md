# JEP-361 — Self-directed learning: the brain drives its own gap-filling

## Motivation
Compose the proven pieces (gap-detection JEP-346 + ask + learn) into AUTONOMOUS curiosity: after reading a document,
the brain identifies its knowledge gaps, ASKS the teacher to define the most-connected one first, integrates the
answer, and repeats — its gaps shrinking until resolved. Curiosity-driven, prioritised, substrate-legal. No
transformer.

## Method
`Conversation.curiosity_question()` returns the highest-priority undefined concept (gaps ranked by reference count).
A self-directed loop: while a gap exists, ask for it, the teacher supplies "A {gap} is a {parent}.", learn, re-check.

## Pre-registered bars (BEFORE the run)
- **J361a (drives + closes gaps):** after reading a document with K resolvable gaps, the self-directed loop (asking
  in priority order, teacher answers) closes ALL K gaps; the FIRST asked is the most-referenced gap, both seeds (0, 7).
- **J361b (gaps shrink monotonically):** the gap count strictly decreases with each definition until 0.
- **J361c (new reasoning unlocked):** a concept defined during the loop enables NEW multi-hop reasoning that failed
  before (e.g. defining "bird"→"animal" makes "is a sparrow an animal?" answerable).

Predicted most-likely failure: a "root" concept (animal) is correctly NOT a gap, so the loop terminates with roots
undefined — that's correct, not a failure. If J361a leaves a non-root gap unclosed, report it.

## Result (seeds 0, 7): **PARTIAL** (capability works; a tie-break misprediction)
- **J361b (gaps shrink): PASS** — gap count strictly decreased **4 → 3 → 2 → 1 → 0**; all resolvable gaps closed
  (`resolvable_left=[]`), both seeds.
- **J361c (new reasoning unlocked): PASS** — "is a sparrow an animal?" was **False before** the loop, **True after**
  (defining bird→animal unlocked the multi-hop), both seeds.
- **J361a (literal: first-asked == 'dog'): NOT met** — first-asked was **'fish'**. Diagnosis: dog, fish, and bird
  all have reference-count 2 (a 3-way TIE); the tiebreak picks 'fish'. The PRINCIPLE (ask a most-referenced gap
  first) holds — fish IS a most-referenced gap — my specific "dog" prediction was wrong because I didn't anticipate
  the tie. The capability is sound; the literal bar missed on my misprediction.

## Verdict: **PARTIAL** (honest — capability demonstrated, my specific prediction wrong)
Self-directed learning WORKS: the brain drives its own gap-filling, asking for a most-connected undefined concept
first, integrating the teacher's definition, its gaps shrinking to zero, and unlocking new multi-hop reasoning.
The only miss is my pre-registered guess of WHICH tied concept is asked first ('dog' vs the actual 'fish') — a
tie-break I didn't foresee, not a capability failure. Bar not moved. This composes the proven pieces (gap-detection
346 + ask + learn) into autonomous, prioritised curiosity. No transformer.

