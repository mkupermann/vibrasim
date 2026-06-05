"""JEP-423 — LLM-parent teaches a coherent topic (Solar System); substrate answers complex multi-relation questions.
No transformer in the substrate. Pre-registered bars in docs/amendments/jep423_topic_knowledge_graph.md.
"""
import json, tempfile, subprocess, sys, os
from pathlib import Path
from world.conversation import Conversation

# LLM-teacher-distilled Solar System facts (established general knowledge), in substrate-parseable form.
LESSON = [
    "A planet is a celestial body.", "A star is a celestial body.", "A moon is a celestial body.",
    "The Sun is a star.", "Earth is a planet.", "Mars is a planet.", "Jupiter is a planet.",
    "Saturn is a planet.", "Venus is a planet.", "Mercury is a planet.", "Neptune is a planet.",
    "Jupiter is the largest planet.", "Mercury is the smallest planet.",
    "A planet is round.", "A star is hot.", "The Sun is hot.",
    "Earth has a moon.", "Mars has two moons.", "Jupiter has many moons.",
    "Earth has water.", "Earth has life.", "Mars is red.", "Saturn has rings.",
    "A planet orbits a star.", "Earth orbits the Sun.", "Mars orbits the Sun.",
    "Gravity holds planets in orbit.", "The Sun produces light.", "The Sun produces heat.",
    "A comet is a celestial body.", "An asteroid is a celestial body.",
    "Astronomy is a science.", "Astronomy studies planets.", "A telescope observes stars.",
    "A galaxy contains stars.", "The Milky Way is a galaxy.", "The Sun is in the Milky Way.",
    "A planet is bigger than a moon.", "A star is bigger than a planet.",
]
QA = [
    ("is Earth a celestial body?", True),       # earth->planet->celestial body (multi-hop)
    ("is the Sun a celestial body?", True),      # sun->star->celestial body
    ("is Jupiter a planet?", True),
    ("is a planet round?", True),
    ("is Earth round?", True),                   # inherited property
    ("what is the largest planet?", "jupiter"),  # superlative
    ("what is the smallest planet?", "mercury"),
    ("how many moons does Mars have?", "2"),
    ("does Earth have water?", True),
    ("does Saturn have rings?", True),
    ("what does the Sun produce?", "light"),     # open relation
    ("is the Milky Way a galaxy?", True),
]
OOD = ["is Earth a sandwich?", "does the Sun have wheels?", "is Pluto a planet?"]  # Pluto untaught -> abstain/no


def run_seed(seed):
    brain = tempfile.mkdtemp(prefix=f"j423_{seed}_")
    c = Conversation(brain_dir=brain, seed=seed)
    for s in LESSON:
        c.say(s)
    facts = set(c.sm.facts)
    junk = [f for f in facts if any(" " in str(x) for x in f)]
    j423a = (len(facts) >= 35 and len(junk) == 0)

    correct = 0
    fails = []
    for q, t in QA:
        a = c.say(q).strip().lower()
        ok = ("yes" in a) if t is True else (t in a)
        correct += ok
        if not ok:
            fails.append(q)
    qa_acc = round(correct / len(QA), 3)
    j423b = qa_acc >= 0.90

    ood_ok = all("yes" not in c.say(q).strip().lower() for q in OOD)
    c.save()
    reloaded = Conversation(brain_dir=brain, seed=seed)
    persists = "yes" in reloaded.say("is Earth a celestial body?").strip().lower()
    j423c = (len(junk) == 0 and persists and ood_ok)
    return {"n_facts": len(facts), "junk": len(junk), "j423a": bool(j423a), "qa_acc": qa_acc, "fails": fails,
            "j423b": bool(j423b), "ood_ok": bool(ood_ok), "persists": bool(persists), "j423c": bool(j423c)}


def suite(repo):
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-m", "not slow", "tests/test_conversation.py"],
                       capture_output=True, text=True, env={**os.environ, "PYTHONPATH": repo})
    last = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ""
    return ("failed" not in r.stdout and "error" not in r.stdout.lower().split("warnings")[0]), last


if __name__ == "__main__":
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print("=== JEP-423: topic knowledge graph (Solar System) ===", flush=True)
    seeds = [0, 7]
    R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]
        print(f"  seed {s}: facts={r['n_facts']} junk={r['junk']} (J423a={r['j423a']}) | Q&A={r['qa_acc']} "
              f"(fails {r['fails']}) (J423b={r['j423b']}) | ood_ok={r['ood_ok']} persists={r['persists']} "
              f"(J423c={r['j423c']})", flush=True)
    gate_ok, line = suite(repo)
    print(f"  conversation suite: {gate_ok} ({line})", flush=True)
    J423a = all(R[s]['j423a'] for s in seeds)
    J423b = all(R[s]['j423b'] for s in seeds)
    J423c = all(R[s]['j423c'] for s in seeds) and gate_ok
    passed = J423a and J423b and J423c
    print("\n--- VERDICT ---", flush=True)
    print(f"J423a taught cleanly (>=35, 0 junk) : {J423a}", flush=True)
    print(f"J423b complex Q&A >=0.90            : {J423b}", flush=True)
    print(f"J423c clean + durable + suite       : {J423c}", flush=True)
    verdict = ("PASS - the LLM teacher built a coherent Solar-System knowledge graph and the substrate (no LLM) answers "
               "complex multi-relation questions (multi-hop is-a, superlatives, attributes, counts, open relations) "
               ">=0.90, zero junk, persistent, with honest abstention on the untaught. The LLM-as-parent deliverable is "
               "validated at topic scale.") if passed else "PARTIAL/NULL - see fails (a relation type missed)."
    print(f"\nJEP-423: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP423"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": R, "gate": gate_ok, "J423a": J423a, "J423b": J423b,
                                                  "J423c": J423c, "passed": passed}, default=str))
    print("DONE", flush=True)
