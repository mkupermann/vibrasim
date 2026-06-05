"""JEP-397 — most-specific parent selection. No transformer.
Pre-registered bars in docs/amendments/jep397_most_specific_parent.md.
"""
import json, tempfile, subprocess, sys, os
from pathlib import Path
from world.conversation import Conversation


def conv(text, seed):
    c = Conversation(brain_dir=tempfile.mkdtemp(prefix=f"j397_{seed}_"), seed=seed)
    c.read_text(text)
    return c


def run_seed(seed):
    c1 = conv("A rose is a flower. A flower is a plant.", seed)
    what_rose = c1.say("what is a rose?").strip().lower()
    desc_rose = c1.say("tell me about a rose").strip().lower()
    j397a = ("flower" in what_rose and "plant" not in what_rose.replace("flower", "")) and "flower" in desc_rose

    c2 = conv("A poodle is a dog. A dog is a mammal. A mammal is an animal.", seed)
    what_poodle = c2.say("what is a poodle?").strip().lower()
    j397b = ("dog" in what_poodle)

    # regression: single parent + multi-hop still works
    c3 = conv("A car is a vehicle.", seed)
    single = "vehicle" in c3.say("what is a car?").strip().lower()
    mh = "yes" in c2.say("is a poodle an animal?").strip().lower()
    j397c_local = bool(single and mh)
    return {"what_rose": what_rose, "desc_rose": desc_rose, "j397a": bool(j397a), "what_poodle": what_poodle,
            "j397b": bool(j397b), "single": bool(single), "mh": bool(mh), "j397c_local": j397c_local}


def suite(repo):
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-m", "not slow", "tests/test_conversation.py"],
                       capture_output=True, text=True, env={**os.environ, "PYTHONPATH": repo})
    last = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ""
    return ("failed" not in r.stdout and "error" not in r.stdout.lower().split("warnings")[0]), last


if __name__ == "__main__":
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print("=== JEP-397: most-specific parent ===", flush=True)
    seeds = [0, 7]
    R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]
        print(f"  seed {s}: what-rose={r['what_rose']!r} desc={r['desc_rose']!r} (J397a={r['j397a']}) | "
              f"what-poodle={r['what_poodle']!r} (J397b={r['j397b']}) | single={r['single']} mh={r['mh']}", flush=True)
    gate_ok, line = suite(repo)
    print(f"  conversation suite: {gate_ok} ({line})", flush=True)

    J397a = all(R[s]['j397a'] for s in seeds)
    J397b = all(R[s]['j397b'] for s in seeds)
    J397c = all(R[s]['j397c_local'] for s in seeds) and gate_ok
    passed = J397a and J397b and J397c
    print("\n--- VERDICT ---", flush=True)
    print(f"J397a specific over general : {J397a}", flush=True)
    print(f"J397b deep chain            : {J397b}", flush=True)
    print(f"J397c no regression         : {J397c}", flush=True)
    verdict = ("PASS - 'what is X' and describe now return the MOST-SPECIFIC parent after consolidation (rose->flower "
               "not plant, poodle->dog), with single-parent and multi-hop is-a intact; suite green. Discussion is "
               "informative again.") if passed else "NULL/partial - see rows (a bar missed; report, do not retune)."
    print(f"\nJEP-397: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP397"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": R, "gate": gate_ok, "J397a": J397a, "J397b": J397b,
                                                  "J397c": J397c, "passed": passed}, default=str))
    print("DONE", flush=True)
