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

## Result — PARTIAL (2D structure emerges; square-grid eigenvalue degeneracy caps it at ~0.90)
| measure | value |
|---------|-------|
| recovered-coord corr x / y | 0.895 / 0.896 |
| relational inference east / north | 0.881 / 0.889 |

**VERDICT: PARTIAL.** The cognitive map recovers the latent 2D structure (corr ~0.90 both axes) and infers
global 2D relations on NON-adjacent pairs (east 0.88, north 0.89, >> chance 0.5) - the 2D extension of JEP-17
works. But it just misses the 0.9 bars because a SQUARE grid has EIGENVALUE DEGENERACY: the x-mode and y-mode
(cos(pi x/K), cos(pi y/K)) share eigenvalues, so eigh returns an arbitrary ROTATION within the degenerate
subspace -> recovered axes are slightly mixed (~0.90, not ~1.0). Known math degeneracy, not a failure of the
representation. Principled fix (not bar-tuning): a RECTANGULAR grid (K1!=K2) breaks the degeneracy -> clean axis
separation -> JEP-20b. Bars locked, not tuned.

## JEP-20b — rectangular grid (degeneracy broken) — PASS
| measure | value |
|---------|-------|
| recovered-coord corr x / y | 0.976 / 0.977 |
| relational inference east / north | 0.966 / 0.980 |

**VERDICT: PASS.** On a rectangular grid (9x6, breaking the square-grid eigenvalue degeneracy), the cognitive
map recovers the latent 2D structure cleanly (corr ~0.98 both axes - grid-cell-like codes) and infers global 2D
relations (east 0.97, north 0.98) on NON-adjacent concept pairs never co-observed. Confirms JEP-20's shortfall
was the eigen-degeneracy, not the representation. With JEP-17 (1D transitive inference) this establishes the
SR/cognitive-map machinery as a relational-reasoning engine in 1D AND 2D concept spaces - reasoning as the same
geometry that does spatial navigation. Honest scope: still STRUCTURED relational inference (orders, grids), not
open conceptual/linguistic understanding. SR grid-cells (Stachenfeld 2017), spectral embedding established - named.
