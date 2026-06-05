"""JEP-403 — lazy consolidation: reliable deep reasoning for interactive (GUI) teaching. No transformer.
Pre-registered bars in docs/amendments/jep403_lazy_consolidation.md.
"""
import json, tempfile, subprocess, sys, os
from pathlib import Path
import numpy as np
from world.conversation import Conversation


def build_tree(n_nodes, rng, max_depth=8):
    depth = {0: 0}; parent = {0: None}
    for i in range(1, n_nodes):
        cands = [k for k in depth if depth[k] < max_depth]
        w = np.array([depth[k] + 1 for k in cands], float)
        p = int(rng.choice(cands, p=w / w.sum()))
        parent[i] = p; depth[i] = depth[p] + 1
    return parent, depth


def nm(i):
    s = ""; j = i + 1
    while j > 0:
        s = chr(ord('a') + (j % 26)) + s; j //= 26
    return "x" + s


def ancestors(parent, x):
    out = []
    while parent[x] is not None:
        out.append(parent[x]); x = parent[x]
    return out


def run_seed(seed, N=90):
    rng = np.random.default_rng(seed)
    parent, depth = build_tree(N, rng)
    c = Conversation(brain_dir=tempfile.mkdtemp(prefix=f"j403_{seed}_"), seed=seed)
    # teach via INDIVIDUAL say() statements (interactive), NOT read_text
    for i in range(1, N):
        c.say(f"A {nm(i)} is a {nm(parent[i])}.")
    # J403b: after teaching-only (no question yet), the store is NOT yet consolidated
    consolidated_before_q = "isa" in c.sm.closed_relations
    # ask deep questions (this triggers lazy consolidation)
    rng2 = np.random.default_rng(seed + 100)
    leaves = [k for k in range(N) if k not in set(parent.values())]; rng2.shuffle(leaves)
    correct = 0; total = 0
    for x in leaves[:30]:
        anc = ancestors(parent, x)
        if not anc:
            continue
        z = anc[min(len(anc) - 1, int(rng2.integers(0, len(anc))))]
        if "yes" in c.say(f"is a {nm(x)} a {nm(z)}?").strip().lower():
            correct += 1
        total += 1
    deep_acc = round(correct / total, 3) if total else None
    consolidated_after_q = "isa" in c.sm.closed_relations
    return {"deep_acc": deep_acc, "consolidated_before_q": bool(consolidated_before_q),
            "consolidated_after_q": bool(consolidated_after_q), "facts": len(c.sm.facts)}


def single(seed):
    c = Conversation(brain_dir=tempfile.mkdtemp(prefix=f"j403s_{seed}_"), seed=seed)
    c.say("A poodle is a dog. A dog is a mammal.")
    return "yes" in c.say("is a poodle a mammal?").strip().lower()


def suite(repo):
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-m", "not slow", "tests/test_conversation.py"],
                       capture_output=True, text=True, env={**os.environ, "PYTHONPATH": repo})
    last = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ""
    return ("failed" not in r.stdout and "error" not in r.stdout.lower().split("warnings")[0]), last


if __name__ == "__main__":
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print("=== JEP-403: lazy consolidation for interactive teaching ===", flush=True)
    seeds = [0, 7]
    R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]
        print(f"  seed {s}: deep_acc={r['deep_acc']} (interactive, {r['facts']} facts) | consolidated before-Q="
              f"{r['consolidated_before_q']} after-Q={r['consolidated_after_q']}", flush=True)
    singles = all(single(s) for s in seeds)
    gate_ok, line = suite(repo)
    print(f"  single teach->ask: {singles} | conversation suite: {gate_ok} ({line})", flush=True)

    J403a = all(R[s]['deep_acc'] >= 0.95 for s in seeds)
    J403b = all((not R[s]['consolidated_before_q']) and R[s]['consolidated_after_q'] for s in seeds)
    J403c = singles and gate_ok
    passed = J403a and J403b and J403c
    print("\n--- VERDICT ---", flush=True)
    print(f"J403a interactive deep reasoning >=0.95 : {J403a}", flush=True)
    print(f"J403b lazy (consolidate only before Q)  : {J403b}", flush=True)
    print(f"J403c single teach->ask + suite         : {J403c}", flush=True)
    verdict = ("PASS - interactive statement-by-statement teaching now yields reliable deep multi-hop (>=0.95) because "
               "the store lazily consolidates before answering a question (not per statement); single teach->ask and "
               "the suite are intact. The GUI's interactive teaching gets the consolidation reliability automatically.")\
        if passed else "NULL/partial - see rows (a bar missed; report, do not retune)."
    print(f"\nJEP-403: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP403"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": R, "singles": singles, "gate": gate_ok, "J403a": J403a,
                                                  "J403b": J403b, "J403c": J403c, "passed": passed}, default=str))
    print("DONE", flush=True)
