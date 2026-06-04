# GEO-25 — Adversarial self-review: does a TRIVIAL lexical baseline match the geometric method?

## Motivation
Many rungs hit 1.00 on TEMPLATED sentences. Honest worry (negative-control discipline): templated tasks may
be solvable by dumb string matching, in which case the LLM geometry adds nothing THERE and "geometric
understanding" would be overclaimed. GEO-25 pits the geometric retriever against a trivial token-overlap
(Jaccard) retriever on BOTH templated and PARAPHRASED queries. The honest prediction: lexical ties geometry
on templated queries (deflation) but FAILS on paraphrases, where only the embedding geometry survives — so
the LLM geometry's real contribution is paraphrase/semantic robustness, not the templated headline numbers.

## Pre-registration (locked BEFORE run)
- 15 facts "The capital of <country> is <city>." Two query sets: TEMPLATED ("What is the capital of
  <country>?") and PARAPHRASED ("Which city serves as <country>'s seat of government?").
- Methods: (a) geometric (MiniLM cosine), (b) lexical (token Jaccard overlap vs each fact).
- Metric: retrieval hits@1 on each query set.
- Honest bars: expect lexical ~ geometric on TEMPLATED (>=0.8 both) -> templated numbers don't prove
  geometry; expect geometric >> lexical on PARAPHRASED (geometric >=0.7, lexical < geometric by >=0.3) ->
  the LLM geometry's true value is semantic robustness. Report all four cells; any surprise is the finding.

PASS-as-designed if it isolates the real contribution (lexical competitive on templated, geometry wins
paraphrase). This is a deflation/honesty rung, not a victory lap.
