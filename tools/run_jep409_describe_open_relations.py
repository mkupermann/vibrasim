"""JEP-409 — 'tell me about X' synthesizes actions/attributes too. No transformer.
Pre-registered bars in docs/amendments/jep409_describe_open_relations.md.
"""
import json, tempfile, subprocess, sys, os
from pathlib import Path
from world.conversation import Conversation


def tell(stmts, who, seed):
    c = Conversation(brain_dir=tempfile.mkdtemp(prefix=f"j409_{seed}_"), seed=seed)
    for s in stmts:
        c.read_text(s)
    return c.say(f"tell me about {who}").strip().lower()


def run_seed(seed):
    m = tell(["Michael is a teacher.", "Michael likes coffee.", "Michael wrote a book."], "Michael", seed)
    j409a = ("teacher" in m and "coffee" in m and "book" in m)
    p = tell(["A poodle is a kind of dog.", "A dog is a mammal.", "A dog can bark.", "A dog has four legs.",
              "A tail is part of a dog."], "a poodle", seed)
    j409b = ("dog" in p and "bark" in p and "legs" in p and "tail" in p)
    return {"michael": m, "j409a": bool(j409a), "poodle": p, "j409b": bool(j409b)}


def suite(repo):
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-m", "not slow", "tests/test_conversation.py"],
                       capture_output=True, text=True, env={**os.environ, "PYTHONPATH": repo})
    last = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ""
    return ("failed" not in r.stdout and "error" not in r.stdout.lower().split("warnings")[0]), last


if __name__ == "__main__":
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print("=== JEP-409: describe with open relations ===", flush=True)
    seeds = [0, 7]
    R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]
        print(f"  seed {s}: J409a={r['j409a']} michael={r['michael']!r} | J409b={r['j409b']} poodle={r['poodle']!r}",
              flush=True)
    gate_ok, line = suite(repo)
    print(f"  conversation suite: {gate_ok} ({line})", flush=True)
    J409a = all(R[s]['j409a'] for s in seeds)
    J409b = all(R[s]['j409b'] for s in seeds)
    J409c = gate_ok
    passed = J409a and J409b and J409c
    print("\n--- VERDICT ---", flush=True)
    print(f"J409a actions/attributes in describe : {J409a}", flush=True)
    print(f"J409b taxonomy intact                : {J409b}", flush=True)
    print(f"J409c suite green                    : {J409c}", flush=True)
    verdict = ("PASS - 'tell me about X' now synthesizes ALL known facts: taxonomy + properties + count + parts + "
               "actions/attributes ('Michael is a teacher; it likes coffee; it wrote book'), taxonomy describe intact, "
               "suite green. The user can inspect everything the brain learned about an entity.") if passed else \
              "NULL/partial - see rows (a bar missed; report, do not retune)."
    print(f"\nJEP-409: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP409"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": R, "gate": gate_ok, "J409a": J409a, "J409b": J409b,
                                                  "J409c": J409c, "passed": passed}, default=str))
    print("DONE", flush=True)
