# JEP-17 — relational reasoning from the cognitive map: transitive inference

## Motivation
Bridge from sensorimotor navigation to ABSTRACT reasoning. The same SR / cognitive-map machinery (EQMOD-4)
should support TRANSITIVE INFERENCE: from only ADJACENT comparisons (1<2, 2<3, ...) infer NON-adjacent orders
(2<5) never observed together - the classic relational-reasoning paradigm hippocampal cognitive maps are known
to support (Stachenfeld 2017; Whittington TEM 2020). Mechanism: the diffusion geometry of the chain (SR /
Laplacian Fiedler vector) recovers the latent 1D ORDER from purely local transitions; non-adjacent inference =
compare recovered positions. This is "reasoning as navigation in a learned concept space."

## Pre-registration (locked BEFORE run)
- N items in a latent linear order; chain graph (i ~ i+1). Learn SR by LOCAL TD on random walks (only adjacent
  transitions occur). Recover 1D position from the SR/Laplacian Fiedler vector; orient sign by the KNOWN adjacent
  comparisons.
- Test transitive inference on ALL NON-adjacent pairs (never co-observed), including INTERNAL pairs (no endpoint
  anchor, the hardest).
- Bars: non-adjacent inference accuracy >= 0.9 AND internal-pair accuracy >= 0.8 (>> chance 0.5) AND the SYMBOLIC
  DISTANCE EFFECT is present (accuracy/margin increases with rank distance - the signature of genuine relational
  inference). PASS = the cognitive-map/SR machinery performs transitive inference from local observations. NULL
  otherwise. Methods (SR, spectral/Laplacian embedding, transitive inference) established - named as such.
