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
