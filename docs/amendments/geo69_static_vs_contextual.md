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

## Result — DEFLATION (semantic matching is mostly DISTRIBUTIONAL, not transformer-specific)
| method | semantic hits@1 |
|--------|-----------------|
| contextual (full transformer) | 0.80 |
| static (mean-pooled word vectors, no transformer) | **0.70** |
| lexical | 0.10 |

**VERDICT: DEFLATION.** Mean-pooled STATIC word vectors (the model's word-embedding layer averaged, no
transformer blocks/attention) already resolve descriptions at 0.70 — close to the full contextual 0.80, far
above lexical 0.10. So the surviving "irreducibly geometric" value — SEMANTIC MATCHING — is mostly
DISTRIBUTIONAL SEMANTICS, a pre-transformer capability (word2vec/GloVe era, ~2013). The transformer/LLM adds
a MODEST contextual boost (+0.10), not the fundamental capability. (Caveat: static vectors here come from the
same transformer's embedding layer; true word2vec/GloVe may differ slightly, but the point holds — contextual
encoding is not NEEDED for most of it.) 15th self-correction.

## FINAL maximally-honest scoping (GEO-66 + GEO-68 + GEO-69)
Three rigorous deflations bottom out the inquiry into what the "geometric ML/LLM" approach genuinely
contributes:
- LEARNING relations = a linear probe (GEO-66).
- multi-hop COMPOSITION = a database join + entity resolution (GEO-68).
- SEMANTIC MATCHING itself = mostly distributional semantics, static word vectors do ~0.70 (GEO-69); the
  transformer adds a modest +0.10.
So the genuine, irreducible ingredient is DISTRIBUTIONAL SEMANTIC MATCHING (resolving meaning to entities) —
decades-old, modestly improved by the LLM's contextual encoding — composed with entirely classical machinery
(database joins, set-logic operators, linear probes, RAG grounding, a thin generator). Honest final answer:
the system is a clean, useful, deployable SYNTHESIS of established methods; its one genuinely-valuable
ingredient (distributional semantic matching) is old, not novel, and only modestly LLM-enhanced. No part is
new-as-method; the value is the honest engineering synthesis + the precise boundary map. This is the deepest
honest characterization the programme can give.
