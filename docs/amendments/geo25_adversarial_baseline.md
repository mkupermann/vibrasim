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

## Result — an honest DEFLATION
| query set | geometric | lexical |
|-----------|-----------|---------|
| templated | 1.00 | 1.00 |
| "paraphrased" | 1.00 | **1.00** |

**VERDICT: DEFLATION (honest self-correction).** Lexical token-overlap also scores 1.00 on BOTH sets —
because my "paraphrase" still contained the country NAME (e.g. "France"), a unique token shared with the
target fact. So the capital/named-entity retrieval task is LEXICALLY DETERMINED: a dumb string matcher
solves it via the shared unique key. **Consequence:** the named-entity retrieval / QA / grounding headline
numbers (GEO-15 retrieval, GEO-16/17 hop-1, GEO-23) are substantially solvable WITHOUT the LLM geometry —
they do not, by themselves, prove "geometric understanding." What DOES genuinely require the geometry (no
lexical shortcut, no shared token between cue and answer): the ANALOGY / relation-OFFSET / few-shot results
(GEO-5 0.88, GEO-6 0.94–1.00) and the LLM-prior learning effect (GEO-24). The proper paraphrase test must
REMOVE the shared identifying token — done in GEO-25b (descriptive queries). This is the negative control
doing its job: a chunk of the programme's headline retrieval numbers is lexical, now stated plainly.
