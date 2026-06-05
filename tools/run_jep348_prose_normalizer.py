"""JEP-348 — widen prose coverage with a sentence normalizer. No transformer.
Pre-registered bars in docs/amendments/jep348_prose_normalizer.md.
"""
import json, tempfile, subprocess, sys, os
from pathlib import Path
import numpy as np
from world.conversation import Conversation
from world.brain_query import BrainQuery


def run_seed(seed):
    d = tempfile.mkdtemp(prefix=f"norm_{seed}_")
    c = Conversation(brain_dir=d, seed=seed)
    for s in ["A poodle is a kind of dog.", "Dogs are carnivores.", "A dog has four legs.",
              "A dog is a mammal.", "A mammal is an animal."]:
        c._learn_one(s)
    bq = BrainQuery(c.sm, seed=seed)
    checks = {
        "kind_of": bq.is_a("poodle", "dog") is True,
        "plural_isa": bq.is_a("dog", "carnivore") is True,
        "numeric": bq.how_many("dog") == 4,
        "multihop_still": bq.is_a("poodle", "animal") is True,
    }
    return {"acc": round(sum(checks.values()) / len(checks), 3), "checks": {k: bool(v) for k, v in checks.items()}}


def coverage(repo):
    r = subprocess.run([sys.executable, "tools/run_jep347_realistic_prose_coverage.py"], capture_output=True,
                       text=True, env={**os.environ, "PYTHONPATH": repo})
    # parse 'parse coverage=X'
    import re
    covs = [float(x) for x in re.findall(r"parse coverage=([0-9.]+)", r.stdout)]
    qas = [float(x) for x in re.findall(r"Q&A=([0-9.]+)", r.stdout)]
    return (min(covs) if covs else 0.0), (min(qas) if qas else 0.0)


def regression(repo):
    outs = {}
    for name in ["run_jep340_conversation", "run_jep345_conversational_robustness", "run_jep346_read_document_and_gaps"]:
        r = subprocess.run([sys.executable, f"tools/{name}.py"], capture_output=True, text=True,
                           env={**os.environ, "PYTHONPATH": repo})
        num = name.split("jep")[1][:3]
        outs[num] = f"JEP-{num}: PASS" in r.stdout
    return outs


if __name__ == "__main__":
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print("=== JEP-348: prose normalizer widens coverage ===", flush=True)
    seeds = [0, 7]; R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        print(f"  seed {s}: the-3-forms acc={R[s]['acc']} | {R[s]['checks']}", flush=True)
    cov, qa = coverage(repo)
    reg = regression(repo)
    print(f"  JEP-347 re-run: coverage={cov} Q&A={qa} | regression: {reg}", flush=True)

    J348a = all(R[s]['acc'] >= 1.0 for s in seeds)
    J348b = cov >= 0.90 and qa >= 0.90
    J348c = all(reg.values())
    passed = J348a and J348b and J348c
    print("\n--- VERDICT ---", flush=True)
    print(f"J348a the 3 missed forms now work : {J348a}", flush=True)
    print(f"J348b coverage up to >=0.90       : {J348b} (cov={cov})", flush=True)
    print(f"J348c no regression               : {J348c}", flush=True)
    verdict = ("PASS - the normalizer lifts realistic-prose coverage (plural is-a, 'kind of', numeric possession now "
               "parse), no regression") if passed else "NULL/partial"
    print(f"\nJEP-348: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP348"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": R, "coverage": cov, "qa": qa, "reg": reg,
                                                  "J348a": J348a, "J348b": J348b, "J348c": J348c,
                                                  "passed": passed}, default=str))
    print("DONE", flush=True)
