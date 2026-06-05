# JEP-417 — Irregular verb morphology (English): "what did X write?" matches stored "wrote"

## Motivation
Teaching the substrate English starts with morphology. The JEP-416 demo showed "what did Peat write?" failed because
the stored verb was "wrote" (irregular past) and `_vstem` (w[:5]) doesn't relate write/wrote. Add an irregular past→
present lemma map so taught action facts are queryable regardless of tense. No transformer.

## Method
`_VERB_LEMMA` maps common irregular past forms to present (wrote→write, built→build, taught→teach, …); `_vstem`
normalizes through it before stemming, so query and stored verbs canonicalize together.

## Pre-registered bars
- **J417a:** "Peat wrote Synchronicity." → "what did Peat write?" → synchronicity; "Newton built a telescope." → "what
  did Newton build?" → telescope; both seeds (0, 7).
- **J417b:** regular verbs still work ("Bohm proposed holography." → "what did Bohm propose?" → holography).
- **J417c:** `pytest -m "not slow" tests/test_conversation.py` passes.

## Result: **PASS** — "what did Peat write?"→synchronicity, write/build/discover/propose all match across tense;
10 tests pass. English verb morphology (irregular past↔present) handled for open-relation queries.

## Verdict: **PASS** — taught action facts are queryable regardless of verb tense; a first piece of "teach English".
No transformer.
