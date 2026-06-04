# JEP-30 — compositional category query: lowest-common-ancestor from the hyperbolic embedding

## Motivation
Beyond pairwise IS-A: a COMPOSITIONAL query combining two concepts - "what category includes BOTH X and Y" =
their lowest common ancestor (LCA). Read it GEOMETRICALLY from the hyperbolic embedding (the most-specific
more-general node closest to both), not from the tree. Tests a step toward compositional conceptual reasoning.

## Pre-registration (locked BEFORE run)
- 77-concept toy taxonomy; hyperbolic 10D. For random concept pairs, predict LCA = argmin over nodes C with
  norm <= min(norm A, norm B) of d_hyp(C,A)+d_hyp(C,B). Compare to true LCA (deepest common ancestor in the tree).
- Bars: exact-LCA accuracy >= 0.6 AND predicted-is-a-common-ancestor >= 0.85. PASS = the embedding supports
  compositional category queries from geometry. NULL otherwise. Established (hyperbolic embeddings), named.

## Result — NULL (geometric-readout BUG, not embedding failure)
exact-LCA 0.099, common-ancestor 0.099. Examples show it predicted ONE OF THE INPUTS as the LCA
(mammal,duck -> predicted mammal; finch,bamboo -> predicted finch). Cause: the candidate constraint
norm[C] <= min(norm[A],norm[B]) ALLOWED the more-general input itself (which has distance 0 to itself), so
argmin(d(C,A)+d(C,B)) picked it. Fix: candidates must be STRICTLY more general than BOTH inputs (norm strictly
smaller) and exclude the inputs -> JEP-30b. Embedding likely fine; the readout was wrong. Bars locked.

## JEP-30b — fixed readout — PARTIAL (works for same-subtree, embedding distortion hurts distant pairs)
exact-LCA 0.549, common-ancestor 0.747. 4/6 examples correct (mammal/duck->vertebrate, beetle/ant->insect, etc).
Errors (tick/raptor->bird, rat/tuna->fish) are distant-branch pairs where the predicted node is an ancestor of
ONLY ONE input. The readout is PRINCIPLED (in a tree the LCA minimizes d(C,A)+d(C,B) since the A-B path passes
through it), so the residual errors are EMBEDDING DISTORTION (hyperbolic distances not perfectly tree-additive),
predicting a better embedding should help -> JEP-30c (20D, more iters). Bars locked.

## JEP-30c — better embedding (20D) — PARTIAL (capability there, improves with quality, common-ancestor just under bar)
| metric | 10D (JEP-30b) | 20D (JEP-30c) | bar |
|--------|---------------|---------------|-----|
| exact-LCA | 0.549 | 0.630 | 0.60 (MET) |
| common-ancestor | 0.747 | 0.807 | 0.85 (missed by 0.043) |

**VERDICT: PARTIAL - compositional LCA partially works; confirms embedding quality was the limiter.** Doubling
hyperbolic dimension (10D->20D) lifted exact-LCA 0.55->0.63 (now meets the 0.6 bar) and common-ancestor 0.75->0.81
(still 0.043 under 0.85). So the hyperbolic embedding DOES support compositional category queries ("what category
includes both X and Y") read from geometry, and accuracy tracks embedding quality - but it is not yet reliable
enough for the full pre-registered bar. NOT chasing more dims (bar-chasing). Honest conclusion: compositional LCA
is a genuine but BOUNDED capability of the concept reasoner - it combines two concepts geometrically at ~0.6-0.8
accuracy, a real step beyond pairwise IS-A toward compositional reasoning, honestly bounded. Established methods
(hyperbolic embeddings), named as such. Bars locked, not tuned.

## Compositional thread conclusion
The concept reasoner supports: pairwise IS-A (reliable, JEP-28b/29b) and compositional LCA / common-category
queries (PARTIAL, ~0.6-0.8, JEP-30c). Combining concepts geometrically works but is embedding-quality-limited.
A real step toward compositional conceptual reasoning, not a finished one - honestly bounded.
