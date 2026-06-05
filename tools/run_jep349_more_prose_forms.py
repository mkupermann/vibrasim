"""JEP-349 — more prose forms (conjunctions, relative clauses, locational). No transformer.
Pre-registered bars in docs/amendments/jep349_more_prose_forms.md.
"""
import json, tempfile, subprocess, sys, os
from pathlib import Path
from world.conversation import Conversation
from world.brain_query import BrainQuery


def climb_loc(mem, x, y, g):
    from collections import deque
    q, seen, n = deque([x]), {x}, 0
    while q and n < 20:
        cur = q.popleft(); n += 1
        for (p, _) in mem.query_all(cur, "located_in", g):
            if p == y:
                return True
            if p not in seen:
                seen.add(p); q.append(p)
    return False


def run_seed(seed):
    c = Conversation(brain_dir=tempfile.mkdtemp(prefix=f"forms_{seed}_"), seed=seed)
    c._learn_one("Cats and dogs are mammals.")
    c._learn_one("A poodle, which is a dog, can bark.")
    c._learn_one("Paris is in France.")
    c._learn_one("France is in Europe.")
    bq = BrainQuery(c.sm, seed=seed)
    g = bq.gate
    checks = {
        "conj_cat": bq.is_a("cat", "mammal") is True,
        "conj_dog": bq.is_a("dog", "mammal") is True,
        "relclause_isa": bq.is_a("poodle", "dog") is True,
        "relclause_prop": bq.has_property("poodle", "bark") is True,
        "locational": climb_loc(c.sm, "paris", "france", g),
        "locational_multihop": climb_loc(c.sm, "paris", "europe", g),
    }
    return {"acc": round(sum(checks.values()) / len(checks), 3), "checks": {k: bool(v) for k, v in checks.items()}}


def regression(repo):
    outs = {}
    for name in ["run_jep347_realistic_prose_coverage", "run_jep348_prose_normalizer"]:
        r = subprocess.run([sys.executable, f"tools/{name}.py"], capture_output=True, text=True,
                           env={**os.environ, "PYTHONPATH": repo})
        num = name.split("jep")[1][:3]
        outs[num] = f"JEP-{num}: PASS" in r.stdout
    g = subprocess.run([sys.executable, "-m", "pytest", "tests/test_conversation.py",
                        "tests/test_substrate_memory.py", "-q"], capture_output=True, text=True,
                       env={**os.environ, "PYTHONPATH": repo})
    outs["gate"] = "passed" in g.stdout and "failed" not in g.stdout
    return outs


if __name__ == "__main__":
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print("=== JEP-349: more prose forms (conjunction / relative clause / locational) ===", flush=True)
    seeds = [0, 7]; R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        print(f"  seed {s}: acc={R[s]['acc']} | {R[s]['checks']}", flush=True)
    reg = regression(repo)
    print(f"  regression: {reg}", flush=True)
    J349a = all(R[s]['acc'] >= 1.0 for s in seeds)
    J349bc = all(reg.values())
    passed = J349a and J349bc
    print("\n--- VERDICT ---", flush=True)
    print(f"J349a new forms all work          : {J349a}", flush=True)
    print(f"J349b/c no regression (347/348/gate): {J349bc}", flush=True)
    verdict = ("PASS - conjunction subjects, relative clauses, and locational forms now parse; prior coverage + "
               "gates intact") if passed else "NULL/partial"
    print(f"\nJEP-349: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP349"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": R, "reg": reg, "J349a": J349a, "J349bc": J349bc,
                                                  "passed": passed}, default=str))
    print("DONE", flush=True)
