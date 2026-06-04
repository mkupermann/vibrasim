# JEP-13 — spectral abstraction: a compact task-agnostic basis that COMPOSES to novel goals

## Motivation
From navigation toward ABSTRACTION. The eigenvectors of the world model's graph (Laplacian eigenvectors =
proto-value functions, Mahadevan & Maggioni 2007) form a compact, TASK-AGNOSTIC basis learned WITHOUT knowing
any goal. Claim: a small basis (k << S) can REPRESENT the value function of ANY novel goal as a linear
combination -> the agent abstracts the environment's structure once and composes it to solve new tasks. The
eigenbasis is Hebbian-learnable (Oja's rule = local), so it stays substrate-relevant.

## Pre-registration (locked BEFORE run)
- Maze (DFS tree). Build adjacency A, graph Laplacian L; take the k SMOOTHEST eigenvectors (smallest eigenvalues)
  = proto-value functions (PVFs). These are computed with NO goal information (task-agnostic).
- For N=40 NOVEL random goals: true goal value V_g = SR column M[:,g] (geodesic value). Project onto the k PVFs:
  V_hat = sum_i (V_g . e_i) e_i. Measure reconstruction R^2. Then PLAN greedily on V_hat (pick neighbour with
  higher V_hat); measure goal-reaching.
- Controls: k RANDOM orthonormal basis vectors (same dimensionality, no structure).
- Bars (k = ceil(S/4)): PVF reconstruction R^2 >= 0.9 AND PVF planning reached >= 0.9 AND PVF >> random-basis
  (R^2 and planning). PASS = a compact learned basis abstracts the environment and composes to novel goals.
  NULL otherwise. Proto-value functions / spectral RL (Mahadevan 2007) established - named as such.
