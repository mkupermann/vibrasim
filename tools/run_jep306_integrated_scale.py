"""JEP-306 — integrated reasoning at scale over the durable growing substrate, vs a generated ground truth.
Characterizes the honest operating envelope (accuracy vs N), with neurogenesis on. No transformer.

Pre-registered bars in docs/amendments/jep306_integrated_scale.md.
"""
import json, tempfile
from pathlib import Path
import numpy as np
from world.substrate_memory import SubstrateMemory


def gen_taxonomy(n_concepts, branch, seed):
    """A forest of is-a trees: node i's parent is an earlier node (or root). Returns parent map + roots."""
    rng = np.random.default_rng(seed)
    parent = {}
    for i in range(1, n_concepts):
        # attach to an earlier node to bound depth ~log; some become roots
        if rng.random() < 0.12:
            continue                                  # a new root
        p = int(rng.integers(0, i))
        parent[f"c{i}"] = f"c{p}"
    return parent


def ancestors(parent, x):
    out, cur = [], x
    while cur in parent:
        cur = parent[cur]; out.append(cur)
    return out


def build_graph(n_concepts, branch, seed):
    parent = gen_taxonomy(n_concepts, branch, seed)
    rng = np.random.default_rng(seed + 1)
    concepts = [f"c{i}" for i in range(n_concepts)]
    # properties on ~1/5 of nodes (inherited); a few exceptions
    props = {}
    for c in concepts:
        if rng.random() < 0.2:
            props.setdefault(c, set()).add(f"p{int(rng.integers(0, max(2, n_concepts // 10)))}")
    not_props = {}
    # inject exceptions: pick nodes that inherit a prop, negate it
    for c in concepts:
        anc = ancestors(parent, c)
        inh = [p for a in anc for p in props.get(a, set())]
        if inh and rng.random() < 0.15:
            not_props.setdefault(c, set()).add(inh[int(rng.integers(len(inh)))])
    return parent, props, not_props, concepts


def gt_is_a(parent, x, y):
    return y in ancestors(parent, x)


def gt_has_prop(parent, props, not_props, x, p):
    for a in [x] + ancestors(parent, x):              # most specific first
        if p in not_props.get(a, set()):
            return False
        if p in props.get(a, set()):
            return True
    return False


def gate_threshold(mem, seed):
    cal = [("z1", "isa", "w1"), ("z2", "isa", "w2"), ("z3", "isa", "w3")]
    for (c, r, p) in cal:
        if c not in [f[0] for f in mem.facts]:
            mem.add_fact(c, r, p)
    taught = np.mean([mem.query(c, "isa")[1] for (c, _, _) in cal])
    rng = np.random.default_rng(seed + 321)
    untaught = np.mean([mem.query(f"none_{int(rng.integers(1e9))}", "isa")[1] for _ in range(32)])
    return float((taught + untaught) / 2.0)


def is_a_sub(mem, x, y, gate, max_hops=30):
    cur, seen = x, {x}
    for _ in range(max_hops):
        p, s = mem.query(cur, "isa")
        if p is None or s < gate or p in seen:
            return False
        if p == y:
            return True
        seen.add(p); cur = p
    return False


def has_prop_sub(mem, parent, x, p, gate, max_hops=30):
    cur, seen, chain = x, {x}, [x]
    for _ in range(max_hops):
        pp, s = mem.query(cur, "isa")
        if pp is None or s < gate or pp in seen:
            break
        chain.append(pp); seen.add(pp); cur = pp
    for a in chain:
        if mem.contains(a, "not_hasprop", p, gate):
            return False
        if mem.contains(a, "hasprop", p, gate):
            return True
    return False


def build_store(parent, props, not_props):
    mem = SubstrateMemory(D=4096, tau=0.12, directed=True)
    for c, p in parent.items():
        mem.add_fact(c, "isa", p)
    for c, ps in props.items():
        for p in ps:
            mem.add_fact(c, "hasprop", p)
    for c, ps in not_props.items():
        for p in ps:
            mem.add_fact(c, "not_hasprop", p)
    return mem


def n_facts(parent, props, not_props):
    return len(parent) + sum(len(v) for v in props.values()) + sum(len(v) for v in not_props.values())


