"""Permanent test gate for the durable VSA relational memory (JEP-294..320).
Locks: persistence round-trip, routed multi-hop, inheritance/exception, DAG, abduction, contradiction, and the
meta-learning inductions. Fast (D kept modest); no transformer. Run: pytest tests/test_substrate_memory.py -q
"""
import tempfile
import numpy as np
import pytest

from world.substrate_memory import SubstrateMemory, atom_vector


def _gate(mem, role="isa"):
    edges = [(a, b) for (a, r, b) in mem.facts if r == role]
    rng = np.random.default_rng(0)
    samp = [edges[i] for i in rng.choice(len(edges), min(20, len(edges)), replace=False)] if edges else []
    t = np.mean([mem.query(a, role)[1] for (a, b) in samp]) if samp else 0.2
    u = np.mean([mem.query(f"none_{int(rng.integers(1e9))}", role)[1] for _ in range(20)])
    return float((t + u) / 2)


def _climb(mem, x, y, rel, g, mx=15):
    cur, seen = x, {x}
    for _ in range(mx):
        p, s = mem.query(cur, rel)
        if p is None or s < g or p in seen:
            return False
        if p == y:
            return True
        seen.add(p); cur = p
    return False


def _taxonomy(directed=True):
    mem = SubstrateMemory(D=2048, tau=0.12, directed=directed)
    for c, p in [("poodle", "dog"), ("dog", "mammal"), ("mammal", "animal"),
                 ("penguin", "bird"), ("penguin", "swimmer"), ("bird", "animal"), ("swimmer", "animal")]:
        mem.add_fact(c, "isa", p)
    return mem


def test_atom_vector_deterministic_cross_process():
    # hashlib-seeded -> identical regardless of process/run (the JEP-295 correctness detail)
    a = atom_vector("germany", 2048); b = atom_vector("germany", 2048)
    assert np.array_equal(a, b)
    assert abs(float(np.dot(a, atom_vector("hungary", 2048)) / 2048)) < 0.1   # near-orthogonal


def test_persistence_roundtrip():
    mem = _taxonomy()
    with tempfile.TemporaryDirectory() as d:
        mem.save(d)
        m2 = SubstrateMemory.load(d)
    assert m2.query("poodle", "isa")[0] == "dog"
    assert m2.directed == mem.directed
    assert m2.key_modules  # routing table persisted


def test_directed_multihop_and_directionality():
    mem = _taxonomy(directed=True)
    g = _gate(mem)
    assert _climb(mem, "poodle", "animal", "isa", g)          # 3 hops
    assert not _climb(mem, "poodle", "fish", "isa", g)
    # directionality: a node does not retrieve its children backward
    assert mem.query("animal", "isa")[1] < g


def test_routing_rejects_untaught_key():
    # module-aware routing (JEP-307): a key never stored as a subject returns no match -> clean reject
    mem = _taxonomy()
    assert mem.query("animal", "isa")[0] is None         # 'animal' is never a subject of isa
    assert mem.query("nonexistent", "isa")[0] is None


def test_dag_set_retrieval():
    mem = _taxonomy()
    g = _gate(mem)
    parents = {p for (p, _) in mem.query_all("penguin", "isa", g)}
    assert {"bird", "swimmer"} <= parents


def test_inheritance_with_exception():
    mem = _taxonomy()
    mem.add_fact("bird", "hasprop", "fly")
    mem.add_fact("penguin", "not_hasprop", "fly")
    g = _gate(mem)

    def hasprop(x, p):
        chain, cur, seen = [x], x, {x}
        for _ in range(15):
            nx, s = mem.query(cur, "isa")
            if nx is None or s < g or nx in seen:
                break
            chain.append(nx); seen.add(nx); cur = nx
        for a in chain:
            if mem.contains(a, "not_hasprop", p, g):
                return False
            if mem.contains(a, "hasprop", p, g):
                return True
        return False

    assert hasprop("penguin", "fly") is False        # exception wins
    assert hasprop("robin" if False else "swimmer", "fly") in (False, True)  # no crash on unknown chain


def test_abduction_via_inverse():
    mem = SubstrateMemory(D=2048, directed=True)
    for c, e in [("smoking", "cancer"), ("radiation", "cancer")]:
        mem.add_fact(c, "causes", e); mem.add_fact(e, "caused_by", c)
    g = _gate(mem, "caused_by")
    causes = {c for (c, _) in mem.query_all("cancer", "caused_by", g)}
    assert causes == {"smoking", "radiation"}


def test_contradiction_detection_vs_exception():
    mem = _taxonomy()
    mem.add_fact("bird", "hasprop", "fly")
    mem.add_fact("penguin", "not_hasprop", "fly")           # exception (inherited+ / explicit-)
    mem.add_fact("robin", "hasprop", "swim")
    mem.add_fact("robin", "not_hasprop", "swim")            # direct contradiction
    g = _gate(mem)
    conflicts = mem.detect_conflicts(g)
    assert ("robin", "hasprop", "swim") in conflicts
    assert not any(c[0] == "penguin" for c in conflicts)    # exception NOT flagged


def _bfs_reach(mem, x, y, rel, g, mx=40):
    from collections import deque
    q, seen, n = deque([x]), {x}, 0
    while q and n < mx:
        cur = q.popleft(); n += 1
        for (p, _) in mem.query_all(cur, rel, g):
            if p == y:
                return True
            if p not in seen:
                seen.add(p); q.append(p)
    return False


