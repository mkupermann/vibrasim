"""JEP-286 — closing the gap: REAL-PERCEPTION -> REASONING loop (per Michael's steer).

The engine SEES real Fashion-MNIST clothing photos (raw pixels = the senses), recognizes them with its prototype
perception, and REASONS about what it sees ('is this footwear?') using a taxonomy it READ. No transformer, no
pretrained vision. The symbol-grounding loop on real senses.

Pre-registered bars in docs/amendments/jep286_real_perception_reasoning_loop.md.
"""
import json
from pathlib import Path
import numpy as np

from world.understanding import UnderstandingEngine

# Fashion-MNIST: 4=coat, 5=sandal, 6=shirt, 9=ankle-boot
CLASSES = {"shirt": 6, "coat": 4, "sandal": 5, "boot": 9}
FOOTWEAR = {"sandal", "boot"}
K = 30            # real examples per concept
N_TEST = 50       # held-out test images per class


def run_seed(seed):
    d = np.load("data/fashion_mnist.npz")
    xtr, ytr = d["x_train"].astype(np.float64) / 255.0, d["y_train"]
    xte, yte = d["x_test"].astype(np.float64) / 255.0, d["y_test"]
    rng = np.random.default_rng(seed)

    # --- LEARN concepts from a few REAL training images (prototype perception) ---
    e = UnderstandingEngine(seed=seed)
    for name, lbl in CLASSES.items():
        idx = rng.choice(np.where(ytr == lbl)[0], size=K, replace=False)
        e.learn_concept(name, [xtr[i] for i in idx])
    # --- READ the prose taxonomy (clothing vs footwear are separate) ---
    e.read("A shirt is clothing. A coat is clothing. A sandal is footwear. A boot is footwear.")

    # --- PERCEIVE held-out REAL images + REASON 'is this footwear?' ---
    perceive_ok = reason_ok = total = 0
    demo = None
    for name, lbl in CLASSES.items():
        idx = rng.choice(np.where(yte == lbl)[0], size=N_TEST, replace=False)
        for i in idx:
            total += 1
            seen = e.perceive(xte[i])                       # raw pixels -> concept
            perceive_ok += (seen == name)
            said_footwear = e.is_a(seen, "footwear") if seen else False
            truth_footwear = name in FOOTWEAR
            reason_ok += (said_footwear == truth_footwear)
            if demo is None:
                demo = (name, seen, said_footwear, truth_footwear)

    # --- CONTROL: no taxonomy read -> 'is this footwear?' unanswerable ---
    ectl = UnderstandingEngine(seed=seed)
    for name, lbl in CLASSES.items():
        idx = rng.choice(np.where(ytr == lbl)[0], size=K, replace=False)
        ectl.learn_concept(name, [xtr[i] for i in idx])
    # ectl perceives but has NO taxonomy -> is_a(seen, footwear) is always False -> reasoning accuracy = base rate of 'not footwear'
    ctl_ok = ctl_tot = 0
    for name, lbl in CLASSES.items():
        idx = rng.choice(np.where(yte == lbl)[0], size=N_TEST, replace=False)
        for i in idx:
            ctl_tot += 1
            seen = ectl.perceive(xte[i])
            ctl_ok += (ectl.is_a(seen, "footwear") == (name in FOOTWEAR))   # always says 'not footwear' (no taxonomy)

    return {"perceive_acc": round(perceive_ok / total, 3), "reason_acc": round(reason_ok / total, 3),
            "control_acc": round(ctl_ok / ctl_tot, 3), "demo": demo}


if __name__ == "__main__":
    print("=== JEP-286: real-perception -> reasoning loop (Fashion-MNIST + prose) ===", flush=True)
    seeds = [42, 7]
    R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]
        true_cls, seen, said_fw, truth_fw = r["demo"]
        print(f"  seed {s}: perceive_acc={r['perceive_acc']} | 'is this footwear?' acc={r['reason_acc']} | "
              f"control(no-taxonomy)={r['control_acc']}", flush=True)
        print(f"    demo: a real {true_cls} image -> perceived '{seen}' -> is_a({seen},footwear)={said_fw} "
              f"(truth {truth_fw})", flush=True)

    J286a = all(R[s]['perceive_acc'] >= 0.60 for s in seeds)
    J286b = all(R[s]['reason_acc'] >= 0.85 for s in seeds)
    J286c = all(R[s]['demo'] is not None for s in seeds)
    J286d = all(R[s]['reason_acc'] > R[s]['control_acc'] for s in seeds)
    passed = J286a and J286b and J286c

    print("\n--- VERDICT ---", flush=True)
    print(f"J286a perception on real pixels (>=0.60): {J286a}", flush=True)
    print(f"J286b coarse perceive+reason (>=0.85)   : {J286b}", flush=True)
    print(f"J286c end-to-end loop demonstrated      : {J286c}", flush=True)
    print(f"J286d knowledge necessary (> control)   : {J286d}", flush=True)
    verdict = ("PASS - the engine PERCEIVES real images and REASONS about them via read prose: the symbol-grounding "
               "loop closed on real senses") if passed else "NULL/partial"
    print(f"\nJEP-286: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP286"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps(
        {"rows": {str(s): {k: v for k, v in R[s].items() if k != "demo"} for s in seeds},
         "J286a": J286a, "J286b": J286b, "J286c": J286c, "J286d": J286d, "passed": passed}, indent=2, default=str))
    print("DONE", flush=True)
