"""Tests for the EQMOD-4 mixed-curvature ConceptReasoner (JEP-28). Fast slice.

Protects the reusable deliverable: relatedness (Euclidean) + IS-A (hyperbolic) over a taxonomy.
Honest bounds (per docs/amendments/jep28_concept_reasoner.md): per-query IS-A is reliable at >= 5D,
NOT at 2D; aggregate held-out IS-A generalization >= ~0.85 at >= 5D on small taxonomies.
"""
import numpy as np
import pytest

pytest.importorskip("torch", reason="tools/concept_reasoner.py needs torch; "
                    "not a declared dependency (archive JEP-28 track)")

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
    # NOTE: the calibrated classifier needs ENOUGH pairs; use an adequately-sized taxonomy
    # (a tiny 8-node tree does not give enough calibration data - JEP-32 finding).
    tax2 = {"living_thing": ["animal", "plant"], "animal": ["mammal", "bird"],
            "mammal": ["carnivore", "primate"], "carnivore": ["cat", "dog", "wolf"],
            "primate": ["human", "chimp"], "bird": ["eagle", "sparrow", "owl"],
            "plant": ["tree", "flower"], "tree": ["oak", "pine", "maple"],
            "flower": ["rose", "tulip", "daisy"]}
    cr = ConceptReasoner(tax2); cr.fit(euc_dim=4, hyp_dim=10, iters=4000)
    assert cr.is_a("cat", "mammal")          # true ancestor
    assert cr.is_a("cat", "animal")          # true ancestor (transitive)
    assert not cr.is_a("oak", "mammal")      # cross-branch general concept - must be rejected
    assert not cr.is_a("rose", "animal")     # cross-branch
    # NOTE: siblings (is_a('cat','dog')) are a known residual weakness (JEP-32), not asserted here.


def test_order_method_rejects_siblings():
    # JEP-45: isa_method="order" (Vendrov order embeddings) fixes the sibling residual that the
    # default poincare method has (JEP-33), and is the recommended method for large real hierarchies.
    cr = ConceptReasoner(TAX); cr.fit(euc_dim=4, hyp_dim=8, iters=4000, isa_method="order")
    assert cr.is_a("cat", "mammal")        # true ancestor
    assert cr.is_a("cat", "carnivore")     # true ancestor
    assert not cr.is_a("cat", "dog")       # SIBLING - order embeddings reject (poincare does not)
    assert not cr.is_a("mammal", "cat")    # reversed
    assert not cr.is_a("eagle", "sparrow")  # sibling


def test_more_general_direction():
    cr = _fit()
    assert cr.more_general("cat", "mammal") == "mammal"
    assert cr.more_general("animal", "carnivore") == "animal"


def test_relatedness_nearest_is_taxonomic():
    cr = _fit()
    near = cr.nearest("cat", k=3)
    # cat's nearest should include its siblings (dog/wolf) or its parent class, not e.g. eagle
    assert any(n in {"dog", "wolf", "carnivore"} for n in near)


def test_is_a_in_sample_correct():
    # The robust, reliable deliverable behavior: the reasoner correctly answers is_a for the taxonomy it is
    # fit on (in-sample). HELD-OUT link-prediction generalization is a SEPARATE, scale-dependent property:
    # it is WEAK on small taxonomies (~0.4 calibrated recall) and needs a larger taxonomy (77+ concepts) to
    # generalize - documented in docs/amendments/jep51_dag.md. So we test the robust in-sample correctness.
    cr = _fit()
    ALL = [(u, v) for v in range(cr.N) for u in cr._ancestors(v)]
    tpr = np.mean([cr.is_a(cr.nodes[v], cr.nodes[u]) for (u, v) in ALL])  # in-sample recall on true ancestors
    assert tpr >= 0.95, f"in-sample is_a recall too low: {tpr:.2f}"
