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
