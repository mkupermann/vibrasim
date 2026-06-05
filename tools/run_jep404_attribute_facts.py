"""JEP-404 — teach attribute/possessive facts in natural language. No transformer.
Pre-registered bars in docs/amendments/jep404_attribute_facts.md.
"""
import json, tempfile, subprocess, sys, os
from pathlib import Path
from world.conversation import Conversation


def conv(seed):
    return Conversation(brain_dir=tempfile.mkdtemp(prefix=f"j404_{seed}_"), seed=seed)


def run_seed(seed):
    c = conv(seed)
    c.read_text("Your creator is Michael Kupermann. Your name is EQMOD.")
    who_creator = c.say("who is your creator?").strip().lower()
    what_name = c.say("what is your name?").strip().lower()
    j404a = ("michael kupermann" in who_creator and "eqmod" in what_name)

    c2 = conv(seed)
    c2.read_text("The capital of France is Paris. The name of your creator is Michael Kupermann.")
    cap = c2.say("what is the capital of France?").strip().lower()
    no_junk = not any(" " in a for (a, r, b) in c2.sm.facts)        # no 'capital of france' junk subject
    name_creator = c2.say("what is the name of your creator?").strip().lower()
    j404b = ("paris" in cap and no_junk and "michael kupermann" in name_creator)

    c3 = conv(seed)
    c3.read_text("A poodle is a dog.")
    isa_ok = "yes" in c3.say("is a poodle a dog?").strip().lower()
    return {"who_creator": who_creator, "what_name": what_name, "j404a": bool(j404a),
            "cap": cap, "no_junk": bool(no_junk), "name_creator": name_creator, "j404b": bool(j404b),
            "isa_ok": bool(isa_ok), "facts2": sorted(c2.sm.facts)}


def suite(repo):
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-m", "not slow", "tests/test_conversation.py"],
                       capture_output=True, text=True, env={**os.environ, "PYTHONPATH": repo})
    last = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ""
    return ("failed" not in r.stdout and "error" not in r.stdout.lower().split("warnings")[0]), last


if __name__ == "__main__":
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print("=== JEP-404: attribute/possessive facts ===", flush=True)
    seeds = [0, 7]
    R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]
        print(f"  seed {s}: who-creator={r['who_creator']!r} name={r['what_name']!r} (J404a={r['j404a']}) | "
              f"capital={r['cap']!r} no-junk={r['no_junk']} name-of-creator={r['name_creator']!r} (J404b={r['j404b']}) "
              f"| isa={r['isa_ok']}", flush=True)
    gate_ok, line = suite(repo)
    print(f"  conversation suite: {gate_ok} ({line})", flush=True)

    J404a = all(R[s]['j404a'] for s in seeds)
    J404b = all(R[s]['j404b'] for s in seeds)
    J404c = all(R[s]['isa_ok'] for s in seeds) and gate_ok
    passed = J404a and J404b and J404c
    print("\n--- VERDICT ---", flush=True)
    print(f"J404a teach+query self/attribute : {J404a}", flush=True)
    print(f"J404b of/possessive + no junk    : {J404b}", flush=True)
    print(f"J404c is-a intact + suite        : {J404c}", flush=True)
    verdict = ("PASS - attribute/possessive facts are teachable in natural language and queryable: 'Your creator is "
               "Michael Kupermann' -> 'who is your creator?' -> Michael Kupermann; 'The capital of France is Paris' -> "
               "Paris (no junk is-a); is-a intact, suite green. Michael can now teach the substrate detailed/personal "
               "facts in the GUI.") if passed else "NULL/partial - see rows (a bar missed; report, do not retune)."
    print(f"\nJEP-404: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP404"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": R, "gate": gate_ok, "J404a": J404a, "J404b": J404b,
                                                  "J404c": J404c, "passed": passed}, default=str))
    print("DONE", flush=True)
