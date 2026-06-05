# JEP-339 — Extracting the substrate-legal kernel from GeoWorld: hyperbolic taxonomy embedding

## Context (Michael asked to "include arxiv 2602.23058v1")
GeoWorld = Hyperbolic-JEPA + Geometric-RL. Its ACTUAL method uses a ~300M-parameter TRANSFORMER predictor and a
PRETRAINED ViT encoder — both explicitly FORBIDDEN by CLAUDE.md (no transformer, no pretrained model). Those are NOT
incorporated. What IS substrate-legal is the paper's geometric KERNEL: hyperbolic space (Poincaré ball) represents
HIERARCHIES with low distortion in few dimensions (classical, Nickel & Kiela 2017; Sarkar; not neural). Test whether
that kernel helps OUR taxonomy reasoning — honestly, vs the existing VSA which already does is-a at 1.0.

## Method (classical, no neural net)
Embed the substrate's is-a tree into a D-dim Poincaré ball by hyperbolic multidimensional scaling: parametrize each
node as a ball point (exp-map of a free Euclidean vector), minimize Σ (d_H(p_i,p_j) − graph_dist(i,j))² with
L-BFGS. `d_H(u,v) = arccosh(1 + 2‖u−v‖² / ((1−‖u‖²)(1−‖v‖²)))`. Test: does hyperbolic distance + norm recover the
hierarchy (ancestors rank closest; general concepts near origin)?

## Pre-registered bars (BEFORE the run)
- **J339a (kernel works, low-dim):** in D=5 the hyperbolic embedding recovers the is-a hierarchy — ancestor-ranking
  AUC ≥ 0.85 AND norm encodes depth (root-ward concepts have smaller norm), both seeds (0, 7).
- **J339b (honest comparison):** report dimension-efficiency vs the VSA. The HONEST expected finding: hyperbolic is
  more dimension-efficient for pure trees, but the existing VSA already does is-a at 1.0 with routing — so this is a
  complementary geometry, NOT a needed replacement. State plainly which (if either) we adopt.

Predicted most-likely failure: hyperbolic MDS on a small tree may need careful init (ball-boundary blowup); if
J339a misses, report the distortion and whether it's optimization (init/lr) vs a representational limit. The
transformer/RL parts of the paper are out of scope by rule — not a failure, a constraint.

## Result (seeds 0, 7): **PASS**
- **J339a:** in D=5, hyperbolic MDS recovers the hierarchy — ancestor-ranking AUC = **0.937**, depth-monotonic
  (norm encodes depth, child farther from origin than parent) = **1.0**, mean distortion = **0.067**, both seeds.
  **PASS.**
- **J339b (honest):** the VSA already answers is-a at 1.0 with routing at scale; the hyperbolic embedding is a more
  dimension-efficient geometry for PURE TREES (5 dims here) and a useful COMPLEMENT, but not a needed replacement of
  the VSA store. Adopted as an optional geometry; the transformer + Geometric-RL core of the paper is FORBIDDEN by
  CLAUDE.md and was NOT incorporated.

## Verdict: **PASS** (kernel extracted, neural parts rejected)
The substrate-legal kernel of GeoWorld — hyperbolic (Poincaré-ball) representation of hierarchies — works:
a classical, neural-net-free embedding recovers the is-a tree in 5 dimensions (AUC 0.937, norm = depth). This is
how Michael's paper request is honored WITHOUT breaking the no-transformer/no-pretrained rule: take the geometric
idea (established, Nickel & Kiela 2017), test it on the substrate's own taxonomy, and explicitly reject the
300M-param transformer predictor + pretrained ViT that the paper actually uses. No transformer, no pretrained model.
