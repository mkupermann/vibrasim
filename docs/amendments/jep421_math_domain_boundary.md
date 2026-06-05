# JEP-421 — The math domain boundary: definitions/taxonomy YES, computation NO

## Motivation
Michael supplied a math resource (Open University, "Numbers, Units and Arithmetic"). Honestly map what the substrate
can become from math content: it stores facts and reasons over them, but it does NOT COMPUTE. So mathematical
DEFINITIONS and TAXONOMY (units, terms, categories, "a metre is a unit of length") are reachable, but ARITHMETIC
("what is 2+3?") is not — that requires a computation the fact-store cannot perform or generalize. Honest boundary,
sets expectations for the math resource. No transformer.

## Method
Teach math definition/taxonomy facts (units, measurement terms) and verify reasoning; then confirm arithmetic
statements neither store nor answer, and that teaching one specific sum does not enable a different sum (no
generalization — the computation wall).

## Pre-registered PREDICTION + bars (BEFORE the run)
- **J421a (definitions/taxonomy reachable):** "A metre is a unit of length. A unit is a measurement. An hour is a unit
  of time." → "is a metre a unit?" yes, "is a metre a measurement?" yes (multi-hop), both seeds (0, 7).
- **J421b (computation NOT reachable — the honest wall):** "what is two plus three?" → abstains (no answer); after
  "Two plus three is five." (which does not parse to a usable arithmetic fact), "what is two plus four?" still abstains.
  Document: the substrate recalls taught FACTS, it does not COMPUTE.
- **J421c (no regression):** `pytest -m "not slow" tests/test_conversation.py` passes.

Either way the finding is the honest boundary. The reachable math content is conceptual/definitional (taught by the LLM
parent); computation belongs to a calculator/algorithm, not a fact substrate. Bars fixed; no retuning. No transformer.

## Result (seeds 0, 7): **PASS** — definitions reachable, computation is the honest wall
- **J421a (definitions/taxonomy): PASS** — "A metre is a unit of length. A unit is a measurement." → "is a metre a
  unit?" yes, "is a metre a measurement?" yes (multi-hop metre→unit→measurement). Math definitions/taxonomy parse and
  reason. Both seeds.
- **J421b (computation NOT reachable): CONFIRMED** — "what is two plus three?" abstains; "Two plus three is five." does
  not produce a usable arithmetic fact, and "what is two plus four?" still abstains. The substrate recalls taught FACTS,
  it does not COMPUTE. Both seeds.
- **J421c (no regression): PASS** — `tests/test_conversation.py` 10 passed.

## Verdict: **PASS — honest math boundary: conceptual/definitional content yes, arithmetic no**
From a math resource the substrate can learn DEFINITIONS and TAXONOMY (units, measurement terms, categories) and reason
over them multi-hop, taught by the LLM parent — but it does NOT COMPUTE arithmetic (that needs a calculator/algorithm,
not a fact store), and teaching one sum does not generalize to another. This sets honest expectations for the Open
University math resource: teach its definitions and concepts, not its calculations. No transformer.
