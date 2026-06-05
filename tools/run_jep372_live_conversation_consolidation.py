"""JEP-372 — end-to-end: the live Conversation auto-consolidates after read_text so deep questions are reliable.
No transformer. Pre-registered bars in docs/amendments/jep372_live_conversation_consolidation.md.
"""
import json, tempfile, subprocess, sys, os
from pathlib import Path
import numpy as np
from world.conversation import Conversation


def nm(i):
    """Alphabetic-only pseudo-word node name (the understanding engine rejects names with digits)."""
    s = ""; j = i + 1
    while j > 0:
        s = chr(ord('a') + (j % 26)) + s; j //= 26
    return "x" + s


def build_taxonomy_doc(n_nodes, rng, max_depth=8):
    depth = {0: 0}; parent = {0: None}
    for i in range(1, n_nodes):
        cands = [k for k in depth if depth[k] < max_depth]
        w = np.array([depth[k] + 1 for k in cands], float)
        p = int(rng.choice(cands, p=w / w.sum()))
        parent[i] = p; depth[i] = depth[p] + 1
    # render as plain English is-a sentences the conversation can read (alphabetic names only)
    sents = [f"A {nm(i)} is a {nm(parent[i])}." for i in range(1, n_nodes)]
    return parent, depth, " ".join(sents)


def ancestors(parent, x):
    out = []
    while parent[x] is not None:
        out.append(parent[x]); x = parent[x]
    return out


def deep_acc_via_say(conv, parent, n_nodes, seed):
    rng = np.random.default_rng(seed + 100)
    leaves = [k for k in range(n_nodes) if k not in set(parent.values())]; rng.shuffle(leaves)
    sample = leaves[:30]
    correct = 0; total = 0
    for x in sample:
        anc = ancestors(parent, x)
        if not anc:
            continue
        z = anc[min(len(anc) - 1, int(rng.integers(0, len(anc))))]
        ans = conv.say(f"is a {nm(x)} a {nm(z)}?").strip().lower()
        correct += ("yes" in ans); total += 1
    return round(correct / total, 3) if total else None


def neg_acc_via_say(conv, parent, n_nodes, seed):
    rng = np.random.default_rng(seed + 200)
    leaves = [k for k in range(n_nodes) if k not in set(parent.values())]; rng.shuffle(leaves)
    correct = 0; total = 0
    for x in leaves[:30]:
        anc = set(ancestors(parent, x))
        non = [y for y in range(n_nodes) if y != x and y not in anc]
        if not non:
            continue
        z = int(rng.choice(non))
        ans = conv.say(f"is a {nm(x)} a {nm(z)}?").strip().lower()
        correct += ("yes" not in ans); total += 1
    return round(correct / total, 3) if total else None


def run_seed(seed, N=300):
    rng = np.random.default_rng(seed)
    parent, depth, doc = build_taxonomy_doc(N, rng)

    # CONTROL: read but DISABLE auto-consolidation (monkeypatch consolidate to no-op)
    ctrl = Conversation(brain_dir=tempfile.mkdtemp(prefix=f"j372c_{seed}_"), seed=seed)
    ctrl.consolidate = lambda: ctrl                      # disable
    ctrl.read_text(doc)
    ctrl_deep = deep_acc_via_say(ctrl, parent, N, seed)

    # AUTO: real Conversation, auto-consolidates inside read_text
    conv = Conversation(brain_dir=tempfile.mkdtemp(prefix=f"j372a_{seed}_"), seed=seed)
    conv.read_text(doc)
    auto_deep = deep_acc_via_say(conv, parent, N, seed)
    auto_neg = neg_acc_via_say(conv, parent, N, seed)

    # exception: teach a not-is-a and confirm it is still respected after consolidation
    deep_node = next(k for k in range(N) if depth[k] >= 4)
    anc = ancestors(parent, deep_node)
    exc_ok = True
    if len(anc) >= 2:
        conv.say(f"A {nm(deep_node)} is not a {nm(anc[-1])}.")
        conv.consolidate()
        ans = conv.say(f"is a {nm(deep_node)} a {nm(anc[-1])}?").strip().lower()
        exc_ok = ("yes" not in ans)

    # persistence: save -> load -> deep question still reliable
    conv.save()
    reloaded = Conversation(brain_dir=conv.brain_dir, seed=seed)
    reload_deep = deep_acc_via_say(reloaded, parent, N, seed)

    return {"facts": len(conv.sm.facts), "ctrl_deep": ctrl_deep, "auto_deep": auto_deep,
            "auto_neg": auto_neg, "exc_ok": bool(exc_ok), "reload_deep": reload_deep}


def regression(repo):
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-m", "not slow", "tests/test_conversation.py"],
                       capture_output=True, text=True, env={**os.environ, "PYTHONPATH": repo})
    last = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ""
    return ("failed" not in r.stdout and "error" not in r.stdout.lower().split("warnings")[0]), last


if __name__ == "__main__":
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print("=== JEP-372: live Conversation auto-consolidation (end-to-end) ===", flush=True)
    seeds = [0, 7]
    R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]
        print(f"  seed {s}: deep via say() control={r['ctrl_deep']} -> auto={r['auto_deep']} | neg={r['auto_neg']} | "
              f"exception-respected={r['exc_ok']} | reload deep={r['reload_deep']} | facts={r['facts']}", flush=True)
    gate_ok, gate_line = regression(repo)
    print(f"  conversation suite: {gate_ok}  ({gate_line})", flush=True)

    J372a = all(R[s]['auto_deep'] >= 0.95 and R[s]['auto_deep'] >= R[s]['ctrl_deep'] for s in seeds)
    J372b = all(R[s]['exc_ok'] and R[s]['auto_neg'] >= 0.90 for s in seeds)
    J372c = all(R[s]['reload_deep'] >= 0.95 for s in seeds) and gate_ok
    passed = J372a and J372b and J372c
    print("\n--- VERDICT ---", flush=True)
    print(f"J372a deep questions via say() >=0.95 & >= control : {J372a}", flush=True)
    print(f"J372b exceptions respected + negatives >=0.90      : {J372b}", flush=True)
    print(f"J372c persists across save/load + suite green      : {J372c}", flush=True)
    verdict = ("PASS - the live Conversation auto-consolidates after reading a document, so deep questions asked "
               "through say() are answered reliably (>=0.95), exceptions stay respected, and the consolidated brain "
               "persists across save/load -- the within-domain reliability fix is now end-to-end in the deployed talk "
               "loop.") if passed else "NULL/partial - see rows (a bar missed; report honestly, do not retune)."
    print(f"\nJEP-372: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP372"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": R, "gate": gate_ok, "J372a": J372a, "J372b": J372b,
                                                  "J372c": J372c, "passed": passed}, default=str))
    print("DONE", flush=True)
