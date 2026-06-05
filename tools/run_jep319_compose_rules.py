"""JEP-319 — induce two-relation COMPOSITION rules from examples, apply over the store. No transformer.
Pre-registered bars in docs/amendments/jep319_compose_rules.md.
"""
import json, tempfile, itertools
from pathlib import Path
import numpy as np
from world.substrate_memory import SubstrateMemory

PARENT = [("al", "bo"), ("al", "bea"), ("al", "cal"),
          ("bo", "cy"), ("bo", "dan"), ("bea", "ed"), ("bea", "fay"), ("cal", "gus")]
SIBS = [("bo", "bea"), ("bo", "cal"), ("bea", "cal"), ("cy", "dan"), ("ed", "fay")]   # stored symmetric below
CALIB = [("z1", "parent_of", "w1"), ("z2", "parent_of", "w2"), ("z3", "parent_of", "w3")]


def gate(mem, seed):
    t = np.mean([mem.query(c, "parent_of")[1] for (c, _, _) in CALIB])
    rng = np.random.default_rng(seed + 321)
    u = np.mean([mem.query(f"n_{int(rng.integers(1e9))}", "parent_of")[1] for _ in range(32)])
    return float((t + u) / 2)


def build():
    mem = SubstrateMemory(D=4096, tau=0.12, directed=True)
    for a, b in PARENT:
        mem.add_fact(a, "parent_of", b)
    for a, b in SIBS:
        mem.add_fact(a, "sibling_of", b); mem.add_fact(b, "sibling_of", a)   # symmetric
    for (c, r, p) in CALIB:
        mem.add_fact(c, r, p)
    return mem


def base_sets(mem):
    return {rel: {(s, o) for (s, r, o) in mem.facts if r == rel} for rel in ["parent_of", "sibling_of"]}


def gt_compose(R1, R2, B):
    return {(a, c) for (a, x) in B[R1] for (x2, c) in B[R2] if x == x2 and a != c}


def induce(examples, B, rels):
    best, bestsc = None, 0.0
    for R1, R2 in itertools.product(rels, repeat=2):
        comp = gt_compose(R1, R2, B)
        sc = np.mean([1.0 if (a, c) in comp else 0.0 for (a, c) in examples]) if examples else 0.0
        if sc > bestsc:
            best, bestsc = (R1, R2), sc
    return (best if bestsc >= 0.8 else None), bestsc


def apply_rule(mem, R1, R2, a, c, g):
    xs = [x for (x, _) in mem.query_all(a, R1, g)]
    for x in xs:
        if c in [y for (y, _) in mem.query_all(x, R2, g)]:
            return True
    return False


def run_seed(seed):
    mem = build(); d = tempfile.mkdtemp(prefix=f"cmp_{seed}_"); mem.save(d); mem2 = SubstrateMemory.load(d)
    g = gate(mem2, seed); B = base_sets(mem2); rels = ["parent_of", "sibling_of"]

    targets = {"grandparent_of": ("parent_of", "parent_of"), "aunt_of": ("sibling_of", "parent_of")}
    induced = {}; apply_acc = []
    for T, (tr1, tr2) in targets.items():
        gt = sorted(gt_compose(tr1, tr2, B))
        labeled = gt[:2]; held = gt[2:]
        rule, sc = induce(labeled, B, rels)
        induced[T] = rule
        # held-out + negatives
        nodes = sorted({x for e in PARENT for x in e})
        negs = [pr for pr in itertools.permutations(nodes, 2) if pr not in set(gt)][:max(1, len(held))]
        for (a, c) in held + negs:
            pred = apply_rule(mem2, rule[0], rule[1], a, c, g) if rule else False
            apply_acc.append(pred == ((a, c) in set(gt)))

    induce_ok = all(induced[T] == targets[T] for T in targets)

    # J319c negative: a scrambled target has no covering rule
    rng = np.random.default_rng(seed)
    scram = [(f"x{int(rng.integers(100))}", f"y{int(rng.integers(100))}") for _ in range(5)]
    neg_rule, neg_sc = induce(scram, B, rels)
    no_false_rule = (neg_rule is None)

    mem3 = SubstrateMemory.load(d); B3 = base_sets(mem3)
    persist = all(induce(sorted(gt_compose(*targets[T], B3))[:2], B3, rels)[0] == induced[T] for T in targets)
    return {"induce_ok": bool(induce_ok), "apply_acc": round(float(np.mean(apply_acc)), 3),
            "no_false_rule": bool(no_false_rule), "persist": bool(persist), "induced": induced}


if __name__ == "__main__":
    print("=== JEP-319: induce two-relation composition rules ===", flush=True)
    seeds = [0, 7]; R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        print(f"  seed {s}: induce_ok={R[s]['induce_ok']} apply acc={R[s]['apply_acc']} "
              f"no-false-rule={R[s]['no_false_rule']} persists={R[s]['persist']}", flush=True)
        print(f"           induced={R[s]['induced']}", flush=True)
    J319a = all(R[s]['induce_ok'] for s in seeds)
    J319b = all(R[s]['apply_acc'] >= 0.90 for s in seeds)
    J319c = all(R[s]['no_false_rule'] and R[s]['persist'] for s in seeds)
    passed = J319a and J319b and J319c
    print("\n--- VERDICT ---", flush=True)
    print(f"J319a induce composition rule correctly: {J319a}", flush=True)
    print(f"J319b apply to held-out (>=.90)         : {J319b}", flush=True)
    print(f"J319c negative no-rule + persists       : {J319c}", flush=True)
    verdict = ("PASS - the substrate induces that a relation is the COMPOSITION of two base relations and answers "
               "held-out queries by composing them over the store") if passed else "NULL/partial"
    print(f"\nJEP-319: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP319"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": R, "J319a": J319a, "J319b": J319b, "J319c": J319c,
                                                  "passed": passed}, default=str))
    print("DONE", flush=True)
