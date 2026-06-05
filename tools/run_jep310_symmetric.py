"""JEP-310 — symmetric relations (store both directions, query either way)."""
import json, tempfile
from pathlib import Path
import numpy as np
from world.substrate_memory import SubstrateMemory

PAIRS = {"married_to": [("alice", "bob"), ("carol", "dave"), ("eve", "frank")],
         "sibling_of": [("tom", "sue"), ("ann", "joe"), ("kim", "leo")]}
CALIB = [("z1", "married_to", "w1"), ("z2", "married_to", "w2"), ("z3", "married_to", "w3")]


def gate(mem, seed):
    t = np.mean([mem.query(c, "married_to")[1] for (c, _, _) in CALIB])
    rng = np.random.default_rng(seed + 321)
    u = np.mean([mem.query(f"n_{int(rng.integers(1e9))}", "married_to")[1] for _ in range(32)])
    return float((t + u) / 2)


def build():
    mem = SubstrateMemory(D=4096, tau=0.12, directed=True)
    for rel, ps in PAIRS.items():
        for (a, b) in ps:
            mem.add_fact(a, rel, b); mem.add_fact(b, rel, a)        # symmetric: both directions
    for (c, r, p) in CALIB:
        mem.add_fact(c, r, p)
    return mem


def run_seed(seed):
    mem = build(); d = tempfile.mkdtemp(); mem.save(d); mem2 = SubstrateMemory.load(d); g = gate(mem2, seed)
    ok = tot = 0
    for rel, ps in PAIRS.items():
        for (a, b) in ps:
            tot += 2
            ok += (mem2.query(a, rel)[0] == b) + (mem2.query(b, rel)[0] == a)
    mem3 = SubstrateMemory.load(d)
    persist = all(mem3.query(a, rel)[0] == mem2.query(a, rel)[0] for rel, ps in PAIRS.items() for (a, b) in ps)
    return {"sym_acc": round(ok / tot, 3), "persist": bool(persist)}


if __name__ == "__main__":
    seeds = [0, 7]; R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        print(f"JEP310 seed {s}: symmetric acc={R[s]['sym_acc']} persists={R[s]['persist']}", flush=True)
    J310a = all(R[s]['sym_acc'] >= 0.95 for s in seeds); J310b = all(R[s]['persist'] for s in seeds)
    passed = J310a and J310b
    print(f"JEP-310: {'PASS' if passed else 'NULL/partial'} (J310a={J310a} J310b={J310b})", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP310"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": R, "J310a": J310a, "J310b": J310b, "passed": passed}, default=str))
    print("DONE", flush=True)
