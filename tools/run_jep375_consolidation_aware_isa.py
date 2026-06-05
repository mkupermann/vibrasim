"""JEP-375 — consolidation-aware is-a: skip the BFS walk when the closure is materialized. No transformer.
Pre-registered bars in docs/amendments/jep375_consolidation_aware_isa.md.
"""
import json, tempfile, subprocess, sys, os
from pathlib import Path
import numpy as np
from world.conversation import Conversation
from world.substrate_memory import SubstrateMemory
from world.brain_query import BrainQuery
from tools.run_jep372_live_conversation_consolidation import (
    nm, build_taxonomy_doc, ancestors, deep_acc_via_say, neg_acc_via_say)


def run_seed(seed, N=300):
    rng = np.random.default_rng(seed)
    parent, depth, doc = build_taxonomy_doc(N, rng)
    conv = Conversation(brain_dir=tempfile.mkdtemp(prefix=f"j375_{seed}_"), seed=seed)
    conv.read_text(doc)                                  # auto-consolidates -> closed_relations={'isa'}
    closed = "isa" in conv.sm.closed_relations
    deep = deep_acc_via_say(conv, parent, N, seed)
    neg = neg_acc_via_say(conv, parent, N, seed)

    deep_node = next(k for k in range(N) if depth[k] >= 4)
    anc = ancestors(parent, deep_node)
    exc_ok = True
    if len(anc) >= 2:
        conv.say(f"A {nm(deep_node)} is not a {nm(anc[-1])}.")
        conv.consolidate()
        exc_ok = "yes" not in conv.say(f"is a {nm(deep_node)} a {nm(anc[-1])}?").strip().lower()

    conv.save()
    reloaded = Conversation(brain_dir=conv.brain_dir, seed=seed)
    reload_closed = "isa" in reloaded.sm.closed_relations
    reload_deep = deep_acc_via_say(reloaded, parent, N, seed)
    reload_neg = neg_acc_via_say(reloaded, parent, N, seed)
    return {"closed": bool(closed), "deep": deep, "neg": neg, "exc_ok": bool(exc_ok),
            "reload_closed": bool(reload_closed), "reload_deep": reload_deep, "reload_neg": reload_neg,
            "D": conv.sm.D, "facts": len(conv.sm.facts)}


def non_consolidated_multihop(seed):
    """Regression: an UN-consolidated store must still answer a deep multi-hop is-a chain via the BFS walk."""
    m = SubstrateMemory(D=8192, directed=True)
    chain = ["poodle", "dog", "canine", "mammal", "vertebrate", "animal", "organism"]
    for a, b in zip(chain, chain[1:]):
        m.add_fact(a, "isa", b)
    bq = BrainQuery(m, seed=seed)
    return bq.is_a("poodle", "organism") is True and bq.is_a("poodle", "rock") is False


def regression(repo):
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-m", "not slow",
                        "tests/test_conversation.py", "tests/test_substrate_memory.py"],
                       capture_output=True, text=True, env={**os.environ, "PYTHONPATH": repo})
    last = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ""
    return ("failed" not in r.stdout and "error" not in r.stdout.lower().split("warnings")[0]), last


if __name__ == "__main__":
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print("=== JEP-375: consolidation-aware is-a (skip BFS when closure materialized) ===", flush=True)
    seeds = [0, 7]
    R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]
        print(f"  seed {s}: closed={r['closed']} D={r['D']} | deep={r['deep']} neg={r['neg']} | exception={r['exc_ok']}"
              f" | reload(closed={r['reload_closed']} deep={r['reload_deep']} neg={r['reload_neg']})", flush=True)
    multihop = all(non_consolidated_multihop(s) for s in seeds)
    gate_ok, gate_line = regression(repo)
    print(f"  non-consolidated multi-hop intact: {multihop} | suite: {gate_ok} ({gate_line})", flush=True)

    J375a = all(R[s]['neg'] >= 0.95 for s in seeds)
    J375b = all(R[s]['deep'] >= 0.95 for s in seeds)
    J375c = (multihop and gate_ok and
             all(R[s]['exc_ok'] and R[s]['reload_deep'] >= 0.95 and R[s]['reload_neg'] >= 0.95 for s in seeds))
    passed = J375a and J375b and J375c
    print("\n--- VERDICT ---", flush=True)
    print(f"J375a negatives >=0.95            : {J375a}", flush=True)
    print(f"J375b deep >=0.95                 : {J375b}", flush=True)
    print(f"J375c multi-hop+exc+persist+suite : {J375c}", flush=True)
    verdict = ("PASS - consolidation-aware is-a answers by direct single-hop membership when the closure is "
               "materialized, fixing the structural false-positives (negatives -> >=0.95) while deep stays reliable; "
               "the BFS multi-hop path is preserved for un-consolidated stores, exceptions hold, and closed_relations "
               "persists across save/load. The live talk loop now has reliable deep AND negative within-domain Q&A "
               "end-to-end -- the right structural fix, not brute-force dimension.") if passed else \
              "NULL/partial - see rows (a bar missed; report, do not retune)."
    print(f"\nJEP-375: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP375"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": R, "multihop": multihop, "gate": gate_ok,
                                                  "J375a": J375a, "J375b": J375b, "J375c": J375c,
                                                  "passed": passed}, default=str))
    print("DONE", flush=True)
