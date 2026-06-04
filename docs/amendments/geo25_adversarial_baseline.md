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

## GEO-25b result — the genuine contribution, isolated
| query set | geometric | lexical | chance |
|-----------|-----------|---------|--------|
| descriptive, NO shared token | **0.80** | 0.10 | 0.10 |

**VERDICT: PASS.** With the lexical shortcut removed (queries are DESCRIPTIONS — "the country famous for the
Eiffel Tower" — sharing no identifying token with "The capital of France is Paris"), geometry scores 0.80
while lexical collapses to chance 0.10. **This isolates the LLM geometry's real, irreducible value: SEMANTIC
matching — resolving descriptions/paraphrases to entities, which string matching cannot do.**

## Corrected honest framing for the whole programme
- **Lexically inflated** (a dumb string matcher ties the geometry because entity NAMES are shared unique
  keys): named-entity retrieval/QA/grounding headline 1.00s — GEO-15 retrieval, GEO-16/17 hop-1, GEO-23.
  These demonstrate the PIPELINE works, not that geometry is necessary for them.
- **Genuinely geometric** (no lexical shortcut — the irreducible contribution): semantic/descriptive
  retrieval (GEO-25b 0.80 vs 0.10), analogy (GEO-5 0.88), relation-offset & few-shot (GEO-6 0.94–1.00),
  composition (GEO-1/7), the LLM-prior learning effect (GEO-24). THESE are where the LLM geometry earns its
  place. The symbolic-layer findings (GEO-18/20) and grounding/abstention (GEO-23) remain valid as
  ARCHITECTURE properties regardless of the lexical caveat.
