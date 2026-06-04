# GEO-17 — Realism stress test: 3 hops + large distractor store + PARAPHRASED questions

## Motivation
GEO-16 multi-hop was 1.00 but on CLEAN templates, 20 facts, 2 hops. Real understanding needs robustness.
GEO-17 stresses all three: (1) 3 hops (Person->Company->City->Country), (2) a large distractor fact store
(100+ irrelevant facts), (3) PARAPHRASED natural questions (not the template). If accuracy survives, the
method is genuinely useful; if it degrades, that is an honest boundary.

## Pre-registration (locked BEFORE run)
- 12 chains Person->Company->City->Country (36 chain facts) + 120 DISTRACTOR facts (random unrelated
  sentences) all in one store.
- Questions PARAPHRASED, e.g. "In which country is the firm employing <Person> based?" (no template match).
- 3-hop iterative geometric retrieval; bridges extracted symbolically.
- Bars: 3-hop accuracy >= 0.6 with distractors+paraphrase (chance ~1/(#countries)). Report per-hop
  retrieval accuracy too (where does it break). Compare to clean-template 3-hop.

PASS if >=0.6 under the hard condition. PARTIAL if clean works but paraphrase/distractors degrade it. NULL
if it breaks. ALL outcomes reported (this is a boundary-mapping rung).
