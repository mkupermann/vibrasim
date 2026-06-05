"""JEP-388 — relational prose: queryable part-of + causal variants. No transformer.
Pre-registered bars in docs/amendments/jep388_relational_prose.md.
"""
import json, tempfile, subprocess, sys, os
from pathlib import Path
from world.conversation import Conversation


def conv(text, seed):
    c = Conversation(brain_dir=tempfile.mkdtemp(prefix=f"j388_{seed}_"), seed=seed)
    c.read_text(text)
    return c


def run_seed(seed):
    # J388a: part-of queryable
    c = conv("A wheel is part of a car.", seed)
    yes = "yes" in c.say("is a wheel part of a car?").strip().lower()
    no = "yes" not in c.say("is a wheel part of a tree?").strip().lower()
    j388a = bool(yes and no)

    # J388b: causal variants
    cv = conv("Viruses cause disease.", seed)
    cm = conv("Smoking can cause cancer.", seed)
    cs = conv("Smoking causes cancer.", seed)
    b1 = ("virus", "causes", "disease") in set(cv.sm.facts)
    b2 = ("smoking", "causes", "cancer") in set(cm.sm.facts)
    b3 = ("smoking", "causes", "cancer") in set(cs.sm.facts)
    qd = "virus" in cv.say("what causes disease?").strip().lower()
    j388b = bool(b1 and b2 and b3 and qd)

    # J388c: 'is a part of' variant + regression
    ce = conv("The engine is a part of the car.", seed)
    e_ok = ("engine", "partof", "car") in set(ce.sm.facts)
    ch = conv("A car has wheels.", seed)
    h_ok = ("wheel", "partof", "car") in set(ch.sm.facts)
    j388c_local = bool(e_ok and h_ok)
    return {"j388a": j388a, "yes": bool(yes), "no": bool(no), "j388b": j388b, "b1": bool(b1), "b2": bool(b2),
            "qd": bool(qd), "e_ok": bool(e_ok), "h_ok": bool(h_ok), "j388c_local": j388c_local}


def suite(repo):
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-m", "not slow", "tests/test_conversation.py"],
                       capture_output=True, text=True, env={**os.environ, "PYTHONPATH": repo})
    last = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ""
    return ("failed" not in r.stdout and "error" not in r.stdout.lower().split("warnings")[0]), last


if __name__ == "__main__":
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print("=== JEP-388: relational prose (part-of query + causal variants) ===", flush=True)
    seeds = [0, 7]
    R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]
        print(f"  seed {s}: J388a part-of-query={r['j388a']} (yes={r['yes']},no={r['no']}) | J388b causal={r['j388b']} "
              f"(virus={r['b1']},can-cause={r['b2']},what-causes={r['qd']}) | J388c engine={r['e_ok']} "
              f"has-wheels={r['h_ok']}", flush=True)
    gate_ok, line = suite(repo)
    print(f"  conversation suite: {gate_ok} ({line})", flush=True)

    J388a = all(R[s]['j388a'] for s in seeds)
    J388b = all(R[s]['j388b'] for s in seeds)
    J388c = all(R[s]['j388c_local'] for s in seeds) and gate_ok
    passed = J388a and J388b and J388c
    print("\n--- VERDICT ---", flush=True)
    print(f"J388a part-of queryable        : {J388a}", flush=True)
    print(f"J388b causal variants          : {J388b}", flush=True)
    print(f"J388c 'is a part of' + suite   : {J388c}", flush=True)
    verdict = ("PASS - stored part-of knowledge is now queryable ('is a wheel part of a car?' -> yes), causal prose "
               "parses in singular/plural/modal forms (+ queryable via 'what causes X?'), and 'is a part of' parses; "
               "suite green. Relational prose beyond taxonomy is now reliable.") if passed else \
              "NULL/partial - see rows (a bar missed; report, do not retune)."
    print(f"\nJEP-388: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP388"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": R, "gate": gate_ok, "J388a": J388a, "J388b": J388b,
                                                  "J388c": J388c, "passed": passed}, default=str))
    print("DONE", flush=True)
