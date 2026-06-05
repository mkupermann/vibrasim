"""JEP-476 — comprehensive clean-room integration audit: teach ONE rich world exercising EVERY capability
added this session (reasoning + 5 affect modes + signed relations + alliances + ambivalence + temporal),
run a battery, verify zero confident falsehoods + high accuracy, AND durability across save/reload.
Clean-room (lesson #16). Pre-registered bars in docs/amendments/jep476_full_audit.md.
"""
import json, tempfile
from pathlib import Path
from world.conversation import Conversation

TEACH = [
    # taxonomy + properties + exception + parts
    "A poodle is a dog.", "A dog is a mammal.", "A mammal is an animal.", "An animal is an organism.",
    "Mammals are warm-blooded.", "A dog has four legs.",
    "A penguin is a bird.", "A bird is an animal.", "Birds can fly.", "A penguin cannot fly.",
    # affect: taught class + inheritance
    "Snakes are evil.", "A cobra is a snake.", "Heroes are good.", "A knight is a hero.",
    # signed relations: propagation + alliances + ambivalence
    "A villain is an enemy of a hero.", "A rebel is an enemy of a villain.",
    "A spy is a friend of a hero.", "A spy is a friend of a villain.",
    # temporal sequence
    "Breakfast happens before lunch.", "Lunch happens before dinner.",
    # proper noun + superlative + attribute
    "Mars is a planet.", "Jupiter is the largest planet.", "The capital of France is Paris.",
    # emotional fact (will be buried under interference)
    "A dragon breathes fire.",
]

PROBES = [
    ("is a poodle an organism?", "yesno", True),
    ("is an organism a poodle?", "yesno", False),
    ("is a poodle warm-blooded?", "yesno", True),
    ("can a penguin fly?", "yesno", False),
    ("is a poodle a bird?", "yesno", False),
    ("is a quark a mammal?", "yesno", False),
    ("how many legs does a dog have?", "value", "4"),
    ("what is the energy of a villain?", "value", "dark"),    # signed-propagated
    ("what is the energy of a cobra?", "value", "dark"),      # inherited
    ("what is the energy of a knight?", "value", "bright"),   # inherited positive
    ("is a rebel an ally of a hero?", "yesno", True),         # enemy of enemy
    ("is a spy conflicted?", "yesno", True),                  # ambivalence
    ("is a knight conflicted?", "yesno", False),
    ("what comes after breakfast?", "value", "lunch"),
    ("what comes before dinner?", "value", "lunch"),
    ("is breakfast before dinner?", "yesno", True),
    ("is dinner before breakfast?", "yesno", False),
    ("what happened first?", "value", "breakfast"),
    ("is Mars a planet?", "yesno", True),
    ("what is the largest planet?", "value", "jupiter"),
    ("what is the capital of France?", "value", "paris"),
    ("what does a dragon breathe?", "value", "fire"),
]


def _classify(ans, kind, expected):
    a = str(ans).strip().lower()
    abstain = any(k in a for k in ("don't know", "not sure", "teach me", "clear to me"))
    if kind == "yesno":
        af, dn = a.startswith("yes"), a.startswith("no")
        if expected:
            return "correct" if af else ("falsehood" if dn else "abstain")
        return "correct" if dn else ("falsehood" if af else "abstain")
    if abstain:
        return "abstain"
    if str(expected).lower() in a or (expected == "4" and "four" in a):
        return "correct"
    return "abstain" if a in ("neutral",) else "falsehood"


def battery(conv):
    rows = [(q, _classify(conv.say(q), k, e)) for (q, k, e) in PROBES]
    return sum(1 for _, c in rows if c == "correct"), [q for (q, c) in rows if c == "falsehood"], rows


def run(seed):
    d = tempfile.mkdtemp()
    c = Conversation(brain_dir=d, seed=seed)
    for t in TEACH:
        c.say(t)
    for i in range(80):                       # interference (bury the emotional fact)
        c.say(f"A gizmo{i} is a widget.")
    ok1, f1, rows = battery(c)
    c.save()
    c2 = Conversation(brain_dir=d, seed=seed)  # reload
    ok2, f2, _ = battery(c2)
    return dict(ok1=ok1, f1=f1, ok2=ok2, f2=f2, n=len(PROBES), rows=rows)


if __name__ == "__main__":
    print("=== JEP-476: comprehensive clean-room integration audit (ALL session capabilities) ===", flush=True)
    seeds = [0, 7]
    R = {}
    for s in seeds:
        R[s] = run(s)
        print(f"  seed {s}: BEFORE {R[s]['ok1']}/{R[s]['n']} fals={len(R[s]['f1'])} | "
              f"AFTER reload {R[s]['ok2']}/{R[s]['n']} fals={len(R[s]['f2'])}", flush=True)
        for q, c in R[s]['rows']:
            if c != "correct":
                print(f"      [{c}] {q}", flush=True)

    J476a = all(R[s]['ok1'] >= 0.90 * R[s]['n'] for s in seeds)
    J476b = all(len(R[s]['f1']) == 0 and len(R[s]['f2']) == 0 for s in seeds)
    J476c = all(R[s]['ok2'] == R[s]['ok1'] for s in seeds)
    passed = J476a and J476b and J476c

    print("\n--- VERDICT ---", flush=True)
    print(f"J476a >=90% correct (all capabilities) : {J476a}", flush=True)
    print(f"J476b zero confident falsehoods        : {J476b}", flush=True)
    print(f"J476c durable across reload (identical) : {J476c}", flush=True)
    verdict = ("PASS - the WHOLE session's system (reasoning + 5 affect modes + relational + temporal) "
               "composes clean-room with no falsehoods and is durable") if passed else "NULL/partial"
    print(f"\nJEP-476: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP476"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"R": {str(s): {k: v for k, v in R[s].items() if k != 'rows'}
                                                        for s in seeds}, "passed": passed,
                                                  "J476a": J476a, "J476b": J476b, "J476c": J476c}, indent=2, default=str))
    print("DONE", flush=True)
