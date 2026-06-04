# GEO-36 — Reproducibility: do the irreducible-edge findings replicate on a DIFFERENT embedding model?

## Motivation
The whole programme used all-MiniLM-L6-v2. If the genuinely-geometric findings (semantic resolution, zero-
shot transfer) are real, they should REPLICATE on a different, architecturally-distinct embedding model
(all-mpnet-base-v2, 768-dim, MPNet). If they vanish, they were model-specific artifacts. This is a robustness
check on the programme's core claims.

## Pre-registration (locked BEFORE run)
- Re-run two cleanest rungs with all-mpnet-base-v2:
  (1) GEO-25b semantic descriptive retrieval (no shared token): geometric vs lexical.
  (2) GEO-27b zero-shot relational transfer to unseen entities: LLM-init vs random-init (unseen-vs-unseen).
- Bars (same as originals): (1) geometric >= 0.7 AND geometric - lexical >= 0.3; (2) LLM-init >= 0.75 AND
  >= random + 0.20. Report MiniLM vs MPNet side by side.
- PASS if both replicate on MPNet (findings model-robust). PARTIAL if one replicates. NULL if neither
  (findings were MiniLM-specific) — a valid, important finding either way.
