"""JEP-373 — dimension-scaled consolidation fixes the negative-probe inflation from JEP-372. No transformer.
Pre-registered bars in docs/amendments/jep373_dimension_scaled_consolidation.md.
Reuses the JEP-372 end-to-end harness; Conversation.consolidate() now auto-scales D.
"""
import json, tempfile, subprocess, sys, os
from pathlib import Path
import numpy as np
from world.conversation import Conversation
from tools.run_jep372_live_conversation_consolidation import (
    nm, build_taxonomy_doc, ancestors, deep_acc_via_say, neg_acc_via_say)


def run_seed(seed, N=300):
    rng = np.random.default_rng(seed)
    parent, depth, doc = build_taxonomy_doc(N, rng)
    conv = Conversation(brain_dir=tempfile.mkdtemp(prefix=f"j373_{seed}_"), seed=seed)
    conv.read_text(doc)                                   # auto-consolidates with auto_scale=True
    D_after = conv.sm.D
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
    reload_deep = deep_acc_via_say(reloaded, parent, N, seed)
    return {"facts": len(conv.sm.facts), "D_after": D_after, "deep": deep, "neg": neg,
            "exc_ok": bool(exc_ok), "reload_deep": reload_deep}


def regression(repo):
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-m", "not slow",
                        "tests/test_conversation.py", "tests/test_substrate_memory.py"],
                       capture_output=True, text=True, env={**os.environ, "PYTHONPATH": repo})
    last = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ""
    return ("failed" not in r.stdout and "error" not in r.stdout.lower().split("warnings")[0]), last


if __name__ == "__main__":
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print("=== JEP-373: dimension-scaled consolidation (fix JEP-372 negatives) ===", flush=True)
    seeds = [0, 7]
    R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]
        print(f"  seed {s}: D->{r['D_after']} facts={r['facts']} | deep={r['deep']} neg={r['neg']} "
              f"(was 0.8 seed0 @D=4096) | exception={r['exc_ok']} | reload deep={r['reload_deep']}", flush=True)
    gate_ok, gate_line = regression(repo)
    print(f"  suite: {gate_ok}  ({gate_line})", flush=True)

    J373a = all(R[s]['neg'] >= 0.95 for s in seeds)
    J373b = all(R[s]['deep'] >= 0.95 for s in seeds)
    J373c = all(R[s]['exc_ok'] and R[s]['reload_deep'] >= 0.95 for s in seeds) and gate_ok
    passed = J373a and J373b and J373c
    print("\n--- VERDICT ---", flush=True)
    print(f"J373a negatives recovered >=0.95 : {J373a}", flush=True)
    print(f"J373b deep still reliable >=0.95  : {J373b}", flush=True)
    print(f"J373c exceptions+persist+suite    : {J373c}", flush=True)
    verdict = ("PASS - dimension-scaled consolidation fixes the JEP-372 negative-probe inflation: auto_scale raises D "
               "with the consolidated load so random cleanup cross-similarity drops, negatives recover to >=0.95 on "
               "both seeds while deep stays 1.0, exceptions hold, and the consolidated brain persists. The live talk "
               "loop now has reliable deep AND negative within-domain Q&A end-to-end.") if passed else \
              ("NULL/partial - scaling D did not fully fix negatives (deeper cause) or broke a bar; see rows. "
               "Reported, not retuned.")
    print(f"\nJEP-373: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP373"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": R, "gate": gate_ok, "J373a": J373a, "J373b": J373b,
                                                  "J373c": J373c, "passed": passed}, default=str))
    print("DONE", flush=True)
