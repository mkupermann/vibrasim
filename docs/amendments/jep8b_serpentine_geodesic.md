# JEP-8b — serpentine maze: where Euclidean is genuinely deceptive (real geodesic test)

## Motivation
JEP-8 NULL: a weak barrier left the learned encoder mostly Euclidean. A serpentine (boustrophedon) maze makes
Euclidean strongly DECEPTIVE — cells in adjacent corridors are Euclidean-close but geodesically far (must travel
the whole snake). This is the genuine test of whether the LOCAL contrastive rule learns geodesic connectivity.

## Pre-registration (locked BEFORE run)
- Serpentine maze: vertical wall columns with alternating top/bottom gaps forcing a single snaking corridor.
- Encoder via local contrastive rule on walks over free cells (as JEP-8). Geodesic = BFS.
- Tests (same bars as JEP-8): (1) Spearman(emb, GEODESIC) >= 0.7 AND >= Spearman(emb, EUCLIDEAN) + 0.15;
  (2) energy-MPC LEARNED >= 0.7 AND >= EUCLIDEAN-control + 0.2 AND >> random. Here the Euclidean control SHOULD
  fail badly (it tries to go straight through walls).
- PASS = local learning captures geodesic structure where Euclidean is deceptive. NULL = even here it cannot.