def score(mem, parent, props, not_props, concepts, seed, gate):
    rng = np.random.default_rng(seed + 7)
    # is-a: balanced positives (descendant->ancestor) + negatives
    pos = [(c, a) for c in concepts for a in ancestors(parent, c)]
    sample_pos = [pos[i] for i in rng.choice(len(pos), min(60, len(pos)), replace=False)] if pos else []
    negs = []
    while len(negs) < len(sample_pos):
        a, b = concepts[int(rng.integers(len(concepts)))], concepts[int(rng.integers(len(concepts)))]
        if not gt_is_a(parent, a, b):
            negs.append((a, b))
    isa_q = sample_pos + negs
    isa_acc = np.mean([is_a_sub(mem, a, b, gate) == gt_is_a(parent, a, b) for (a, b) in isa_q]) if isa_q else 1.0
    # property: sample concept x prop
    allprops = sorted({p for v in props.values() for p in v})
    prop_q = [(concepts[int(rng.integers(len(concepts)))], allprops[int(rng.integers(len(allprops)))])
              for _ in range(80)] if allprops else []
    prop_acc = np.mean([has_prop_sub(mem, parent, x, p, gate) == gt_has_prop(parent, props, not_props, x, p)
                        for (x, p) in prop_q]) if prop_q else 1.0
    return float(isa_acc), float(prop_acc)


def run_at(n_concepts, seed):
    parent, props, not_props, concepts = build_graph(n_concepts, 3, seed)
    mem = build_store(parent, props, not_props)
    gate = gate_threshold(mem, seed)
    isa_acc, prop_acc = score(mem, parent, props, not_props, concepts, seed, gate)
    return {"n_facts": n_facts(parent, props, not_props), "n_modules": len(mem.modules),
            "isa_acc": round(isa_acc, 3), "prop_acc": round(prop_acc, 3),
            "integrated": round((isa_acc + prop_acc) / 2, 3),
            "_mem": mem, "_g": (parent, props, not_props, concepts)}


if __name__ == "__main__":
    print("=== JEP-306: integrated reasoning at scale (envelope) ===", flush=True)
    seeds = [0, 7]
    Ns = [50, 100, 200, 400, 800]

    # J306b: envelope
    curve = {s: {} for s in seeds}
    for s in seeds:
        for n in Ns:
            r = run_at(n, s)
            curve[s][n] = {k: v for k, v in r.items() if not k.startswith("_")}
            print(f"  seed {s} N~{n}: facts={r['n_facts']} modules={r['n_modules']} | is-a={r['isa_acc']} "
                  f"prop={r['prop_acc']} integrated={r['integrated']}", flush=True)

    # J306a + J306c: at N=200, persist round-trip
    persist_ok = {}
    for s in seeds:
        parent, props, not_props, concepts = build_graph(200, 3, s)
        mem = build_store(parent, props, not_props)
        gate = gate_threshold(mem, s)
        pre = score(mem, parent, props, not_props, concepts, s, gate)
        d = tempfile.mkdtemp(prefix=f"scale_{s}_"); mem.save(d)
        mem2 = SubstrateMemory.load(d); gate2 = gate_threshold(mem2, s)
        post = score(mem2, parent, props, not_props, concepts, s, gate2)
        persist_ok[s] = abs((pre[0] + pre[1]) / 2 - (post[0] + post[1]) / 2) <= 0.01

    def integ(s, n):
        return curve[s][n]["integrated"]
    J306a = all(integ(s, 200) >= 0.90 for s in seeds)
    nstar = {}
    for s in seeds:
        below = [n for n in Ns if integ(s, n) < 0.90]
        nstar[s] = below[0] if below else f">{Ns[-1]}"
    multi_engaged = all(curve[s][800]["n_modules"] >= 2 for s in seeds)
    J306b = multi_engaged
    J306c = all(persist_ok[s] for s in seeds)
    passed = J306a and J306b and J306c

    print(f"\n  N* (first <0.90): {nstar} | neurogenesis@N800 modules>=2: {multi_engaged}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    print(f"J306a integrated >=0.90 at N=200      : {J306a}", flush=True)
    print(f"J306b envelope characterized + modules: {J306b}", flush=True)
    print(f"J306c persists at scale (+/-0.01)     : {J306c}", flush=True)
    verdict = ("PASS - integrated reasoning holds to N=200 and the degradation envelope + neurogenesis are "
               "characterized; the grown store persists") if passed else "NULL/partial - see envelope"
    print(f"\nJEP-306: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP306"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"curve": curve, "nstar": {str(k): str(v) for k, v in nstar.items()},
                                                  "J306a": J306a, "J306b": J306b, "J306c": J306c,
                                                  "passed": passed}, indent=2, default=str))
    print("DONE", flush=True)
