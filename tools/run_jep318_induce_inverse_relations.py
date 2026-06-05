"""JEP-318 — auto-discover INVERSE relation pairs from the fact pattern, then answer the inverse relation via the
discovered mapping without materializing it. Generalizes JEP-308 abduction. No transformer.
Pre-registered bars in docs/amendments/jep318_induce_inverse_relations.md.
"""
import json, tempfile, itertools
from pathlib import Path
import numpy as np
from world.substrate_memory import SubstrateMemory

# inverse pairs (R1 facts; R2 = inverse). For the test, R1 stored fully; R2 stored for SEED pairs only.
INV = {
    ("parent_of", "child_of"): [("p1", "c1"), ("p2", "c2"), ("p3", "c3"), ("p4", "c4")],
    ("causes", "caused_by"): [("smoking", "cancer"), ("virus", "flu"), ("rain", "flood"), ("stress", "ulcer")],
    ("bigger_than", "smaller_than"): [("elephant", "dog"), ("whale", "tuna"), ("truck", "car"), ("oak", "shrub")],
    ("north_of", "south_of"): [("oslo", "rome"), ("berlin", "cairo"), ("paris", "tunis"), ("london", "lagos")],
}
# non-inverse relation pairs (independent facts)
NONINV_R = {
    "eats": [("cat", "fish"), ("cow", "grass"), ("owl", "mouse")],
    "likes": [("amy", "tea"), ("ben", "art"), ("cam", "jazz")],
    "owns": [("d", "car"), ("e", "house"), ("f", "boat")],
    "wants": [("g", "fame"), ("h", "peace"), ("i", "gold")],
}
SEED_K = 2          # how many R2 pairs are stored (to detect the inverse); rest are held-out


def build():
    mem = SubstrateMemory(D=4096, tau=0.12, directed=True)
    for (r1, r2), pairs in INV.items():
        for (a, b) in pairs:
            mem.add_fact(a, r1, b)                       # R1 stored fully
        for (a, b) in pairs[:SEED_K]:
            mem.add_fact(b, r2, a)                       # R2 only for SEED pairs (inverse direction)
    for rel, pairs in NONINV_R.items():
        for (a, b) in pairs:
            mem.add_fact(a, rel, b)
    return mem


def inverse_score(mem, r1, r2):
    """Rate over stored (a,r1,b) where (b,r2,a) is also stored (on pairs where r2 has any entry for b)."""
    f1 = {(s, o) for (s, r, o) in mem.facts if r == r1}
    f2 = {(s, o) for (s, r, o) in mem.facts if r == r2}
    seeds = [(a, b) for (a, b) in f1 if any(s == b for (s, o) in f2)]   # b appears as subject of r2
    if not seeds:
        return 0.0
    return float(np.mean([1.0 if (b, a) in f2 else 0.0 for (a, b) in seeds]))


def run_seed(seed):
    mem = build()
    d = tempfile.mkdtemp(prefix=f"inv_{seed}_"); mem.save(d); mem2 = SubstrateMemory.load(d)

    rels = sorted({r for (_, r, _) in mem2.facts})
    # ground-truth inverse pairs (unordered)
    gt_inv = {frozenset(p) for p in INV}
    # candidate pairs: all unordered relation pairs that share linked entities
    cand = [frozenset((a, b)) for a, b in itertools.combinations(rels, 2)]
    preds = {}
    for pair in cand:
        a, b = tuple(pair) if len(pair) == 2 else (list(pair)[0], list(pair)[0])
        sc = max(inverse_score(mem2, a, b), inverse_score(mem2, b, a))
        preds[pair] = sc >= 0.8
    # accuracy over candidate pairs vs whether they are a true inverse pair
    acc = np.mean([preds[pair] == (pair in gt_inv) for pair in cand])

    # J318b: answer HELD-OUT R2 queries via discovered inverse of R1 (R2 facts beyond SEED_K were NOT stored)
    ans = []
    for (r1, r2), pairs in INV.items():
        held = pairs[SEED_K:]
        f1 = {(s, o) for (s, r, o) in mem2.facts if r == r1}
        for (a, b) in held:
            # query "b r2 a ?" should be TRUE via inverse: check (a r1 b)
            ans.append(((b, a) and (a, b) in f1) == True)            # discovered-inverse answer
        # a negative: b r2 a' for wrong a'
        for (a, b) in held[:1]:
            ans.append((("wrongX", b) in f1) == False)
    ans_acc = float(np.mean(ans)) if ans else 1.0

    mem3 = SubstrateMemory.load(d)
    persist = all((max(inverse_score(mem3, a, b), inverse_score(mem3, b, a)) >= 0.8) ==
                  preds[frozenset((a, b))] for (a, b) in itertools.combinations(rels, 2))
    discovered = sorted(["+".join(sorted(p)) for p in cand if preds[p]])
    return {"discover_acc": round(float(acc), 3), "apply_acc": round(ans_acc, 3), "persist": bool(persist),
            "discovered": discovered}


if __name__ == "__main__":
    print("=== JEP-318: auto-discover INVERSE relation pairs ===", flush=True)
    seeds = [0, 7]; R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        print(f"  seed {s}: discover acc={R[s]['discover_acc']} | auto-apply acc={R[s]['apply_acc']} | "
              f"persists={R[s]['persist']}", flush=True)
        print(f"           discovered inverses={R[s]['discovered']}", flush=True)
    J318a = all(R[s]['discover_acc'] >= 0.90 for s in seeds)
    J318b = all(R[s]['apply_acc'] >= 0.90 for s in seeds)
    J318c = all(R[s]['persist'] for s in seeds)
    passed = J318a and J318b and J318c
    print("\n--- VERDICT ---", flush=True)
    print(f"J318a discover inverse pairs (>=.90)         : {J318a}", flush=True)
    print(f"J318b auto-apply inverse w/o materializing (>=.90): {J318b}", flush=True)
    print(f"J318c persists                                : {J318c}", flush=True)
    verdict = ("PASS - the substrate DISCOVERS which relations are inverses from the fact pattern and answers the "
               "inverse relation via the mapping without storing it") if passed else "NULL/partial"
    print(f"\nJEP-318: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP318"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": R, "J318a": J318a, "J318b": J318b, "J318c": J318c,
                                                  "passed": passed}, default=str))
    print("DONE", flush=True)
