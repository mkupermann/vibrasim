# GEO-67 — Minimum viable embedding model for the irreducibly-geometric capability (semantic retrieval)

## Motivation
GEO-66 narrowed the genuine geometric value to TRAINING-FREE semantic retrieval/analogy/composition. GEO-36
showed bigger (mpnet) is better. The reverse question (efficiency floor): does a TINY 3-layer model still do
SEMANTIC description-retrieval (GEO-25b)? Tells the user the cheapest deployable model — and whether the
capability needs model scale or works on a minimal embedder.

## Pre-registration (locked BEFORE run)
- Re-run GEO-25b (descriptive queries, no shared token) on three models: paraphrase-MiniLM-L3-v2 (~17M),
  all-MiniLM-L6-v2 (~22M, default), all-mpnet-base-v2 (~110M).
- Metric: semantic retrieval hits@1 (vs lexical 0.10). Report the model-size vs accuracy curve.
- Characterization. Flag the smallest model that still beats lexical decisively (>=0.6). The curve is the finding.

## Result — efficiency floor is LOW (~17M)
| model | size | semantic hits@1 |
|-------|------|-----------------|
| paraphrase-MiniLM-L3-v2 | ~17M / 3-layer | 0.80 |
| all-MiniLM-L6-v2 (default) | ~22M / 6-layer | 0.80 |
| all-mpnet-base-v2 | ~110M / 12-layer | **1.00** |
| (lexical baseline) | — | 0.10 |

**FINDING.** Semantic description-retrieval works on a TINY 17M 3-layer model (0.80, same as the 22M default),
far above lexical (0.10). Model size buys accuracy (mpnet 1.00) but the capability is present even on a minimal
embedder. **Efficiency floor ~17M** — deployable on very modest hardware. Guidance: L3/L6 (~20M) for
speed/footprint at 0.80; mpnet (110M) for accuracy at 1.00. The genuinely-geometric value (semantic matching)
does not require model scale — it is a property of even small distributional-semantic embeddings, sharpening
GEO-66's point that the value is the EMBEDDINGS (any decent semantic embedder), not a special framing.
