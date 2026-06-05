"""JEP-419 — teach a synonym vocabulary (curated by the LLM from Fernald's English Synonyms) and verify understanding +
persistence. No transformer in the substrate. Pre-registered bars in docs/amendments/jep419_synonym_vocabulary.md.
"""
import json, tempfile, subprocess, sys, os
from pathlib import Path
from world.conversation import Conversation

# Curated clean, genuinely-interchangeable synonym pairs (variant -> canonical), distilled by the LLM teacher from
# Fernald, "English Synonyms and Antonyms". (The book warns most synonyms carry nuance; the teacher picks safe ones.)
SYNONYMS = {
    "big": "large", "huge": "large", "enormous": "large", "giant": "large",
    "small": "little", "tiny": "little",
    "fast": "quick", "rapid": "quick", "swift": "quick",
    "smart": "intelligent", "clever": "intelligent", "bright": "intelligent",
    "happy": "glad", "joyful": "glad",
    "begin": "start", "commence": "start",
    "end": "finish", "conclude": "finish",
    "buy": "purchase", "build": "construct", "make": "create",
    "strong": "powerful", "weak": "feeble", "rich": "wealthy",
    "brave": "courageous", "afraid": "scared", "angry": "mad",
    "correct": "right", "hard": "difficult", "easy": "simple",
    "important": "significant", "cold": "chilly", "beautiful": "pretty",
}
# (teach_sentence, question_with_synonym, expected_yes)
TESTS = [
    ("An elephant is big.", "is an elephant large?", True),
    ("A cheetah is fast.", "is a cheetah quick?", True),
    ("A human is smart.", "is a human intelligent?", True),
    ("A child is happy.", "is a child glad?", True),
    ("A lion is strong.", "is a lion powerful?", True),
    ("A diamond is hard.", "is a diamond difficult?", True),
    ("A mouse is small.", "is a mouse little?", True),
    ("A test is important.", "is a test significant?", True),
]


def run_seed(seed):
    brain = tempfile.mkdtemp(prefix=f"j419_{seed}_")
    c = Conversation(brain_dir=brain, seed=seed)
    for v, canon in SYNONYMS.items():
        c.say(f"{v} means {canon}.")
    n_taught = len(c.sm.synonyms)
    j419a = n_taught >= 25

    correct = 0
    for teach, q, exp in TESTS:
        c.say(teach)
        ans = "yes" in c.say(q).strip().lower()
        correct += (ans == exp)
    j419b = correct >= 7

    c.save()
    reloaded = Conversation(brain_dir=brain, seed=seed)
    syn_persist = reloaded.sm.synonyms.get("big") == "large" and len(reloaded.sm.synonyms) == n_taught
    # a fact taught before reload, queried with synonym after reload
    reload_works = "yes" in reloaded.say("is an elephant large?").strip().lower()
    j419c = syn_persist and reload_works
    return {"n_taught": n_taught, "j419a": bool(j419a), "correct": correct, "total": len(TESTS),
            "j419b": bool(j419b), "syn_persist": bool(syn_persist), "reload_works": bool(reload_works),
            "j419c": bool(j419c)}


def suite(repo):
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-m", "not slow", "tests/test_conversation.py"],
                       capture_output=True, text=True, env={**os.environ, "PYTHONPATH": repo})
    last = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ""
    return ("failed" not in r.stdout and "error" not in r.stdout.lower().split("warnings")[0]), last


if __name__ == "__main__":
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print("=== JEP-419: teach a synonym vocabulary (from Fernald) ===", flush=True)
    seeds = [0, 7]
    R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]
        print(f"  seed {s}: synonyms taught={r['n_taught']} (J419a={r['j419a']}) | synonym Q&A {r['correct']}/"
              f"{r['total']} (J419b={r['j419b']}) | persist={r['syn_persist']} reload_works={r['reload_works']} "
              f"(J419c={r['j419c']})", flush=True)
    gate_ok, line = suite(repo)
    print(f"  conversation suite: {gate_ok} ({line})", flush=True)
    J419a = all(R[s]['j419a'] for s in seeds)
    J419b = all(R[s]['j419b'] for s in seeds)
    J419c = all(R[s]['j419c'] for s in seeds) and gate_ok
    passed = J419a and J419b and J419c
    print("\n--- VERDICT ---", flush=True)
    print(f"J419a vocabulary taught (>=25)  : {J419a}", flush=True)
    print(f"J419b understands via synonyms  : {J419b}", flush=True)
    print(f"J419c persists + suite          : {J419c}", flush=True)
    verdict = ("PASS - the LLM teacher gave the substrate a synonym vocabulary (from Fernald); the substrate now "
               "understands facts/questions phrased with synonyms (big/large, fast/quick, ...), and the vocabulary "
               "persists across save/load. Concrete 'teach English' from a real language resource; no LLM in the "
               "substrate.") if passed else "NULL/partial - see rows (a bar missed; report, do not retune)."
    print(f"\nJEP-419: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP419"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": R, "gate": gate_ok, "J419a": J419a, "J419b": J419b,
                                                  "J419c": J419c, "passed": passed}, default=str))
    print("DONE", flush=True)
