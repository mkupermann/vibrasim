# GEO-69 — Does semantic matching need the TRANSFORMER, or would static word vectors do?

## Motivation
GEO-66/68 narrowed the irreducible value to SEMANTIC MATCHING. The deepest deflation: is that from the
TRANSFORMER (contextual encoding), or would classic STATIC word vectors (mean-pooled, pre-transformer
distributional semantics) resolve descriptions too? If static works, semantic matching is a 2013-era
capability, not an LLM/transformer one. If only the full model works, the transformer's contextualization is
genuinely needed.

## Pre-registration (locked BEFORE run)
- Re-run GEO-25b (descriptive queries, no shared token) with: (a) full contextual sentence-transformer
  (all-MiniLM-L6-v2); (b) STATIC = mean-pooled token embeddings from the SAME model's word-embedding layer
  (no transformer blocks, no attention).
- Metric: semantic hits@1 (vs lexical 0.10). Bars (descriptive): if static >= 0.6, semantic matching does NOT
  need the transformer (distributional). If static ~ chance and contextual >> static, the transformer is
  needed. Honest either way.
