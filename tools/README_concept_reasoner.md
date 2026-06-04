# ConceptReasoner — mixed-curvature concept reasoning (EQMOD-4)

A small, dependency-light tool that builds a **dual-geometry embedding** of a taxonomy and answers two kinds of
question about concepts:

- **relatedness** ("how related are X and Y?") — from a **Euclidean** embedding
- **IS-A / hypernymy** ("is X a kind of Y?", "which is more general?") — from a **hyperbolic** (Poincaré) embedding

Handles multi-parent (DAG) taxonomies (JEP-51: `_ancestors` is the transitive closure over all
parents). No pretrained models, no transformer — just two geometry fits over a taxonomy graph. Built from the EQMOD-4
geometry findings (different relation types want different curvature: metric→Euclidean, taxonomic→hyperbolic).

## Why two geometries?
A single Euclidean space captures *relatedness* well but has no notion of *generality* (JEP-26: Euclidean IS-A
direction was 0.39, **below chance**). Hyperbolic space encodes generality in its **radial** axis (general
concepts near the origin, specific near the boundary), so hypernymy reads off the geometry. Each geometry
captures what the other misses (JEP-26/27).

## Usage
```python
from tools.concept_reasoner import ConceptReasoner

# taxonomy as parent -> [children]
tax = {
    "animal": ["mammal", "bird"],
    "mammal": ["carnivore", "primate"],
    "carnivore": ["cat", "dog"],
    "primate": ["human", "chimp"],
}
cr = ConceptReasoner(tax)
cr.fit(euc_dim=4, hyp_dim=8, iters=3000)   # use hyp_dim >= 5 (2D is unreliable per-query)

cr.is_a("cat", "mammal")          # True   (a cat is a kind of mammal)
cr.is_a("mammal", "cat")          # False
cr.more_general("cat", "mammal")  # "mammal"
cr.nearest("cat", k=3)            # taxonomic neighbours (siblings / parent class)
cr.relatedness("cat", "dog")      # higher = more related
```

## Honest bounds (read before relying on it)
Validated, with limits, across EQMOD-4 (see `docs/amendments/jep28*.md`, `jep29*.md`, `jep31*.md`):

| taxonomy | held-out IS-A accuracy | notes |
|----------|------------------------|-------|
| 77 concepts (curated) | 0.91 | reliable at `hyp_dim >= 5`; **2D is NOT reliable** per-query |
| 366 concepts (WordNet carnivore) | 0.86 | needs ~`hyp_dim=20`, ~12k full-batch iters |
| 1170 concepts (WordNet mammal) | 0.53 → 0.65 | **under-converged** at the budget tried; not reliable |

**Held-out generalization needs SCALE (JEP-51):** the reasoner answers is_a for relations IN its fitted
taxonomy reliably (in-sample recall ~1.0). But generalizing to UNSEEN is_a relations (held-out link prediction)
is WEAK only on VERY SMALL taxonomies (<~50 concepts: ~0.4 recall); at >=50 concepts it generalizes reasonably
(balanced ~0.85, recall ~0.73, JEP-52). The calibrated is_a is conservative (high precision, ~0.73 recall) - good
for grounding. The "0.91 generalization" figure (JEP-28b) was the norm-DIRECTION metric (which-is-more-general,
given a known pair) on a larger taxonomy, not calibrated is_a recall on a small one. Use it as a lookup over a
KNOWN taxonomy; do not expect strong unseen-relation prediction on small inputs.

**Compute scales super-linearly with hierarchy size/depth.** For larger/deeper taxonomies, raise `hyp_dim` and
`iters` substantially (a GPU helps — see `docs/AMD_GPU_COMPUTE.md`). The norm-based IS-A readout degrades on very
deep hierarchies.

**`is_a` is a calibrated classifier** (JEP-32): generality (norm gap) + containment (hyperbolic distance), so it
correctly rejects general concepts in *other* branches (`is_a(oak, mammal)=False`). Classification accuracy ~0.96
on small taxonomies. KNOWN residual: same-depth **siblings** (`is_a(cat, dog)`) can be false-positive (TNR ~0.92) —
small distance + ~0 norm gap sit near the decision boundary. Aggregate accuracy is the honest metric; cherry-picked
easy queries can pass while the aggregate degrades (JEP-29 lesson).

**Compositional queries** (lowest common ancestor / "what category includes both X and Y") work *partially*
(~0.6–0.8, JEP-30c) and improve with embedding dimension — a genuine but bounded step beyond pairwise IS-A.


## Choosing the IS-A method (JEP-39..45)
`fit(isa_method=...)` selects how IS-A is computed - no single method is best (mapped tradeoffs):
- `"poincare"` (default): calibrated hyperbolic. Cross-branch correct; SIBLING residual (`is_a(cat,dog)` can be
  wrong); ~0.78 ceiling on deep real WordNet (the limit is the METHOD, not compute/dimension - JEP-40/41).
- `"order"` (recommended for LARGE REAL hierarchies): order embeddings (Vendrov 2016). Fixes siblings AND scales
  to ~0.91 held-out IS-A on WordNet (366 concepts); small cross-branch residual (a specific concept can dominate
  an unrelated general one). 
- Entailment cones (Ganea 2018, `tools/run_jep39*`): fix BOTH residuals on small/clean taxonomies (1.00) but do
  NOT scale (TPR 0.42 at 366). Best for small clean trees.

**Choose by USE CASE, not just aggregate accuracy (JEP-46 - important):** higher benchmark accuracy can mean
WORSE task performance when error types differ.
- **Raw is-a classification / hypernym lookup** on a large hierarchy -> `"order"` (0.91 vs 0.78).
- **GROUNDING / planning** ("which entities are-a category X") -> `"poincare"` (DEFAULT). Grounding needs
  precision against CROSS-BRANCH confusions; order embeddings' cross-branch false-positives ground wrong
  entities (a canine grounded as a feline), which made an integrated agent WORSE (0.50 vs poincare 0.79, JEP-46).
  Poincare's errors are siblings, which don't arise in entity-vs-category grounding.
The error PATTERN, not aggregate accuracy, predicts downstream utility - measure on YOUR task.

## What it is and isn't
It is a faithful, honestly-bounded demonstration that **mixed-curvature cognitive maps** capture both metric and
taxonomic concept structure, shipped as a usable tool. All methods are established (Poincaré embeddings —
Nickel & Kiela 2017; successor-representation grid cells — Stachenfeld 2017; product manifolds — Gu et al. 2019)
and named as such. It is **not** human-level conceptual understanding and claims no novelty.

Tests: `pytest tests/test_concept_reasoner.py`.
