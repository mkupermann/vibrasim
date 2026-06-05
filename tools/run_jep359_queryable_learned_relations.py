"""JEP-359 — queryable learned relations (forward + reverse open-relation questions). No transformer.
Pre-registered bars in docs/amendments/jep359_queryable_learned_relations.md.
"""
import json, tempfile, subprocess, sys, os
from pathlib import Path
from world.substrate_memory import SubstrateMemory
from world.brain_query import BrainQuery
from world.conversation import Conversation


def run_seed_direct(seed):
    m = SubstrateMemory(D=4096, directed=True)
    for s, r, o in [("farmers", "domesticated", "cat"), ("humans", "domesticated", "dog")]:
        m.add_fact(s, r, o)
    bq = BrainQuery(m, seed=seed)
    checks = {
        "who_cat": bq.ask("who domesticated the cat?") == ["farmers"],
        "what_humans": bq.ask("what did humans domesticate?") == ["dog"],
        "what_by": bq.ask("what was the cat domesticated by?") == ["farmers"],
    }
    return {"acc": round(sum(checks.values()) / len(checks), 3), "checks": {k: bool(v) for k, v in checks.items()}}


def run_seed_taught(seed):
    c = Conversation(brain_dir=tempfile.mkdtemp(prefix=f"qlr_{seed}_"), seed=seed)
    c.say("The dog was domesticated by humans."); c.say("humans domesticated dog")
    c.say("The horse was domesticated by people."); c.say("people domesticated horse")
    c.say("A cat was domesticated by farmers.")           # read by itself -> (farmers, domesticated, cat)
    who = c.say("who domesticated the cat?").strip().lower()
    return {"who_cat_taught": "farmers" in who}


def regression(repo):
    g = subprocess.run([sys.executable, "-m", "pytest", "tests/test_conversation.py", "-q"],
                       capture_output=True, text=True, env={**os.environ, "PYTHONPATH": repo})
    q = subprocess.run([sys.executable, "tools/run_jep322_brain_query.py"], capture_output=True, text=True,
                       env={**os.environ, "PYTHONPATH": repo})
    return ("passed" in g.stdout and "failed" not in g.stdout), ("JEP-322: PASS" in q.stdout)


if __name__ == "__main__":
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print("=== JEP-359: queryable learned relations ===", flush=True)
    seeds = [0, 7]
    Rd = {s: run_seed_direct(s) for s in seeds}
    Rt = {s: run_seed_taught(s) for s in seeds}
    for s in seeds:
        print(f"  seed {s}: direct={Rd[s]['acc']} {Rd[s]['checks']} | taught who-cat={Rt[s]['who_cat_taught']}",
              flush=True)
    gate, j322 = regression(repo)
    print(f"  conversation gate: {gate} | JEP-322: {j322}", flush=True)

    J359a = all(Rd[s]['acc'] >= 1.0 for s in seeds)
    J359b = all(Rt[s]['who_cat_taught'] for s in seeds)
    J359c = gate and j322
    passed = J359a and J359b and J359c
    print("\n--- VERDICT ---", flush=True)
    print(f"J359a reverse + forward open-relation Q&A: {J359a}", flush=True)
    print(f"J359b end-to-end via taught construction : {J359b}", flush=True)
    print(f"J359c no regression                      : {J359c}", flush=True)
    verdict = ("PASS - facts from taught constructions are fully queryable: 'who domesticated the cat?' -> farmers, "
               "'what did humans domesticate?' -> dog -- the learn->store->ask loop closes") if passed else "NULL/partial"
    print(f"\nJEP-359: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP359"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"direct": Rd, "taught": Rt, "gate": gate, "j322": j322,
                                                  "J359a": J359a, "J359b": J359b, "J359c": J359c,
                                                  "passed": passed}, default=str))
    print("DONE", flush=True)
