# JEP-8 — does the locally-learned encoder capture GEODESIC (maze) structure? rigorous test of JEP-7

## Motivation
JEP-7 planned at 0.97 but with a low-accuracy predictor — the contrastive encoder did much of the work. This
asks the sharp question: did the LOCAL contrastive rule learn the task's true CONNECTIVITY (geodesic / shortest-
path structure), or merely Euclidean position? Test in a MAZE with walls, where Euclidean distance is deceptive
(a wall between start and goal) and only an encoder that learned the maze topology can navigate.

## Pre-registration (locked BEFORE run)
- 8x8 grid with interior WALL cells forming a barrier with a gap. Movement into a wall = stay. Free-cell graph;
  geodesic distance = BFS on free cells.
- Encoder learned by the LOCAL contrastive temporal-coherence rule on random walks over FREE cells (walls are
  never traversed, so temporal adjacency = geodesic adjacency).
- Tests:
  (1) Spearman(embedding-distance, GEODESIC-distance) vs Spearman(embedding-distance, EUCLIDEAN-distance).
      Bar: geodesic correlation >= 0.7 AND geodesic > euclidean by >= 0.15 (encoder tracks connectivity, not
      raw position).
  (2) Energy-MPC goal-reaching in the maze with the LEARNED encoder vs a EUCLIDEAN-coords encoder control vs
      random. Bar: learned >= 0.7 reached AND learned >= euclidean-control + 0.2 AND >> random.
- PASS = the local rule learned geodesic/topological structure that enables maze navigation where Euclidean
  position fails. NULL otherwise. Methods (contrastive/slow-feature learning, BFS, EBM/MPC) established, named.

## Result — NULL (honest deflation of JEP-7)
| measure | value |
|---------|-------|
| Spearman(emb-dist, GEODESIC) | 0.73 |
| Spearman(emb-dist, EUCLIDEAN) | 0.80 |
| energy-MPC reached, LEARNED encoder | 0.66 |
| energy-MPC reached, EUCLIDEAN control | 0.60 |
| random | 0.20 |

**VERDICT: NULL.** The learned embedding tracks EUCLIDEAN (0.80) MORE than geodesic (0.73), and barely beats
the Euclidean-coords control at navigation (0.66 vs 0.60). With only a small barrier most cell-pairs have
geodesic ~ Euclidean, so the contrastive rule converged to a roughly POSITIONAL embedding. Honest implication:
JEP-7's planning success was largely EUCLIDEAN gradient-following, NOT deep topological world-modeling. To test
whether local learning can capture genuine geodesic structure, the maze must make Euclidean DECEPTIVE for many
pairs (serpentine) -> JEP-8b. This NULL is a finding, not a retry; bars locked, not tuned.
