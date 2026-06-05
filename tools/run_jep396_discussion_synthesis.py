"""JEP-396 — discussion: synthesize what was learned ('tell me about X'), including parts. No transformer.
Pre-registered bars in docs/amendments/jep396_discussion_synthesis.md.
"""
import json, tempfile, subprocess, sys, os
from pathlib import Path
from world.conversation import Conversation

ARTICLE = ("A poodle is a kind of dog. A dog is a mammal. A mammal is an animal. A dog has four legs. "
           "A dog can bark. A tail is part of a dog. A leg is part of a dog.")


def run_seed(seed):
    c = Conversation(brain_dir=tempfile.mkdtemp(prefix=f"j396_{seed}_"), seed=seed)
    c.read_text(ARTICLE)
    about_poodle = c.say("tell me about a poodle").strip().lower()
    about_dog = c.say("tell me about a dog").strip().lower()
    # J396a: class + property + count
    j396a = ("dog" in about_poodle and "bark" in about_poodle and "4 legs" in about_poodle)
    # J396b: parts
    j396b = ("tail" in about_dog)
    # J396c: a concept with no parts describes cleanly (no malformed 'it has .')
    c2 = Conversation(brain_dir=tempfile.mkdtemp(prefix=f"j396b_{seed}_"), seed=seed)
    c2.read_text("A rose is a flower. A flower is a plant.")
    about_rose = c2.say("tell me about a rose").strip().lower()
    clean = ("flower" in about_rose) and ("it has ." not in about_rose) and ("has  " not in about_rose)
    return {"about_poodle": about_poodle, "about_dog": about_dog, "j396a": bool(j396a), "j396b": bool(j396b),
            "about_rose": about_rose, "clean": bool(clean)}


def suite(repo):
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-m", "not slow", "tests/test_conversation.py"],
                       capture_output=True, text=True, env={**os.environ, "PYTHONPATH": repo})
    last = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ""
    return ("failed" not in r.stdout and "error" not in r.stdout.lower().split("warnings")[0]), last


if __name__ == "__main__":
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print("=== JEP-396: discussion synthesis (tell me about X, incl parts) ===", flush=True)
    seeds = [0, 7]
    R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]
        print(f"  seed {s}: poodle={r['about_poodle']!r} | dog={r['about_dog']!r} | rose={r['about_rose']!r}",
              flush=True)
        print(f"           J396a={r['j396a']} J396b(parts)={r['j396b']} J396c(clean)={r['clean']}", flush=True)
    gate_ok, line = suite(repo)
    print(f"  conversation suite: {gate_ok} ({line})", flush=True)

    J396a = all(R[s]['j396a'] for s in seeds)
    J396b = all(R[s]['j396b'] for s in seeds)
    J396c = all(R[s]['clean'] for s in seeds) and gate_ok
    passed = J396a and J396b and J396c
    print("\n--- VERDICT ---", flush=True)
    print(f"J396a class+property+count : {J396a}", flush=True)
    print(f"J396b parts included       : {J396b}", flush=True)
    print(f"J396c clean + suite        : {J396c}", flush=True)
    verdict = ("PASS - 'tell me about X' synthesizes what the substrate read: class + inherited property + count + "
               "parts ('a dog ... it has a tail, a leg'), and a partless concept still describes cleanly; suite green. "
               "The discussion half of Michael's vision works on real prose.") if passed else \
              "NULL/partial - see rows (a bar missed; report, do not retune)."
    print(f"\nJEP-396: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP396"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": R, "gate": gate_ok, "J396a": J396a, "J396b": J396b,
                                                  "J396c": J396c, "passed": passed}, default=str))
    print("DONE", flush=True)
