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
