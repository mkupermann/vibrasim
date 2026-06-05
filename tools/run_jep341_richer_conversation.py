"""JEP-341 — richer conversational understanding (natural phrasings, pronouns, tell-me-about). No transformer.
Pre-registered bars in docs/amendments/jep341_richer_conversation.md.
"""
import json, tempfile, subprocess, sys, os
from pathlib import Path
from world.conversation import Conversation
from world.substrate_memory import SubstrateMemory
from world.brain_query import BrainQuery


def setup(seed):
    d = tempfile.mkdtemp(prefix=f"rich_{seed}_")
    c = Conversation(brain_dir=d, seed=seed)
    for s in ["A poodle is a dog.", "A dog is a mammal.", "A mammal is an animal.", "A dog can bark.",
              "A cat eats fish.", "A cow eats grass.", "A heart is part of a dog."]:   # 'eats' twice -> engine learns it
        c.say(s)
    c.sm.add_fact("dog", "has_legs", "4")               # numeric
    return c


def run_seed(seed):
    c = setup(seed)
    bq = BrainQuery(c.sm, seed=seed)
    # J341a natural question battery (question, expected)
    battery = [
        ("is a poodle a kind of animal?", True),
        ("does a poodle have legs?", True),
        ("how many legs does a dog have?", 4),
        ("what does a cat eat?", ["fish"]),
        ("can a poodle bark?", True),
        ("does a dog have a heart?", True),
    ]
    ok = 0
    for (q, exp) in battery:
        a = bq.ask(q)
        ok += (a == exp)
    qbat_acc = ok / len(battery)

    # describe is well-formed + re-readable
    desc = bq.describe("poodle")
    from world.understanding import UnderstandingEngine
    e2 = UnderstandingEngine(seed=seed)
    desc_ok = ("poodle" in desc.lower() and ("dog" in desc.lower() or "bark" in desc.lower()))
    try:
        e2.read(desc.replace(";", ".")); reread_ok = True
    except Exception:
        reread_ok = False

    # pronoun dialogue via Conversation.say
    c2 = setup(seed)
    c2.say("Tell me about a poodle")                    # sets last subject = poodle
    pron = c2.say("Can it bark?")                        # 'it' -> poodle
    pron_ok = (pron.strip().lower() == "yes.")

    return {"qbattery_acc": round(qbat_acc, 3), "describe": desc, "describe_ok": bool(desc_ok and reread_ok),
            "pronoun_ok": bool(pron_ok)}


def regression(repo):
    outs = {}
    for name in ["run_jep322_brain_query", "run_jep340_conversation"]:
        r = subprocess.run([sys.executable, f"tools/{name}.py"], capture_output=True, text=True,
                           env={**os.environ, "PYTHONPATH": repo})
        num = name.split("jep")[1][:3]
        outs[num] = f"JEP-{num}: PASS" in r.stdout
    return outs


if __name__ == "__main__":
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print("=== JEP-341: richer conversational understanding ===", flush=True)
    seeds = [0, 7]; R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]
        print(f"  seed {s}: question-battery acc={r['qbattery_acc']} | describe_ok={r['describe_ok']} | "
              f"pronoun_ok={r['pronoun_ok']}", flush=True)
        print(f"      describe('poodle') = {r['describe']}", flush=True)
    reg = regression(repo)
    print(f"  regression: {reg}", flush=True)

    J341a = all(R[s]['qbattery_acc'] >= 0.90 and R[s]['pronoun_ok'] for s in seeds)
    J341b = all(reg.values())
    J341c = all(R[s]['describe_ok'] for s in seeds)
    passed = J341a and J341b and J341c
    print("\n--- VERDICT ---", flush=True)
    print(f"J341a natural question battery + pronoun (>=.90): {J341a}", flush=True)
    print(f"J341b no regression (322, 340)                   : {J341b}", flush=True)
    print(f"J341c describe well-formed + re-readable         : {J341c}", flush=True)
    verdict = ("PASS - the conversation understands more natural phrasings (does X have, how many, kind of, tell me "
               "about) and the pronoun 'it'; talking feels less templated") if passed else "NULL/partial"
    print(f"\nJEP-341: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP341"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": R, "reg": reg, "J341a": J341a, "J341b": J341b,
                                                  "J341c": J341c, "passed": passed}, default=str))
    print("DONE", flush=True)
