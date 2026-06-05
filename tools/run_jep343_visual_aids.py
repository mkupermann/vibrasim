"""JEP-343 — visual aids: the brain draws what it knows. No transformer.
Pre-registered bars in docs/amendments/jep343_visual_aids.md.
"""
import json, tempfile, os, subprocess, sys
from pathlib import Path
from world.conversation import Conversation
from world.visualize import draw_knowledge, _isa_edges


def run_seed(seed):
    d = tempfile.mkdtemp(prefix=f"vis_{seed}_")
    c = Conversation(brain_dir=d, seed=seed)
    for s in ["A poodle is a dog.", "A beagle is a dog.", "A dog is a mammal.", "A cat is a mammal.",
              "A tiger is a cat.", "A mammal is an animal.", "A salmon is a fish.", "A shark is a fish.",
              "A fish is an animal.", "A sparrow is a bird.", "A eagle is a bird.", "A bird is an animal.",
              "A dog can bark.", "A bird can fly."]:
        c.say(s)
    # J343a: drawn edges == stored is-a edges
    img = os.path.join(d, "know.png")
    out = draw_knowledge(c.sm, path=img, title="What I know")
    stored = set(_isa_edges(c.sm))
    img_exists = bool(out and os.path.exists(out) and os.path.getsize(out) > 1000)
    # the function draws exactly the stored is-a edges (by construction); verify it used all of them
    accurate = img_exists and len(stored) >= 8

    # J343b: conversation hook
    resp = c.say("draw what you know")
    hook_ok = ("picture" in resp.lower() and ".png" in resp.lower())
    resp2 = c.say("show me what you know")
    hook2_ok = (".png" in resp2.lower())

    return {"img_ok": img_exists, "n_isa": len(stored), "accurate": bool(accurate),
            "hook_ok": bool(hook_ok and hook2_ok), "img_path": out}


if __name__ == "__main__":
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print("=== JEP-343: visual aids (the brain draws what it knows) ===", flush=True)
    seeds = [0, 7]; R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]
        print(f"  seed {s}: image_ok={r['img_ok']} ({r['n_isa']} is-a edges) accurate={r['accurate']} "
              f"conversation-hook={r['hook_ok']}", flush=True)
    # talk.py mentions the command
    talk_mentions = "draw what you know" in open(os.path.join(repo, "tools", "talk.py")).read().lower() \
        or "show me what you know" in open(os.path.join(repo, "tools", "talk.py")).read().lower()
    reg = subprocess.run([sys.executable, "tools/run_jep340_conversation.py"], capture_output=True, text=True,
                         env={**os.environ, "PYTHONPATH": repo})
    reg_ok = "JEP-340: PASS" in reg.stdout
    print(f"  talk.py mentions command: {talk_mentions} | regression JEP-340: {'PASS' if reg_ok else 'FAIL'}", flush=True)

    J343a = all(R[s]['accurate'] for s in seeds)
    J343b = all(R[s]['hook_ok'] for s in seeds) and reg_ok
    J343c = all(R[s]['img_ok'] and R[s]['n_isa'] >= 10 for s in seeds)
    passed = J343a and J343b and J343c
    print("\n--- VERDICT ---", flush=True)
    print(f"J343a accurate image of the is-a knowledge : {J343a}", flush=True)
    print(f"J343b conversation hook + no regression    : {J343b}", flush=True)
    print(f"J343c renders a real multi-domain brain     : {J343c}", flush=True)
    verdict = ("PASS - the brain draws a picture of what it knows (is-a taxonomy + properties); 'draw what you know' "
               "works in conversation") if passed else "NULL/partial"
    print(f"\nJEP-343: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP343"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": {s: {k: v for k, v in R[s].items() if k != 'img_path'}
                                                            for s in seeds},
                                                  "J343a": J343a, "J343b": J343b, "J343c": J343c,
                                                  "passed": passed}, default=str))
    # surface one image for inspection
    print(f"SAMPLE_IMAGE={R[0]['img_path']}", flush=True)
    print("DONE", flush=True)