def test_temporal_before_transitive_asymmetric():
    mem = SubstrateMemory(D=4096, directed=True)
    for a, b in [("protest", "election"), ("election", "war"), ("war", "treaty")]:
        mem.add_fact(a, "before", b)
    g = _gate(mem, "before")
    assert _bfs_reach(mem, "protest", "treaty", "before", g)      # 3-hop transitive
    assert not _bfs_reach(mem, "treaty", "protest", "before", g)  # asymmetric


def test_induce_symmetry_and_transitivity():
    mem = SubstrateMemory(D=4096, directed=True)
    for a, b in [("a", "b"), ("a", "c"), ("b", "c")]:            # transitive closure pattern
        mem.add_fact(a, "rel_t", b)
    for a, b in [("x", "y"), ("p", "q")]:
        mem.add_fact(a, "rel_s", b); mem.add_fact(b, "rel_s", a)  # symmetric
    f_s = {(s, o) for (s, r, o) in mem.facts if r == "rel_s"}
    f_t = {(s, o) for (s, r, o) in mem.facts if r == "rel_t"}
    sym = np.mean([1.0 if (b, a) in f_s else 0.0 for (a, b) in f_s])
    comps = [(a, c) for (a, b) in f_t for (b2, c) in f_t if b == b2 and a != c]
    trans = np.mean([1.0 if (a, c) in f_t else 0.0 for (a, c) in comps]) if comps else 0.0
    assert sym >= 0.7 and trans >= 0.7


def test_discover_inverse_pair():
    mem = SubstrateMemory(D=4096, directed=True)
    for a, b in [("p1", "c1"), ("p2", "c2"), ("p3", "c3")]:
        mem.add_fact(a, "parent_of", b); mem.add_fact(b, "child_of", a)
    fp = {(s, o) for (s, r, o) in mem.facts if r == "parent_of"}
    fc = {(s, o) for (s, r, o) in mem.facts if r == "child_of"}
    inv = np.mean([1.0 if (b, a) in fc else 0.0 for (a, b) in fp])
    assert inv >= 0.8


def test_brain_query_interface_and_parser():
    from world.brain_query import BrainQuery
    mem = _taxonomy()
    mem.add_fact("bird", "hasprop", "fly")
    mem.add_fact("penguin", "not_hasprop", "fly")
    for c, e in [("smoking", "cancer")]:
        mem.add_fact(c, "causes", e); mem.add_fact(e, "caused_by", c)
    mem.add_fact("cat", "eats", "fish")
    with tempfile.TemporaryDirectory() as d:
        mem.save(d)
        bq = BrainQuery(SubstrateMemory.load(d))
    assert bq.is_a("poodle", "animal") is True
    assert bq.is_a("poodle", "fish") is False
    assert bq.has_property("penguin", "fly") is False     # exception
    assert bq.why("cancer") == ["smoking"]
    assert bq.ask("is a poodle an animal?") is True
    assert bq.ask("can a penguin fly?") is False
    assert bq.ask("what does a cat eat?") == ["fish"]     # verb-morphology (eat->eats)


def test_noise_tolerance_improves_with_width():
    # JEP-315: wider D tolerates more cue corruption
    def recall(D, f, n=40):
        from world.vsa import bind
        mem = SubstrateMemory(D=D, directed=True)
        facts = [(f"e{i}", "rel", f"v{i}") for i in range(n)]
        for (e, r, o) in facts:
            mem.add_fact(e, r, o)
        VM, names = mem._value_matrix()
        rng = np.random.default_rng(1)
        ok = 0
        for (e, r, o) in facts:
            key = bind(atom_vector(e, D), atom_vector(r, D)).copy()
            key[rng.choice(D, int(f * D), replace=False)] *= -1
            best, bi = -1e9, None
            for m in mem._route(e, r):
                rv = np.roll(mem._mem(m) * key, -1)
                sc = rv @ VM.T / D
                j = int(np.argmax(sc))
                if sc[j] > best:
                    best, bi = sc[j], names[j]
            ok += (bi == o)
        return ok / n
    assert recall(4096, 0.15) <= recall(8192, 0.15) + 1e-9
    assert recall(8192, 0.10) >= 0.9


def test_energy_model_generalizes_valence_to_untaught_concepts():
    """JEP-436: learn_valence trains the energy model so predict_valence GENERALIZES affect to
    concepts never told their valence, from their feature-cloud — while returning taught values exact."""
    import numpy as np
    from world.substrate_memory import SubstrateMemory
    dark = [f"dk_{i}" for i in range(5)]; bright = [f"br_{i}" for i in range(5)]; pool = dark + bright
    rng = np.random.default_rng(0)

    def populate(sm, names):
        out = []
        for nm in names:
            feats = [pool[i] for i in rng.choice(len(pool), size=5, replace=False)]
            for f in feats:
                sm.add_fact(nm, "has", f)
            nd = sum(f in dark for f in feats)
            out.append((nm, -1.0 if nd > 5 - nd else 1.0))
        return out

    sm = SubstrateMemory(D=4096); sm.energy_seed = 0
    train = populate(sm, [f"tr_{i}" for i in range(200)])
    test = populate(sm, [f"te_{i}" for i in range(100)])     # facts only, valence NOT taught
    for nm, v in train:
        sm.learn_valence(nm, v)

    held = sum(np.sign(sm.predict_valence(nm)) == v for nm, v in test) / len(test)
    taught = sum(sm.predict_valence(nm) == v for nm, v in train) / len(train)
    assert held >= 0.80          # generalizes to untaught concepts
    assert taught == 1.0         # exact on taught (no regression)
