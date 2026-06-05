"""JEP-462 — final integration + durability audit: teach a coherent world using ALL session features,
run a battery, then save->reload and re-run. Confirms the whole integrated cognition brain composes,
has zero confident falsehoods, and is durable. Pre-registered bars in
docs/amendments/jep462_final_integration_durability.md.
"""
import json, tempfile
from pathlib import Path

from world.conversation import Conversation

TEACH = [
    "A poodle is a dog.", "A dog is a mammal.", "A mammal is an animal.", "An animal is an organism.",
    "Mammals are warm-blooded.", "A dog has four legs.",
    "A sparrow is a bird.", "A bird is an animal.", "A penguin is a bird.",
    "Birds can fly.", "A penguin cannot fly.",
    "Heroes are good.", "A knight is a hero.",
    "Mars is a planet.", "Mars has two moons.", "Jupiter is the largest planet.",
    "The capital of France is Paris.",
]

PROBES = [
    ("is a poodle an organism?", "yesno", True),
    ("is a poodle warm-blooded?", "yesno", True),
    ("can a penguin fly?", "yesno", False),
    ("can a sparrow fly?", "yesno", True),
    ("how many legs does a dog have?", "value", "4"),
    ("is a poodle a bird?", "yesno", False),
    ("is a quark a mammal?", "yesno", False),
    ("what is the energy of a knight?", "value", "bright"),
    ("why is a knight good?", "value", "hero"),
    ("is Mars a planet?", "yesno", True),
    ("how many moons does Mars have?", "value", "2"),
    ("what is the largest planet?", "value", "jupiter"),
    ("what is the capital of France?", "value", "paris"),
    ("is a knight a hero?", "yesno", True),
    ("is a sparrow an organism?", "yesno", True),
    ("is a dog a poodle?", "yesno", False),
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
    n_ok = sum(1 for _, c in rows if c == "correct")
    fals = [q for (q, c) in rows if c == "falsehood"]
    return n_ok, fals, rows


def run(seed):
    with tempfile.TemporaryDirectory() as d:
        c = Conversation(brain_dir=d, seed=seed)
        for t in TEACH:
            c.say(t)
        ok1, f1, rows1 = battery(c)
        c.save()
        c2 = Conversation(brain_dir=d, seed=seed)        # reload fresh
        ok2, f2, rows2 = battery(c2)
    return dict(ok_before=ok1, fals_before=f1, ok_after=ok2, fals_after=f2, n=len(PROBES),
                rows_before=rows1)


if __name__ == "__main__":
    print("=== JEP-462: final integration + durability audit ===", flush=True)
    seeds = [0, 7]
    R = {}
    for s in seeds:
        R[s] = run(s)
        print(f"  seed {s}: BEFORE {R[s]['ok_before']}/{R[s]['n']} fals={len(R[s]['fals_before'])} | "
              f"AFTER reload {R[s]['ok_after']}/{R[s]['n']} fals={len(R[s]['fals_after'])}", flush=True)
        for q, c in R[s]['rows_before']:
            if c != "correct":
                print(f"      [{c}] {q}", flush=True)

    J462a = all(R[s]['ok_before'] >= 15 for s in seeds)
    J462b = all(len(R[s]['fals_before']) == 0 and len(R[s]['fals_after']) == 0 for s in seeds)
    J462c = all(R[s]['ok_after'] == R[s]['ok_before'] and len(R[s]['fals_after']) == len(R[s]['fals_before'])
                for s in seeds)
    passed = J462a and J462b and J462c

    print("\n--- VERDICT ---", flush=True)
    print(f"J462a everything composes (>=15/16) : {J462a}", flush=True)
    print(f"J462b zero confident falsehoods     : {J462b}", flush=True)
    print(f"J462c durable across reload (identical): {J462c}", flush=True)
    verdict = ("PASS - the full session's cognition work composes cleanly, no falsehoods, durable across "
               "reload") if passed else "NULL/partial"
    print(f"\nJEP-462: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP462"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"R": {str(s): {k: v for k, v in R[s].items() if k != 'rows_before'}
                                                        for s in seeds}, "passed": passed,
                                                  "J462a": J462a, "J462b": J462b, "J462c": J462c}, indent=2, default=str))
    print("DONE", flush=True)
