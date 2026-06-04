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

## Result — NULL (a genuine limit of the simple contrastive rule)
| measure | value |
|---------|-------|
| Spearman(emb-dist, GEODESIC) | 0.50 |
| Spearman(emb-dist, EUCLIDEAN) | 0.58 |
| Spearman(GEODESIC, EUCLIDEAN) ref | 0.72 |
| energy-MPC LEARNED | 0.34 |
| energy-MPC EUCLIDEAN control | 0.28 |
| random | 0.19 |

**VERDICT: NULL — a genuine limit.** Even in a serpentine where Euclidean is deceptive, the simple contrastive
temporal-coherence rule's embedding tracks EUCLIDEAN (0.58) over geodesic (0.50) and barely beats the Euclidean
control (0.34 vs 0.28). So the pairwise attract-neighbours/repel-randoms rule converges to a positional metric,
NOT the maze topology. This bounds the JEP-5/7 representation: it is metric/positional, not geodesic. The
established fix is the SUCCESSOR REPRESENTATION (Dayan 1993) — captures multi-step diffusion/connectivity and is
learnable by a LOCAL TD rule (still substrate-compatible). That is the right next direction (JEP-9). NULL is a
finding; bars locked, not tuned.
