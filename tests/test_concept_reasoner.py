"""Tests for the EQMOD-4 mixed-curvature ConceptReasoner (JEP-28). Fast slice.

Protects the reusable deliverable: relatedness (Euclidean) + IS-A (hyperbolic) over a taxonomy.
Honest bounds (per docs/amendments/jep28_concept_reasoner.md): per-query IS-A is reliable at >= 5D,
NOT at 2D; aggregate held-out IS-A generalization >= ~0.85 at >= 5D on small taxonomies.
"""
import numpy as np
import pytest

from tools.concept_reasoner import ConceptReasoner

TAX = {
    "animal": ["mammal", "bird"],
    "mammal": ["carnivore", "primate"],
    "carnivore": ["cat", "dog", "wolf"],
    "primate": ["human", "chimp"],
    "bird": ["eagle", "sparrow"],
}


def _fit(hyp_dim=8, iters=2500, holdout=None):
    cr = ConceptReasoner(TAX)
    cr.fit(euc_dim=4, hyp_dim=hyp_dim, iters=iters, holdout_pairs=holdout)
    return cr


def test_is_a_basic_correct():
    cr = _fit()
    # a cat is a carnivore / mammal / animal; a mammal is NOT a cat
    assert cr.is_a("cat", "carnivore")
    assert cr.is_a("cat", "mammal")
    assert cr.is_a("cat", "animal")
    assert not cr.is_a("mammal", "cat")
    assert not cr.is_a("animal", "cat")


def test_is_a_rejects_cross_branch():
    # JEP-32 fix: is_a must require CONTAINMENT, not just generality - a general concept in
    # a DIFFERENT branch is not an ancestor (the old generality-only check got these wrong).
    tax2 = {"living_thing": ["animal", "plant"], "animal": ["mammal"], "mammal": ["cat", "dog"],
            "plant": ["tree"], "tree": ["oak", "pine"]}
    cr = ConceptReasoner(tax2); cr.fit(euc_dim=4, hyp_dim=10, iters=3000)
    assert cr.is_a("cat", "mammal")          # true ancestor
    assert cr.is_a("cat", "animal")          # true ancestor (transitive)
    assert not cr.is_a("oak", "mammal")      # cross-branch general concept - must be rejected
    assert not cr.is_a("cat", "plant")       # cross-branch
    # NOTE: siblings (is_a('cat','dog')) are a known residual weakness (JEP-32), not asserted here.


def test_more_general_direction():
    cr = _fit()
    assert cr.more_general("cat", "mammal") == "mammal"
    assert cr.more_general("animal", "carnivore") == "animal"


def test_relatedness_nearest_is_taxonomic():
    cr = _fit()
    near = cr.nearest("cat", k=3)
    # cat's nearest should include its siblings (dog/wolf) or its parent class, not e.g. eagle
    assert any(n in {"dog", "wolf", "carnivore"} for n in near)


def test_heldout_is_a_generalizes():
    cr0 = ConceptReasoner(TAX)
    ALL = [(u, v) for v in range(cr0.N) for u in cr0._ancestors(v)]
    rng = np.random.default_rng(0)
    idx = rng.permutation(len(ALL))
    cut = max(1, int(0.25 * len(ALL)))
    holdout = set(ALL[i] for i in idx[:cut])
    cr = _fit(holdout=holdout)
    acc = np.mean([cr.hnorm[u] < cr.hnorm[v] for (u, v) in holdout])
    # held-out IS-A direction should generalize well above chance (0.5)
    assert acc >= 0.7, f"held-out IS-A generalization too low: {acc:.2f}"
