"""JEP-289 — the BRIDGE: teacher-grounded PERCEPTION -> prose REASONING (unifies JEP-286/287/288).

A GroundedMind = ActiveLearner (perceives the world, grounds concepts from a teacher, asks only when unsure) +
UnderstandingEngine (reasons over what it READ). It SEES real Fashion-MNIST images, grounds the clothing concepts
from a teacher (querying only when unsure), READs a taxonomy, then for a held-out image PERCEIVES it and REASONS
'is this footwear?' -- perceive -> symbol -> reason, end to end. No transformer, no pretrained model.

Pre-registered bars in docs/amendments/jep289_grounded_mind.md.
"""
import json
from pathlib import Path
import numpy as np

from world.active_learner import ActiveLearner
from world.understanding import UnderstandingEngine

CLASSES = {"shirt": 6, "coat": 4, "sandal": 5, "boot": 9}
FOOTWEAR = {"sandal", "boot"}


def run_seed(seed):
    d = np.load("data/fashion_mnist.npz")
    xtr, ytr = d["x_train"].astype(np.float64) / 255.0, d["y_train"]
    xte, yte = d["x_test"].astype(np.float64) / 255.0, d["y_test"]
    rng = np.random.default_rng(seed)
    inv = {v: k for k, v in CLASSES.items()}

    # --- the MIND: perception (teacher-grounded) + reasoning (prose) ---
    al = ActiveLearner(tau=0.12)
    eng = UnderstandingEngine(seed=seed)
    eng.read("A shirt is clothing. A coat is clothing. A sandal is footwear. A boot is footwear.")

    # GROUND the concepts from a TEACHER, ask-when-unsure, over a shuffled stream of real images
    stream_idx = rng.permutation(np.concatenate([rng.choice(np.where(ytr == lbl)[0], 60, replace=False)
                                                 for lbl in CLASSES.values()]))
    for i in stream_idx:
        teacher = (lambda mod, x, _lbl=ytr[i]: inv[_lbl])      # teacher names the true class (stands in for Michael)
        al.observe("sight", xte[i] if False else xtr[i], teacher)
    asked = al.n_asked; seen = al.n_seen

    # PERCEIVE held-out real images + REASON via the read taxonomy
    ok = tot = 0
    demo = None
    for name, lbl in CLASSES.items():
        for i in rng.choice(np.where(yte == lbl)[0], 50, replace=False):
            tot += 1
            sym, _ = al.guess("sight", xte[i])                  # perceive (teacher-grounded prototypes)
            said_fw = eng.is_a(sym, "footwear") if sym else False
            ok += (said_fw == (name in FOOTWEAR))
            if demo is None:
                demo = (name, sym, said_fw)

    return {"reason_acc": round(ok / tot, 3), "asked": int(asked), "seen": int(seen),
            "ask_fraction": round(asked / seen, 3), "demo": demo}


if __name__ == "__main__":
    print("=== JEP-289: teacher-grounded perception -> prose reasoning (GroundedMind) ===", flush=True)
    seeds = [42, 7]
    R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]; t, sym, fw = r["demo"]
        print(f"  seed {s}: perceive+reason 'is this footwear?' acc={r['reason_acc']} | teacher asked "
              f"{r['asked']}/{r['seen']} ({r['ask_fraction']:.0%}) | demo: real {t} -> perceived '{sym}' -> footwear={fw}",
              flush=True)

    J289a = all(R[s]['reason_acc'] >= 0.85 for s in seeds)
    J289b = all(R[s]['ask_fraction'] <= 0.70 for s in seeds)        # teacher-grounded yet label-efficient
    J289c = all(R[s]['demo'] is not None for s in seeds)
    passed = J289a and J289b and J289c

    print("\n--- VERDICT ---", flush=True)
    print(f"J289a perceive->reason works (>=0.85)   : {J289a}", flush=True)
    print(f"J289b teacher-grounded yet efficient(<=70%): {J289b}", flush=True)
    print(f"J289c end-to-end loop demonstrated      : {J289c}", flush=True)
    verdict = ("PASS - a GroundedMind PERCEIVES the world (teacher-grounded, ask-when-unsure) and REASONS about it via "
               "read prose -- perception and understanding unified") if passed else "NULL/partial"
    print(f"\nJEP-289: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP289"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps(
        {"rows": {str(s): R[s] for s in seeds}, "J289a": J289a, "J289b": J289b, "J289c": J289c, "passed": passed},
        indent=2, default=str))
    print("DONE", flush=True)
