"""JEP-392 — 'what is not clear to you?': curiosity-driven gaps from real prose. No transformer.
Pre-registered bars in docs/amendments/jep392_curiosity_real_prose.md.
"""
import json, tempfile, subprocess, sys, os
from pathlib import Path
from world.conversation import Conversation

ARTICLE = ("A dog is a mammal. A mammal is an animal. A whale is a mammal. A whale lives in the ocean. "
           "A salmon is a fish. A sparrow is a bird.")


def run_seed(seed):
    c = Conversation(brain_dir=tempfile.mkdtemp(prefix=f"j392_{seed}_"), seed=seed)
    c.read_text(ARTICLE)
    gaps = set(c.gaps())
    # J392a: gaps are exactly the referenced-but-undefined concepts; no defined ones, no roots
    j392a = (gaps == {"bird", "fish"})
    # J392b: voices them
    nc = c.say("what is not clear to you?").strip().lower()
    j392b = ("bird" in nc and "fish" in nc)
    # J392c: teaching closes + unlocks new multi-hop
    before = "yes" in c.say("is a sparrow an animal?").strip().lower()
    c.read_text("A bird is an animal.")
    gaps_after = set(c.gaps())
    after = "yes" in c.say("is a sparrow an animal?").strip().lower()
    j392c = (not before) and ("bird" not in gaps_after) and after
    return {"gaps": sorted(gaps), "j392a": bool(j392a), "not_clear": nc, "j392b": bool(j392b),
            "before": bool(before), "gaps_after": sorted(gaps_after), "after": bool(after), "j392c": bool(j392c)}


def suite(repo):
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-m", "not slow", "tests/test_conversation.py"],
                       capture_output=True, text=True, env={**os.environ, "PYTHONPATH": repo})
    last = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ""
    return ("failed" not in r.stdout and "error" not in r.stdout.lower().split("warnings")[0]), last


if __name__ == "__main__":
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print("=== JEP-392: curiosity-driven gaps from real prose ===", flush=True)
    seeds = [0, 7]
    R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]
        print(f"  seed {s}: J392a gaps={r['gaps']} ({r['j392a']}) | J392b voices={r['j392b']} | "
              f"J392c before={r['before']} gaps_after={r['gaps_after']} after={r['after']} ({r['j392c']})", flush=True)
    gate_ok, line = suite(repo)
    print(f"  conversation suite: {gate_ok} ({line})", flush=True)

    J392a = all(R[s]['j392a'] for s in seeds)
    J392b = all(R[s]['j392b'] for s in seeds)
    J392c = all(R[s]['j392c'] for s in seeds) and gate_ok
    passed = J392a and J392b and J392c
    print("\n--- VERDICT ---", flush=True)
    print(f"J392a correct gaps from prose : {J392a}", flush=True)
    print(f"J392b voices them             : {J392b}", flush=True)
    print(f"J392c teaching closes+unlocks : {J392c}", flush=True)
    verdict = ("PASS - after reading a real article the substrate identifies exactly the referenced-but-undefined "
               "concepts as gaps (bird, fish), voices them via 'what is not clear to you?', and teaching one closes it "
               "AND unlocks new multi-hop reasoning (sparrow->animal). Michael's 'what is not clear to you?' vision "
               "works on real prose.") if passed else "NULL/partial - see rows (a bar missed; report, do not retune)."
    print(f"\nJEP-392: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP392"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": R, "gate": gate_ok, "J392a": J392a, "J392b": J392b,
                                                  "J392c": J392c, "passed": passed}, default=str))
    print("DONE", flush=True)
