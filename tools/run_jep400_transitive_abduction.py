"""JEP-400 — abduction over read prose: 'why?' phrasings + transitive causal chains. No transformer.
Pre-registered bars in docs/amendments/jep400_transitive_abduction.md.
"""
import json, tempfile, subprocess, sys, os
from pathlib import Path
from world.conversation import Conversation


def conv(text, seed):
    c = Conversation(brain_dir=tempfile.mkdtemp(prefix=f"j400_{seed}_"), seed=seed)
    c.read_text(text)
    return c


def run_seed(seed):
    c = conv("Smoking causes cancer. Cancer causes death. A virus causes infection. Infection causes fever.", seed)
    why_cancer = c.say("why does cancer happen?").strip().lower()
    why_death = c.say("why does death happen?").strip().lower()
    j400a = ("smoking" in why_cancer and "cancer" in why_death)

    causes_death = c.say("what causes death?").strip().lower()
    causes_fever = c.say("what causes fever?").strip().lower()
    j400b = ("cancer" in causes_death and "smoking" in causes_death
             and "infection" in causes_fever and "virus" in causes_fever)

    causes_cancer = c.say("what causes cancer?").strip().lower()
    j400c_local = ("smoking" in causes_cancer)
    return {"why_cancer": why_cancer, "why_death": why_death, "j400a": bool(j400a),
            "causes_death": causes_death, "causes_fever": causes_fever, "j400b": bool(j400b),
            "causes_cancer": causes_cancer, "j400c_local": bool(j400c_local)}


def suite(repo):
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-m", "not slow", "tests/test_conversation.py"],
                       capture_output=True, text=True, env={**os.environ, "PYTHONPATH": repo})
    last = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ""
    return ("failed" not in r.stdout and "error" not in r.stdout.lower().split("warnings")[0]), last


if __name__ == "__main__":
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print("=== JEP-400: transitive abduction + why phrasings ===", flush=True)
    seeds = [0, 7]
    R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]
        print(f"  seed {s}: why-cancer={r['why_cancer']!r} why-death={r['why_death']!r} (J400a={r['j400a']}) | "
              f"causes-death={r['causes_death']!r} causes-fever={r['causes_fever']!r} (J400b={r['j400b']}) | "
              f"causes-cancer={r['causes_cancer']!r} (J400c={r['j400c_local']})", flush=True)
    gate_ok, line = suite(repo)
    print(f"  conversation suite: {gate_ok} ({line})", flush=True)

    J400a = all(R[s]['j400a'] for s in seeds)
    J400b = all(R[s]['j400b'] for s in seeds)
    J400c = all(R[s]['j400c_local'] for s in seeds) and gate_ok
    passed = J400a and J400b and J400c
    print("\n--- VERDICT ---", flush=True)
    print(f"J400a why phrasings parse   : {J400a}", flush=True)
    print(f"J400b transitive abduction  : {J400b}", flush=True)
    print(f"J400c direct cause + suite  : {J400c}", flush=True)
    verdict = ("PASS - abduction over read prose now parses 'why does X happen?' and traces the causal CHAIN "
               "transitively: 'what causes death?' -> cancer AND smoking (root), 'what causes fever?' -> infection AND "
               "virus, while direct single-cause queries still work; suite green. Deeper inference composes over real "
               "prose.") if passed else "NULL/partial - see rows (a bar missed; report, do not retune)."
    print(f"\nJEP-400: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP400"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": R, "gate": gate_ok, "J400a": J400a, "J400b": J400b,
                                                  "J400c": J400c, "passed": passed}, default=str))
    print("DONE", flush=True)
