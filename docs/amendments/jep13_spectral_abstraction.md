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

## Result — PARTIAL (abstraction holds for REPRESENTATION; greedy control brittle)
| measure | PVF basis | random basis | true-SR ref |
|---------|-----------|--------------|-------------|
| reconstruction R^2 (novel goals) | 0.979 | 0.176 | 1.00 |
| greedy-planning reached | 0.30 | 0.07 | 1.00 |

**VERDICT: PARTIAL.** The abstraction claim holds strongly at the REPRESENTATION level: a compact task-agnostic
basis (k=S/4=36 proto-value functions, learned with NO goal info) reconstructs arbitrary novel-goal value
functions at R^2=0.98, vs 0.18 for a random basis of equal size. So the environment's structure compresses into
a small reusable basis that COMPOSES to novel goals. BUT greedy 1-step planning on the reconstructed value
reaches only 0.30: the classic value-approximation-vs-control gap - a ~2% reconstruction error creates local
maxima that trap greedy control (true-SR is monotone -> 1.00). The fix is MPC LOOKAHEAD (multi-step), robust to
approximate value -> JEP-13b. Bars locked, not tuned.

## JEP-13b — MPC lookahead — PARTIAL (helps, doesn't close it)
MPC lookahead (depth 6) on the PVF-approx value reached 0.47 (vs greedy 0.30, random-basis 0.26, true-SR 1.00).
Lookahead helps but the compact basis's residual error creates value local-maxima wider than depth-6 search.
Not forcing higher by tuning depth/k. The real story is a COMPRESSION-vs-CONTROL tradeoff -> JEP-13c maps it.

## JEP-13c (pre-reg) — characterize the compression-vs-control tradeoff
- Sweep basis size k in {S/8, S/4, S/2, 3S/4, S}. For each: PVF reconstruction R^2 + greedy-planning reach on
  novel goals. Expect R^2 high even at small k; reach to increase with k toward 1.00 at k=S.
- Report the curve (no single PASS bar - this is characterization). Finding = WHERE control becomes reliable
  (reach>=0.9) and whether that k still gives meaningful compression (k<S).
