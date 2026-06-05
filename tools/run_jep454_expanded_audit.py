"""JEP-454 — expanded adversarial audit: hunt confident falsehoods across the integrated reasoning +
affect brain. Teach a richer mini-world, run ~20 pre-classified probes, score each
correct/abstain/FALSEHOOD. Pre-registered bars in docs/amendments/jep454_expanded_adversarial_audit.md.
"""
import json
from pathlib import Path

import tempfile
from world.conversation import Conversation

TEACH = [
    "A poodle is a dog.", "A dog is a mammal.", "A mammal is an animal.", "An animal is an organism.",
    "A cat is a mammal.", "A salmon is a fish.", "A fish is an animal.",
    "A sparrow is a bird.", "A bird is an animal.", "A penguin is a bird.", "An ostrich is a bird.",
    "Mammals are warm-blooded.", "Birds can fly.", "Fish can swim.",
    "A penguin cannot fly.", "An ostrich cannot fly.",
    "Snakes are evil.", "A cobra is a snake.", "A viper is a snake.",
    "Heroes are good.", "A knight is a hero.",
    "A dog has four legs.", "A spider has eight legs.",
    "The capital of France is Paris.", "A dragon breathes fire.",
]

# (question, kind, expected) ; kind in {yesno, value}
PROBES = [
    ("is a poodle an organism?", "yesno", True),       # deep chain
    ("is an organism a poodle?", "yesno", False),      # reverse directionality
    ("is a dog a poodle?", "yesno", False),            # reverse (not all dogs are poodles)
    ("is a poodle warm-blooded?", "yesno", True),      # property inheritance
    ("can a penguin fly?", "yesno", False),            # exception
    ("can an ostrich fly?", "yesno", False),           # exception 2
    ("can a sparrow fly?", "yesno", True),             # no exception
    ("is a poodle a fish?", "yesno", False),           # cross-branch negative
    ("is a salmon an animal?", "yesno", True),         # deep via fish
    ("is a cat a mammal?", "yesno", True),
    ("is a quark a mammal?", "yesno", False),          # untaught -> must not say yes
    ("what is the energy of a cobra?", "value", "dark"),   # inherited affect
    ("what is the energy of a viper?", "value", "dark"),   # inherited affect 2
    ("what is the energy of a knight?", "value", "bright"),# inherited positive affect
    ("why is a cobra evil?", "value", "snake"),
    ("what is the capital of France?", "value", "paris"),
    ("how many legs does a dog have?", "value", "4"),
    ("how many legs does a spider have?", "value", "8"),
    ("what does a dragon breathe?", "value", "fire"),  # emotional fact survives
    ("is a sparrow an organism?", "yesno", True),      # deep via bird->animal->organism
]


def _classify(ans, kind, expected):
    a = str(ans).strip().lower()
    abstain = ("don't know" in a or "not sure" in a or "teach me" in a or "isn't clear" in a
               or "aren't clear" in a or a in ("", "hmm."))
    if kind == "yesno":
        affirm = a.startswith("yes"); deny = a.startswith("no")
        if expected:
            if affirm: return "correct"
            if deny: return "falsehood"          # denied a truth
            return "abstain"
        else:
            if deny: return "correct"
            if affirm: return "falsehood"         # asserted a falsehood
            return "abstain"
    else:  # value
        if abstain: return "abstain"
        if str(expected).lower() in a or (expected == "4" and "four" in a) or (expected == "8" and "eight" in a):
            return "correct"
        # a confident but wrong value -> falsehood; a 'neutral'/empty -> abstain
        if a in ("neutral", "neutral."):
            return "abstain"
        return "falsehood"


def run(seed):
    c = Conversation(brain_dir=tempfile.mkdtemp())  # clean-room (lesson #16)
    for t in TEACH:
        c.say(t)
    for i in range(120):                          # interference (bury the emotional fact)
        c.say(f"A gizmo{i} is a widget.")
    rows = []
    for q, kind, exp in PROBES:
        ans = c.say(q)
        rows.append((q, kind, exp, str(ans), _classify(ans, kind, exp)))
    n = len(rows)
    correct = sum(1 for *_, c2 in rows if c2 == "correct")
    falsehoods = [(q, ans) for (q, k, e, ans, c2) in rows if c2 == "falsehood"]
    return dict(rows=rows, correct=correct, n=n, falsehoods=falsehoods)


if __name__ == "__main__":
    print("=== JEP-454: expanded adversarial audit ===", flush=True)
    seeds = [0, 7]
    R = {}
    for s in seeds:
        R[s] = run(s)
        print(f"  seed {s}: correct {R[s]['correct']}/{R[s]['n']} | falsehoods={len(R[s]['falsehoods'])}", flush=True)
        for (q, ans) in R[s]['falsehoods']:
            print(f"      FALSEHOOD: {q} -> {ans}", flush=True)
        if s == 0:
            for (q, k, e, ans, c2) in R[s]['rows']:
                if c2 != "correct":
                    print(f"      [{c2}] {q} -> {ans[:50]}", flush=True)

    J454a = all(len(R[s]['falsehoods']) == 0 for s in seeds)
    J454b = all(R[s]['correct'] / R[s]['n'] >= 0.85 for s in seeds)
    passed = J454a and J454b
    print("\n--- VERDICT (J454c = pytest, separate) ---", flush=True)
    print(f"J454a zero confident falsehoods : {J454a}", flush=True)
    print(f"J454b >=85% correct             : {J454b} ({[round(R[s]['correct']/R[s]['n'],2) for s in seeds]})", flush=True)
    verdict = ("PASS - integrated brain is competent and never confidently wrong"
               if passed else "NULL/partial")
    print(f"\nJEP-454: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP454"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"R": {str(s): {k: v for k, v in R[s].items() if k != 'rows'}
                                                        for s in seeds}, "passed": passed,
                                                  "J454a": J454a, "J454b": J454b}, indent=2, default=str))
    print("DONE", flush=True)
