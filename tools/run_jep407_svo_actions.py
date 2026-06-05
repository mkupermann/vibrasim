"""JEP-407 — action facts: SVO + 'what does X have/verb?' queries. No transformer.
Pre-registered bars in docs/amendments/jep407_svo_actions.md.
"""
import json, tempfile, subprocess, sys, os
from pathlib import Path
from world.conversation import Conversation


def trial(stmts, q, seed):
    c = Conversation(brain_dir=tempfile.mkdtemp(prefix=f"j407_{seed}_"), seed=seed)
    for s in stmts:
        c.read_text(s)
    return c.say(q).strip().lower()


def facts_of(text, seed):
    c = Conversation(brain_dir=tempfile.mkdtemp(prefix=f"j407f_{seed}_"), seed=seed)
    c.read_text(text)
    return set(c.sm.facts)


def run_seed(seed):
    a1 = "coffee" in trial(["Michael likes coffee."], "what does Michael like?", seed)
    a2 = "meat" in trial(["Dogs eat meat."], "what do dogs eat?", seed)
    j407a = a1 and a2

    have = trial(["A dog has a tail.", "A dog has legs."], "what does a dog have?", seed)
    j407b = ("tail" in have and "leg" in have)

    # no wrong capture + no regression
    f1 = facts_of("A dog is a mammal.", seed)
    isa_ok = ("dog", "isa", "mammal") in f1 and not any(r not in ("isa",) for (a, r, b) in f1)
    sun = "yes" in trial(["The sun is hot."], "is the sun hot?", seed)
    mh = "yes" in trial(["A poodle is a dog.", "A dog is a mammal."], "is a poodle a mammal?", seed)
    j407c_local = isa_ok and sun and mh
    return {"j407a": bool(j407a), "a1": bool(a1), "a2": bool(a2), "have": have, "j407b": bool(j407b),
            "isa_ok": bool(isa_ok), "sun": bool(sun), "mh": bool(mh), "j407c_local": bool(j407c_local)}


def suite(repo):
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-m", "not slow", "tests/test_conversation.py"],
                       capture_output=True, text=True, env={**os.environ, "PYTHONPATH": repo})
    last = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ""
    return ("failed" not in r.stdout and "error" not in r.stdout.lower().split("warnings")[0]), last


if __name__ == "__main__":
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print("=== JEP-407: SVO action facts + queries ===", flush=True)
    seeds = [0, 7]
    R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]
        print(f"  seed {s}: J407a SVO={r['j407a']} (like-coffee={r['a1']},dogs-eat={r['a2']}) | J407b have={r['j407b']} "
              f"({r['have']!r}) | J407c isa-only={r['isa_ok']} sun={r['sun']} mh={r['mh']}", flush=True)
    gate_ok, line = suite(repo)
    print(f"  conversation suite: {gate_ok} ({line})", flush=True)

    J407a = all(R[s]['j407a'] for s in seeds)
    J407b = all(R[s]['j407b'] for s in seeds)
    J407c = all(R[s]['j407c_local'] for s in seeds) and gate_ok
    passed = J407a and J407b and J407c
    print("\n--- VERDICT ---", flush=True)
    print(f"J407a SVO action + query : {J407a}", flush=True)
    print(f"J407b parts query        : {J407b}", flush=True)
    print(f"J407c no wrong + suite   : {J407c}", flush=True)
    verdict = ("PASS - action facts work: 'Michael likes coffee' -> 'what does Michael like?' -> coffee; 'Dogs eat "
               "meat' -> 'what do dogs eat?' -> meat; 'what does a dog have?' lists parts; is-a/property NOT mis-"
               "captured as SVO, multi-hop intact, suite green. Natural action statements now teachable in the GUI.") \
        if passed else "NULL/partial - see rows (a bar missed; report, do not retune)."
    print(f"\nJEP-407: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP407"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": R, "gate": gate_ok, "J407a": J407a, "J407b": J407b,
                                                  "J407c": J407c, "passed": passed}, default=str))
    print("DONE", flush=True)
