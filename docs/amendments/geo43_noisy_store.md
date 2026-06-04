# GEO-43 — Robustness to a NOISY real-world store (paraphrase, typos, near-duplicate entities)

## Motivation
Every prior test used clean, templated facts. Real knowledge stores are messy: facts phrased inconsistently,
typos, and near-duplicate entity names ("Jon Smith" vs "John Smith"). GEO-43 tests whether the geometric
retrieval/reasoning degrades gracefully under realistic noise — a deployability question.

## Pre-registration (locked BEFORE run)
- 15 person->city facts. Build a NOISY variant: each fact randomly paraphrased (varied templates) + ~10%
  character typos; entity names include near-duplicates (add 5 distractor people with names 1-2 edits from
  real ones, with different cities).
- Query with the CANONICAL question; measure 1-hop retrieval accuracy on CLEAN vs NOISY store.
- Also: near-duplicate confusion rate (does a query for "John Smith" wrongly return "Jon Smith"'s fact?).
- Bars (characterization): report clean vs noisy accuracy + confusion rate. Flag if noisy drops > 0.2 below
  clean (fragile) or holds within 0.1 (robust). Honest either way; no pass/fail tuning.

## Result — FRAGILE (major honest deployability caveat)
| store | 1-hop accuracy |
|-------|----------------|
| clean | 1.00 |
| noisy (paraphrase + typos + 5 near-dups) | **0.53** |
| near-duplicate confusion rate | **0.33** |

**VERDICT: FRAGILE.** Realistic noise drops accuracy from 1.00 to 0.53. A THIRD of queries return a NEAR-
DUPLICATE entity's fact ("John Smith" -> "Jon Smith"ّs city), because embedding similarity cannot distinguish
near-identical names. **This is the programme's most important deployability caveat: the clean-store 1.00s
are optimistic — messy real data with near-duplicate entities degrades badly.** Mitigation: entity
NORMALIZATION / exact-key identity matching (not pure embedding retrieval) for entity resolution; embeddings
for relevance, exact IDs for identity. Diagnostic split (paraphrase/typo vs near-dup) in GEO-43b to locate
the dominant cause.

## GEO-43b — noise-source split (refines the diagnosis)
| noise source (isolated) | 1-hop |
|-------------------------|-------|
| paraphrase + typos only | 0.73 |
| near-duplicates only (clean facts) | **1.00** (confusion 0.00) |

**Refined honest diagnosis.** Near-duplicate entities with CLEAN text cause ZERO confusion — embeddings
distinguish "John Smith lives in X" from "Jon Smith lives in Y" perfectly. Paraphrase the embeddings also
handle (a STRENGTH, GEO-15). The real culprit is CHARACTER-LEVEL TYPOS (0.27 loss at 10% typo rate), and the
SEVERE combined case (GEO-43, 0.53) is the INTERACTION: a typo'd name drifts toward a near-duplicate's clean
fact. So the deployability lesson is precise: **embeddings are robust to paraphrase, fragile to typos, and
typos x near-duplicate entities compound badly.** Mitigation: spell/character normalization + EXACT entity-ID
resolution for identity (embeddings for relevance, exact keys for who-is-who). The clean-store 1.00s assume
clean text + disambiguated entities — realistic deployments need a normalization/entity-resolution front-end.
