"""JEP-304 — acquire ARBITRARY (open) relation types from prose into the durable substrate. Any verb the engine
learns (>=2 occurrences) is bridged as its own role vector; after reload the substrate answers "does s VERB o?" and
"what does s VERB?" matching the engine. No transformer.

Pre-registered bars in docs/amendments/jep304_open_relations.md.
"""
import json, tempfile, subprocess, sys, os
from pathlib import Path
import numpy as np
from world.understanding import UnderstandingEngine
from world.substrate_memory import SubstrateMemory

CORPUS = (
    "A carnivore eats meat. A cow eats grass. A spider spins a web. A weaver spins silk. "
    "A hen lays eggs. A turtle lays eggs. A factory produces cars. A bakery produces bread. "
    "A bee makes honey. An ant makes tunnels. A bird builds a nest. A beaver builds a dam."
)


def general_gate(mem, seed, sample_facts):
    taught = np.mean([mem.query(s, r)[1] for (s, r, o) in sample_facts[:10]])
    rng = np.random.default_rng(seed + 321)
    roles = list({r for (_, r, _) in sample_facts})
    untaught = np.mean([mem.query(f"none_{int(rng.integers(1e9))}", roles[i % len(roles)])[1]
                        for i in range(32)])
    return float((taught + untaught) / 2.0)


def build(eng, extra_fixed=True):
    mem = SubstrateMemory(D=4096, tau=0.12, directed=True)
    for (s, r, o) in eng.facts:                      # OPEN relations (arbitrary verbs)
        mem.add_fact(s, r, o)
    if extra_fixed:                                  # a few fixed relations too (regression coexistence)
        for c, ps in eng.parents.items():
            for p in ps:
                mem.add_fact(c, "isa", p)
    return mem


def run_seed(seed):
    eng = UnderstandingEngine(seed=seed)
    eng.read(CORPUS)
    facts = list(eng.facts)                          # learned (s, verb, o) triples
    rels = sorted({r for (_, r, _) in facts})

    mem = build(eng)
    d = tempfile.mkdtemp(prefix=f"open_{seed}_")
    mem.save(d)
    mem2 = SubstrateMemory.load(d)
    gate = general_gate(mem2, seed, facts)

    # J304a: recall the object + truth matches engine
    recall = np.mean([mem2.query(s, r)[0] == o for (s, r, o) in facts])
    truth_pos = np.mean([mem2.contains(s, r, o, gate) == eng.relation_holds(s, r, o) for (s, r, o) in facts])

    # J304b: balanced true/false; false = (s, r, o') with o' another object of r not bound to s
    objs_by_rel = {}
    for (s, r, o) in facts:
        objs_by_rel.setdefault(r, set()).add(o)
    rng = np.random.default_rng(seed)
    neg = []
    for (s, r, o) in facts:
        others = [x for x in objs_by_rel[r] if x != o]
        if others:
            neg.append((s, r, others[int(rng.integers(len(others)))]))
    balanced = [(s, r, o, True) for (s, r, o) in facts] + [(s, r, o, False) for (s, r, o) in neg]
    nofalse = np.mean([mem2.contains(s, r, o, gate) == eng.relation_holds(s, r, o) for (s, r, o, _) in balanced])

    # J304c: persists
    mem3 = SubstrateMemory.load(d); gate3 = general_gate(mem3, seed, facts)
    persist = all(mem3.query(s, r)[0] == mem2.query(s, r)[0] for (s, r, o) in facts)

    demo = {"learned_relations": rels,
            "what_does_carnivore_eat": mem2.query("carnivore", "eats")[0],
            "what_does_factory_produce": mem2.query("factory", "produces")[0],
            "spider_spins_web?": mem2.contains("spider", "spins", "web", gate),
            "spider_spins_silk?": mem2.contains("spider", "spins", "silk", gate)}
    return {"recall": round(float(recall), 3), "truth_pos": round(float(truth_pos), 3),
            "balanced_acc": round(float(nofalse), 3), "persist_ok": bool(persist),
            "n_rels": len(rels), "n_facts": len(facts), "demo": demo}


def regression(repo):
    r = subprocess.run([sys.executable, "tools/run_jep300_multirelational_bridge.py"], capture_output=True,
                       text=True, env={**os.environ, "PYTHONPATH": repo})
    return "JEP-300: PASS" in r.stdout


if __name__ == "__main__":
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print("=== JEP-304: arbitrary (open) relation types into the durable substrate ===", flush=True)
    seeds = [0, 7]
    R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]
        print(f"  seed {s}: {r['n_rels']} learned relations, {r['n_facts']} facts | object recall={r['recall']} "
              f"truth={r['truth_pos']} | balanced acc={r['balanced_acc']} | persists={r['persist_ok']}", flush=True)
        print(f"           demo={r['demo']}", flush=True)
    reg = regression(repo)
    print(f"  regression JEP-300: {'PASS' if reg else 'FAIL'}", flush=True)

    J304a = all(R[s]['recall'] >= 0.95 and R[s]['truth_pos'] >= 0.95 for s in seeds)
    J304b = all(R[s]['balanced_acc'] >= 0.90 for s in seeds)
    J304c = all(R[s]['persist_ok'] for s in seeds)
    passed = J304a and J304b and J304c and reg
    print("\n--- VERDICT ---", flush=True)
    print(f"J304a open-relation object recall + truth (>=.95): {J304a}", flush=True)
    print(f"J304b no hallucinated relations (>=.90)          : {J304b}", flush=True)
    print(f"J304c persists across reload                     : {J304c}", flush=True)
    print(f"no-regression: JEP-300 fixed relations still PASS: {reg}", flush=True)
    verdict = ("PASS - the substrate acquires arbitrary relation types learned from prose (any verb), stores them "
               "durably, and answers them after reload, matching the engine") if passed else "NULL/partial"
    print(f"\nJEP-304: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP304"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": {str(s): R[s] for s in seeds}, "reg": reg,
                                                  "J304a": J304a, "J304b": J304b, "J304c": J304c,
                                                  "passed": passed}, indent=2, default=str))
    print("DONE", flush=True)
