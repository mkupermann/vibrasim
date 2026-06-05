"""JEP-385 — capture passive-voice facts. No transformer.
Pre-registered bars in docs/amendments/jep385_passive_voice.md.
"""
import json, tempfile, subprocess, sys, os
from pathlib import Path
from world.conversation import Conversation


def learn(text, seed):
    c = Conversation(brain_dir=tempfile.mkdtemp(prefix=f"j385_{seed}_"), seed=seed)
    c.read_text(text)
    return c


def run_seed(seed):
    c1 = learn("Rabbits are hunted by foxes.", seed)
    c2 = learn("Salmon is eaten by bears.", seed)
    a1 = ("fox", "hunted", "rabbit") in set(c1.sm.facts)
    a2 = ("bear", "eaten", "salmon") in set(c2.sm.facts)
    j385a = bool(a1 and a2)

    # queryable end-to-end
    ans = c1.say("what was the rabbit hunted by?").strip().lower()
    j385b = "fox" in ans

    # no false fire + regression
    cm = learn("A dog is a mammal.", seed)
    cl = learn("Paris is located in France.", seed)
    no_false = (("dog", "isa", "mammal") in set(cm.sm.facts)
                and ("paris", "located_in", "france") in set(cl.sm.facts)
                and not any(r in ("is", "located") for (_, r, _) in cm.sm.facts))
    return {"j385a": j385a, "a1": bool(a1), "a2": bool(a2), "ans": ans, "j385b": bool(j385b),
            "no_false": bool(no_false), "facts1": sorted(c1.sm.facts)}


def suite(repo):
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-m", "not slow", "tests/test_conversation.py"],
                       capture_output=True, text=True, env={**os.environ, "PYTHONPATH": repo})
    last = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ""
    return ("failed" not in r.stdout and "error" not in r.stdout.lower().split("warnings")[0]), last


if __name__ == "__main__":
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print("=== JEP-385: passive voice ===", flush=True)
    seeds = [0, 7]
    R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]
        print(f"  seed {s}: J385a passive-extract={r['j385a']} (fox/rabbit={r['a1']}, bear/salmon={r['a2']}) | "
              f"J385b query='{r['ans']}' ({r['j385b']}) | J385c no-false+reg={r['no_false']}", flush=True)
    gate_ok, line = suite(repo)
    print(f"  conversation suite: {gate_ok} ({line})", flush=True)

    J385a = all(R[s]['j385a'] for s in seeds)
    J385b = all(R[s]['j385b'] for s in seeds)
    J385c = all(R[s]['no_false'] for s in seeds) and gate_ok
    passed = J385a and J385b and J385c
    print("\n--- VERDICT ---", flush=True)
    print(f"J385a passive extracted        : {J385a}", flush=True)
    print(f"J385b queryable end-to-end     : {J385b}", flush=True)
    print(f"J385c no false-fire + suite    : {J385c}", flush=True)
    verdict = ("PASS - passive-voice sentences ('X is <participle> by Y') now yield a queryable agent->patient open "
               "relation answerable via 'what was X <verb> by?', without firing on copular/locational sentences; suite "
               "green. More real prose captured (extraction, not active<->passive unification).") if passed else \
              "NULL/partial - see rows (a bar missed; report, do not retune)."
    print(f"\nJEP-385: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP385"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": R, "gate": gate_ok, "J385a": J385a, "J385b": J385b,
                                                  "J385c": J385c, "passed": passed}, default=str))
    print("DONE", flush=True)
