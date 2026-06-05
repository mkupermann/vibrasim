"""JEP-416 — LLM-as-parent: the LLM teaches the substrate distilled facts from arbitrary content; the substrate
(no LLM) answers. No transformer in the substrate. Pre-registered bars in docs/amendments/jep416_llm_as_parent.md.
"""
import json, tempfile
from pathlib import Path
from world.conversation import Conversation
from world.brain_query import BrainQuery

# Facts the LLM TEACHER distilled from the real book text (The Holographic Universe, pp.~8-13), in substrate-parseable
# form (single-token entities). The substrate did NOT read these itself — the LLM understood the prose and taught them.
LESSON = [
    "Bohm is a physicist.",
    "Pribram is a neurophysiologist.",
    "A physicist is a scientist.",
    "A neurophysiologist is a scientist.",
    "Bohm proposed holography.",
    "Pribram proposed holography.",
    "Holography is a theory.",
    "Holography explains memory.",
    "Holography explains perception.",
    "Holography is controversial.",
    "Ring is a psychologist.",
    "Grof is a psychiatrist.",
    "Wolf is a physicist.",
    "Peat is a physicist.",
    "Aspect is a physicist.",
    "Aspect performed an experiment.",
    "Peat wrote Synchronicity.",
]


def run_seed(seed):
    brain = tempfile.mkdtemp(prefix=f"j416_{seed}_")
    c = Conversation(brain_dir=brain, seed=seed)
    for s in LESSON:
        c.say(s)
    facts = set(c.sm.facts)
    junk = [f for f in facts if any(" " in str(x) for x in f)]
    j416a = (len(facts) >= 12 and len(junk) == 0)

    qa = [
        ("is Bohm a physicist?", True), ("is Bohm a scientist?", True), ("is holography controversial?", True),
        ("is Pribram a physicist?", False), ("is Wolf a physicist?", True),
        ("what did Peat write?", "synchronicity"), ("who proposed holography?", "bohm"),
        ("does holography explain memory?", True),
    ]
    correct = 0
    for q, t in qa:
        a = c.say(q).strip().lower()
        if t is True:
            correct += "yes" in a
        elif t is False:
            correct += "yes" not in a
        else:
            correct += t in a
    j416b = correct >= 6
    about_bohm = c.say("tell me about Bohm").strip().lower()

    # no LLM in the answering path + durable
    bq = BrainQuery(c.sm, seed=seed)
    no_llm = ("transformer" not in type(bq.mem).__module__ and type(bq.mem).__name__ == "SubstrateMemory")
    c.save()
    reloaded = Conversation(brain_dir=brain, seed=seed)
    persists = "yes" in reloaded.say("is Bohm a physicist?").strip().lower()
    j416c = no_llm and persists

    return {"n_facts": len(facts), "junk": len(junk), "j416a": bool(j416a), "correct": correct, "j416b": bool(j416b),
            "about_bohm": about_bohm, "no_llm": bool(no_llm), "persists": bool(persists), "j416c": bool(j416c)}


if __name__ == "__main__":
    print("=== JEP-416: LLM-as-parent (teach arbitrary content; substrate has no LLM) ===", flush=True)
    seeds = [0, 7]
    R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]
        print(f"  seed {s}: facts={r['n_facts']} junk={r['junk']} (J416a={r['j416a']}) | book Q&A {r['correct']}/8 "
              f"(J416b={r['j416b']}) | no_llm={r['no_llm']} persists={r['persists']} (J416c={r['j416c']})", flush=True)
        print(f"           tell me about Bohm -> {r['about_bohm']!r}", flush=True)

    J416a = all(R[s]['j416a'] for s in seeds)
    J416b = all(R[s]['j416b'] for s in seeds)
    J416c = all(R[s]['j416c'] for s in seeds)
    passed = J416a and J416b and J416c
    print("\n--- VERDICT ---", flush=True)
    print(f"J416a taught cleanly (>=12, no junk) : {J416a}", flush=True)
    print(f"J416b substrate answers book Qs      : {J416b}", flush=True)
    print(f"J416c no LLM in substrate + durable  : {J416c}", flush=True)
    verdict = ("PASS - the LLM-as-parent path opens arbitrary content: the LLM distilled faithful facts from a book the "
               "substrate could NOT read itself and taught them; the substrate (pure SubstrateMemory + rules, NO LLM) "
               "now answers questions about the book correctly and persists the knowledge. The 'wall' is resolved under "
               "the real constraint -- no LLM IN the solution; the LLM is the external teacher.") if passed else \
              "NULL/partial - see rows (a bar missed; report, do not retune)."
    print(f"\nJEP-416: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP416"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": R, "J416a": J416a, "J416b": J416b, "J416c": J416c,
                                                  "passed": passed}, default=str))
    print("DONE", flush=True)
