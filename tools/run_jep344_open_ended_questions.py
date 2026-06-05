"""JEP-344 — open-ended questions once ready (Michael rule #1). No transformer.
Pre-registered bars in docs/amendments/jep344_open_ended_questions.md.
"""
import json, tempfile, subprocess, sys, os
from pathlib import Path
from world.conversation import Conversation


def run_seed(seed):
    # READY brain: teach enough connected facts first
    dr = tempfile.mkdtemp(prefix=f"oeq_{seed}_")
    c = Conversation(brain_dir=dr, seed=seed)
    for s in ["A poodle is a dog.", "A dog is a mammal.", "A mammal is an animal.", "A cat is a mammal.",
              "A bird is an animal.", "A sparrow is a bird."]:
        c.say(s)
    ready_facts = c.n_facts
    # causal teach -> "why do you think" question
    r_cause = c.say("Smoking causes cancer.")
    why_ok = "why do you think" in r_cause.lower() and "smoking" in r_cause.lower() and "cancer" in r_cause.lower()
    # is-a with unknown top -> "what is X?" question (teach 'a guppy is a fish', fish unknown)
    r_isa = c.say("A guppy is a fish.")
    whatis_ok = "what is" in r_isa.lower() and "fish" in r_isa.lower()

    # NOT ready brain: few facts -> no open-ended question
    dn = tempfile.mkdtemp(prefix=f"oeq2_{seed}_")
    c2 = Conversation(brain_dir=dn, seed=seed)
    r1 = c2.say("A poodle is a dog.")
    gated_ok = ("why do you think" not in r1.lower() and "what is" not in r1.lower())

    return {"ready_facts": ready_facts, "why_ok": bool(why_ok), "whatis_ok": bool(whatis_ok),
            "gated_ok": bool(gated_ok), "cause_resp": r_cause, "isa_resp": r_isa}


def regression(repo):
    outs = {}
    for name in ["run_jep340_conversation", "run_jep342_make_connections"]:
        r = subprocess.run([sys.executable, f"tools/{name}.py"], capture_output=True, text=True,
                           env={**os.environ, "PYTHONPATH": repo})
        num = name.split("jep")[1][:3]
        outs[num] = f"JEP-{num}: PASS" in r.stdout
    return outs


if __name__ == "__main__":
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print("=== JEP-344: open-ended questions once ready (rule #1) ===", flush=True)
    seeds = [0, 7]; R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]
        print(f"  seed {s}: why_ok={r['why_ok']} whatis_ok={r['whatis_ok']} gated_ok={r['gated_ok']}", flush=True)
        print(f"      causal -> {r['cause_resp']}", flush=True)
        print(f"      is-a   -> {r['isa_resp']}", flush=True)
    reg = regression(repo)
    print(f"  regression: {reg}", flush=True)

    J344a = all(R[s]['why_ok'] and R[s]['whatis_ok'] for s in seeds)
    J344b = all(R[s]['gated_ok'] for s in seeds)
    J344c = all(reg.values())
    passed = J344a and J344b and J344c
    print("\n--- VERDICT ---", flush=True)
    print(f"J344a asks open-ended (why / what-is) when ready: {J344a}", flush=True)
    print(f"J344b gated -- not-ready asks nothing            : {J344b}", flush=True)
    print(f"J344c no regression (340, 342)                   : {J344c}", flush=True)
    verdict = ("PASS - once ready, the brain asks open-ended Socratic questions back (why? what is X?), gated on "
               "enough connected knowledge (Michael rule #1)") if passed else "NULL/partial"
    print(f"\nJEP-344: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP344"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": R, "reg": reg, "J344a": J344a, "J344b": J344b,
                                                  "J344c": J344c, "passed": passed}, default=str))
    print("DONE", flush=True)
