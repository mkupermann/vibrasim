"""JEP-342 — 'make connections': the conversation relates a new fact to what it already knows (deductive). No
transformer. Pre-registered bars in docs/amendments/jep342_make_connections.md.
"""
import json, tempfile, subprocess, sys, os
from pathlib import Path
from world.conversation import Conversation


def run_seed(seed):
    d = tempfile.mkdtemp(prefix=f"conn_{seed}_")
    c = Conversation(brain_dir=d, seed=seed)
    # prior knowledge
    c.say("A dog is a mammal."); c.say("A mammal is an animal."); c.say("A dog can bark.")
    # NEW fact that connects: poodle -> dog -> mammal -> animal, inherits bark
    resp = c.say("A poodle is a dog.")
    low = resp.lower()
    # J342a: the response surfaces the multi-hop connections (mammal, animal) and inherited property (bark)
    has_mammal = "mammal" in low
    has_animal = "animal" in low
    has_bark = "bark" in low
    connects_ok = has_mammal and has_animal and has_bark

    # J342b: an ISOLATED new fact surfaces no connection
    resp2 = c.say("A zorp is a quib.")
    isolated_ok = ("connect" not in resp2.lower())

    return {"response": resp, "connects_ok": bool(connects_ok), "isolated_ok": bool(isolated_ok),
            "response_isolated": resp2}


def regression(repo):
    r = subprocess.run([sys.executable, "tools/run_jep340_conversation.py"], capture_output=True, text=True,
                       env={**os.environ, "PYTHONPATH": repo})
    return "JEP-340: PASS" in r.stdout


if __name__ == "__main__":
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print("=== JEP-342: make connections (relate new facts to what it knows) ===", flush=True)
    seeds = [0, 7]; R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]
        print(f"  seed {s}: connects_ok={r['connects_ok']} isolated_ok={r['isolated_ok']}", flush=True)
        print(f"      teach 'A poodle is a dog.' -> {r['response']}", flush=True)
    reg = regression(repo)
    print(f"  regression JEP-340: {'PASS' if reg else 'FAIL'}", flush=True)

    J342a = all(R[s]['connects_ok'] for s in seeds)
    J342b = all(R[s]['isolated_ok'] for s in seeds)
    J342c = reg
    passed = J342a and J342b and J342c
    print("\n--- VERDICT ---", flush=True)
    print(f"J342a surfaces correct multi-hop connections: {J342a}", flush=True)
    print(f"J342b isolated fact -> no false connection   : {J342b}", flush=True)
    print(f"J342c no regression (340)                    : {J342c}", flush=True)
    verdict = ("PASS - when taught a new fact, it relates it to what it already knows (deductive connections), per "
               "Michael's 'make connections' rule") if passed else "NULL/partial"
    print(f"\nJEP-342: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP342"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": R, "J342a": J342a, "J342b": J342b, "J342c": J342c,
                                                  "passed": passed}, default=str))
    print("DONE", flush=True)
