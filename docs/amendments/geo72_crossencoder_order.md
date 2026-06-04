# GEO-72 — Does a cross-encoder fix the word-order/compositional weakness?

## Motivation
GEO-71: mean-pooled bi-encoders are weak at word order (0.62-0.75), and it doesn't scale with size. The
prescribed fix (GEO-71) is a CROSS-ENCODER (jointly encodes query+fact, so it SEES word order). GEO-72 tests
whether the cross-encoder re-ranker resolves the compositional weakness on the clean 2-way order items.

## Pre-registration (locked BEFORE run)
- GEO-70b clean 2-way identical-bag word-order items.
- For each: cross-encoder scores (query, factA) vs (query, factB), pick higher.
- Compare to the bi-encoder baseline (0.75 MiniLM).
- Bar: cross-encoder >= 0.85 AND > bi-encoder. PASS validates the design rule (cross-encoder for
  role/word-order matching). NULL if it doesn't help.

## Result — PASS
| method | word-order 2-way acc |
|--------|----------------------|
| bi-encoder (pooled) | 0.75 |
| cross-encoder (joint) | **0.88** |

**VERDICT: PASS.** The cross-encoder improves word-order/role matching from 0.75 to 0.88 — joint query+fact
encoding sees word order where pooled bi-encoders cannot. Validates the GEO-71 design rule. 0.88 is good-not-
perfect (role-sensitivity is genuinely hard), but clearly better.

## Compositional-matching story — COMPLETE (GEO-70b/71/72)
- The transformer adds compositional signal over static word vectors (GEO-70b, 0.75 vs 0.38).
- But pooled BI-ENCODERS are weak at it and it does NOT scale with model size (GEO-71, MiniLM 0.75 > mpnet 0.62).
- A CROSS-ENCODER fixes it substantially (GEO-72, 0.75 -> 0.88) — and the system ALREADY ships this via
  rerank_k (GEO-40b). So: enable re-ranking for role/word-order-sensitive matching; the system handles it.
The honest net: the LLM's compositional contribution is real but accessed best through joint (cross-encoder)
scoring, not pooled bi-encoder embeddings — a concrete, actionable design rule, with the fix built in.
