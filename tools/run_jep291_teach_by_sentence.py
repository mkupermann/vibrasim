"""JEP-291 — teaching by SENTENCE (per Michael: "later when it can understand more I answer with sentences").

The teacher's answer is now a full SENTENCE. It does two jobs at once: (1) NAMES the perceived thing ('This is a
dog') -> grounds the percept to that symbol; (2) TEACHES facts ('A dog is a mammal') -> read() into the engine. So
one sentence binds perception to knowledge, and the engine can then perceive a new image of that thing AND reason
about it. No transformer, no pretrained model.

Pre-registered bars in docs/amendments/jep291_teach_by_sentence.md.
"""
import json, re
from pathlib import Path
import numpy as np

from world.active_learner import ActiveLearner
from world.understanding import UnderstandingEngine

CLASSES = {"shirt": 6, "coat": 4, "sandal": 5, "boot": 9}


def teach_sentence(al, eng, modality, x, sentence):
    """The teacher answers with a sentence. Ground the percept from its FIRST clause ('This/It is a X' or 'a X'),
    and read() the WHOLE thing so its facts enter the engine. Returns the grounded name."""
    s = sentence.strip()
    m = re.match(r"(?:this|it|that)\s+is\s+(?:an?\s+|the\s+)?([a-z][a-z0-9\- ]*?)\s*[.,]", s.lower() + ".")
    if not m:
        m = re.match(r"^(?:an?\s+|the\s+)?([a-z][a-z0-9\- ]*?)\b", s.lower())
    name = eng._norm(m.group(1).split()[-1]) if m else None
    if name:
        al.teach(modality, name, np.asarray(x, dtype=np.float64))     # ground the percept to the named symbol
    eng.read(sentence)                                                # learn the sentence's facts (taxonomy etc.)
    return name


def run_seed(seed):
    d = np.load("data/fashion_mnist.npz")
    xtr, ytr = d["x_train"].astype(np.float64) / 255.0, d["y_train"]
    xte, yte = d["x_test"].astype(np.float64) / 255.0, d["y_test"]
    rng = np.random.default_rng(seed)

    al = ActiveLearner(tau=0.12)
    eng = UnderstandingEngine(seed=seed)
    # The teacher teaches each class with a SENTENCE that both names it and states a fact.
    SENTENCES = {
        "shirt": "This is a shirt. A shirt is clothing.",
        "coat": "This is a coat. A coat is clothing.",
        "sandal": "This is a sandal. A sandal is footwear.",
        "boot": "This is a boot. A boot is footwear.",
    }
    grounded = {}
    for name, lbl in CLASSES.items():
        for i in rng.choice(np.where(ytr == lbl)[0], 30, replace=False):
            grounded[name] = teach_sentence(al, eng, "sight", xtr[i], SENTENCES[name])

    # Now PERCEIVE held-out images and REASON, using ONLY what the teacher's SENTENCES grounded + taught.
    ok = tot = 0
    demo = None
    for name, lbl in CLASSES.items():
        for i in rng.choice(np.where(yte == lbl)[0], 50, replace=False):
            tot += 1
            sym, _ = al.guess("sight", xte[i])
            said_fw = eng.is_a(sym, "footwear") if sym else False
            ok += (said_fw == (name in {"sandal", "boot"}))
            if demo is None:
                demo = (name, sym, said_fw)

    # demonstrate the two jobs of one sentence: grounding worked AND facts were learned
    grounding_ok = all(grounded[n] == n for n in CLASSES)
    facts_ok = eng.is_a("shirt", "clothing") and eng.is_a("sandal", "footwear")
    return {"reason_acc": round(ok / tot, 3), "grounding_ok": bool(grounding_ok), "facts_ok": bool(facts_ok),
            "demo": demo}


if __name__ == "__main__":
    print("=== JEP-291: teaching by SENTENCE (name + facts in one answer) ===", flush=True)
    seeds = [42, 7]
    R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]; n, sym, fw = r["demo"]
        print(f"  seed {s}: perceive+reason acc={r['reason_acc']} | sentence grounded the percept={r['grounding_ok']} "
              f"& taught the facts={r['facts_ok']} | demo: real {n} -> '{sym}' -> footwear={fw}", flush=True)

    J291a = all(R[s]['grounding_ok'] for s in seeds)
    J291b = all(R[s]['facts_ok'] for s in seeds)
    J291c = all(R[s]['reason_acc'] >= 0.85 for s in seeds)
    try:
        import importlib; importlib.reload(importlib.import_module("tools.teach_gui")); J291d = True
    except Exception as ex:
        J291d = False; print("  teach_gui:", ex, flush=True)
    passed = J291a and J291b and J291c

    print("\n--- VERDICT ---", flush=True)
    print(f"J291a sentence GROUNDS the percept (names it): {J291a}", flush=True)
    print(f"J291b sentence TEACHES facts (read into engine): {J291b}", flush=True)
    print(f"J291c perceive+reason from sentence-teaching   : {J291c}", flush=True)
    print(f"J291d GUI sentence path present                : {J291d}", flush=True)
    verdict = ("PASS - the teacher's SENTENCE both names the percept and teaches facts; the engine perceives a new "
               "image and reasons about it from that one sentence") if passed else "NULL/partial"
    print(f"\nJEP-291: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP291"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps(
        {"rows": {str(s): R[s] for s in seeds}, "J291a": J291a, "J291b": J291b, "J291c": J291c, "J291d": J291d,
         "passed": passed}, indent=2, default=str))
    print("DONE", flush=True)
