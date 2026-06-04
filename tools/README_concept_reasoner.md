# ConceptReasoner — mixed-curvature concept reasoning (EQMOD-4)

A small, dependency-light tool that builds a **dual-geometry embedding** of a taxonomy and answers two kinds of
question about concepts:

- **relatedness** ("how related are X and Y?") — from a **Euclidean** embedding
- **IS-A / hypernymy** ("is X a kind of Y?", "which is more general?") — from a **hyperbolic** (Poincaré) embedding

No pretrained models, no transformer — just two geometry fits over a taxonomy graph. Built from the EQMOD-4
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

**Compute scales super-linearly with hierarchy size/depth.** For larger/deeper taxonomies, raise `hyp_dim` and
`iters` substantially (a GPU helps — see `docs/AMD_GPU_COMPUTE.md`). The norm-based IS-A readout degrades on very
deep hierarchies.

**Also:** `is_a` checks only the necessary *generality* condition (b more general than a). Per-query accuracy is
~0.86–0.91 on small/medium taxonomies, so a minority of queries are wrong — do NOT treat it as exact. Aggregate
held-out accuracy is the honest metric; cherry-picked easy queries can pass while the aggregate degrades
(JEP-29 lesson).

**Compositional queries** (lowest common ancestor / "what category includes both X and Y") work *partially*
(~0.6–0.8, JEP-30c) and improve with embedding dimension — a genuine but bounded step beyond pairwise IS-A.

## What it is and isn't
It is a faithful, honestly-bounded demonstration that **mixed-curvature cognitive maps** capture both metric and
taxonomic concept structure, shipped as a usable tool. All methods are established (Poincaré embeddings —
Nickel & Kiela 2017; successor-representation grid cells — Stachenfeld 2017; product manifolds — Gu et al. 2019)
and named as such. It is **not** human-level conceptual understanding and claims no novelty.

Tests: `pytest tests/test_concept_reasoner.py`.
