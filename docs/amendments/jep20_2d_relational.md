# JEP-20 — 2D relational inference from the cognitive map (grid-cell structure)

## Motivation
JEP-17 showed 1D transitive inference. Real relational reasoning needs richer structure. A latent 2D
arrangement of concepts, observed only via LOCAL neighbor relations, should be recoverable by the SR/cognitive
map: the two leading non-trivial Laplacian eigenvectors of a 2D grid ARE the 2D coordinates (grid-cell-like
codes, Stachenfeld 2017). This enables inferring GLOBAL 2D relationships (relative direction) for concept pairs
never co-observed - 2D relational generalization from local structure.

## Pre-registration (locked BEFORE run)
- Concepts on a latent KxK 2D grid; only local N/S/E/W adjacency observed (random walk). Learn SR by LOCAL TD.
- Recover 2D coordinates from the 2 leading non-trivial eigenvectors of the SR's symmetric part; align to true
  axes (Procrustes/sign+swap by correlation).
- Tests: (1) recovered-coord vs true-coord correlation >= 0.9 on BOTH axes; (2) relational inference - for
  NON-adjacent concept pairs, predict relative direction (is A east-of / north-of B) from recovered coords;
  accuracy >= 0.9.
- PASS = the cognitive map recovers 2D structure and infers global 2D relations from local observations. NULL
  otherwise. SR/grid-cell (Stachenfeld 2017), spectral embedding - established, named as such.
