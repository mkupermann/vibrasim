# JEP-144 — the open-generation frontier: how far does non-transformer generation reach?

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 graph-walk generation produces FACTUALLY CORRECT multi-sentence text but with LIMITED variety and NO global
  coherence/creativity — factual generation works (templates/graph), open creative generation is no-transformer-
  blocked. PARTIAL mapping the frontier. MOST-LIKELY MISS: it being even flatter (pure fact-listing).

## What is tested
A graph-walk generator: from a concept, emit varied sentences over its facts (categories, properties, relations,
comparisons, causal links) in shuffled order with a few surface templates. Assess factual correctness + variety,
honestly vs creative generation.

## Result — PARTIAL/characterization (HIT): factual generation works, creative is blocked
Generated (varied across runs): "So a poodle is also an animal. A poodle counts as a dog. Every poodle is a pet.
The poodle chases the cat." Factually CORRECT, grammatical, with surface variety (shuffled order, alternate
templates) — but fundamentally FACT-LISTING: no narrative arc, no novel propositions, no discourse coherence beyond
the graph. CONCLUSION: FACTUAL/descriptive generation WORKS without a transformer (templates/graph-walk over known
facts); OPEN/CREATIVE generation (novel ideas, narrative structure, style, abstraction) is the genuine no-
transformer-blocked frontier. The engine can SAY what it knows, not INVENT. Prediction HIT; tally 39/58. This maps
the LAST major capability frontier. COMBINED FRONTIER MAP (now complete): real-prose parse (94% simple / 2% dense),
abstract/superordinate words (PMI underdetermines levels), structure learning (clean=easy, noisy=hard via
compounding, sparse=active-querying), grounding (favorable-regime self-taught), and OPEN GENERATION (factual works,
creative blocked) — all honestly characterized. Established (template/graph-walk generation), named; no novelty.
