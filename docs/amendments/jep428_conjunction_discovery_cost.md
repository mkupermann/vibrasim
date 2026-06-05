# JEP-428 — Can unsupervised search DISCOVER the conjunctive feature, and at what cost?

## Motivation
JEP-427 located the wall: non-linear rules need the right conjunctive features, which must be DISCOVERED unsupervised.
This tests the obvious established method — exhaustive search over feature combinations — and quantifies its COST. The
honest expectation: brute-force pairwise search DISCOVERS the XOR pair for few features, but the search space grows
combinatorially (O(P^k)), so it is intractable for many features / higher-order interactions. This precisely
characterizes why a PRINCIPLED (non-brute-force) discovery mechanism is the open problem. Established method (exhaustive
feature-subset search), named; no claim of novelty. No transformer.

## Method
XOR stream (A=prop0, B=prop1, base rate 0.5, noise). Exhaustive pairwise search: for every pair (i,j) score how well
its 4 conjunctions separate good/bad valence; check whether the true pair (0,1) ranks #1. Then report the search-space
size for order k=2,3,4 across feature counts P=10,20,50,100 (the combinatorial cost).

## Pre-registered PREDICTION + bars (BEFORE the run)
- **J428a (discovery works small):** exhaustive pairwise search ranks the true pair (0,1) #1 by conjunction-separation,
  both seeds (0, 7).
- **J428b (cost explodes):** the search space C(P,k) grows combinatorially — report it; for k=3 at P=100 it is already
  ~1.6e5 and for k=4 ~3.9e6, i.e. exhaustive higher-order discovery is intractable at realistic scale.
- **J428c (the honest map):** brute-force discovers LOW-order conjunctions among FEW features, but there is no tractable
  exhaustive route to high-order interactions among many features — a principled discovery mechanism (the missing new
  math) is required.

Predicted: J428a PASS (small works), J428b confirms the explosion. Bars fixed; no retuning. No transformer.

## Result (seeds 0, 7): **PASS** (prediction HIT)
- **J428a (discovery works small): PASS** — exhaustive pairwise search ranks the true XOR pair (0,1) #1 with a clear
  margin (score 0.81 vs 2nd-best 0.09-0.12). Both seeds.
- **J428b (cost explodes): PASS** — search space C(P,k): P=10 → 45/120/210 (k=2/3/4); P=50 → 1.2k/19.6k/230k;
  P=100 → 4.95k/161.7k/**3.92M**. Combinatorial.
- **J428c (the honest map): confirmed** — brute-force discovers LOW-order conjunctions among FEW features, but
  high-order interactions among many features are intractable by exhaustive search.

## Verdict: **PASS — the missing math is a principled, non-brute-force feature-discovery mechanism**
Completing the JEP-426/427/428 frontier map: (426) a scalar energy/valence signal learns LINEAR rules cheaply;
(427) it is at chance on NON-LINEAR (XOR) rules, which need the right conjunctive features; (428) those features CAN be
found by exhaustive search for few features/low order, but the cost is COMBINATORIAL (C(P,k) → millions), so it does
not scale. The precise, quantified location of where new mathematics is needed: **a tractable, principled mechanism to
DISCOVER the right non-linear features/abstractions from experience — without brute-force search and without
supervision.** That is exactly one of the five open problems, now mapped with data, not asserted. Established methods
(subset search, perceptron limits), named; NOT new science. No transformer.
