"""JEP-287 — slow, confidence-gated letter learning with a TEACHER (per Michael's steer).

Render written letters A-Z, then learn them with the ActiveLearner: ASK the teacher only when UNSURE. Compare to
passive (ask every item) to prove ask-when-unsure is label-efficient. The teacher is an oracle here (stands in for
Michael; tools/teach_gui.py is the live GUI). No transformer, no pretrained model.

Pre-registered bars in docs/amendments/jep287_active_learning_teacher.md.
"""
import json, string
from pathlib import Path
import numpy as np

from world.active_learner import ActiveLearner

LETTERS = string.ascii_uppercase
SIZE = 28


def _center(a):
    """Shift the glyph so its centre of mass is at the frame centre (removes position jitter -> raw-pixel prototypes
    of the same letter align). A simple, no-AI normalization a real visual system would do via foveation."""
    ys, xs = np.nonzero(a > 0.3)
    if len(xs) == 0:
        return a
    cy, cx = ys.mean(), xs.mean()
    sy, sx = int(round(SIZE / 2 - cy)), int(round(SIZE / 2 - cx))
    return np.roll(np.roll(a, sy, axis=0), sx, axis=1)


def render_letter(ch, rng):
    """A 'written letter' image: a font glyph + size/noise jitter, then CENTRED (PIL; not AI)."""
    from PIL import Image, ImageDraw, ImageFont
    img = Image.new("L", (SIZE, SIZE), 0)
    d = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", int(rng.integers(18, 24)))
    except Exception:
        font = ImageFont.load_default()
    d.text((int(rng.integers(3, 7)), int(rng.integers(2, 5))), ch, fill=255, font=font)
    a = np.asarray(img, dtype=np.float64) / 255.0
    a = _center(a)
    a += rng.normal(0, 0.06, a.shape)                 # sensory noise (after centring)
    return np.clip(a, 0, 1).ravel()


def make_data(seed, per_letter):
    rng = np.random.default_rng(seed)
    X, Y = [], []
    for ch in LETTERS:
        for _ in range(per_letter):
            X.append(render_letter(ch, rng)); Y.append(ch)
    idx = rng.permutation(len(X))
    return [X[i] for i in idx], [Y[i] for i in idx]


def run_seed(seed):
    Xtr, Ytr = make_data(seed, 40)
    Xte, Yte = make_data(seed + 100, 12)
    truth_map = {}                                     # the oracle teacher: returns the true label for an example

    # --- ACTIVE: ask only when UNSURE ---
    al = ActiveLearner(tau=0.10)
    conf_hits = conf_n = unsure_hits = unsure_n = 0
    for x, y in zip(Xtr, Ytr):
        teacher = (lambda mod, xx, _y=y: _y)           # oracle stands in for Michael
        sym, asked, correct = al.observe("write", x, teacher)
        if not asked:                                  # it was CONFIDENT -> check whether it was right (J287c)
            conf_n += 1; conf_hits += (sym == y)
        else:
            unsure_n += 1; unsure_hits += (correct is True)
    active_asked = al.n_asked
    active_acc = np.mean([al.guess("write", x)[0] == y for x, y in zip(Xte, Yte)])
    conf_acc = conf_hits / max(conf_n, 1)
    unsure_acc = unsure_hits / max(unsure_n, 1)

    # --- PASSIVE: ask the teacher on EVERY item ---
    pl = ActiveLearner(tau=0.10)
    for x, y in zip(Xtr, Ytr):
        pl.teach("write", y, x)                        # teacher labels everything
    passive_asked = len(Xtr)
    passive_acc = np.mean([pl.guess("write", x)[0] == y for x, y in zip(Xte, Yte)])

    return {"active_acc": round(float(active_acc), 3), "active_asked": int(active_asked),
            "passive_acc": round(float(passive_acc), 3), "passive_asked": int(passive_asked),
            "ask_fraction": round(active_asked / passive_asked, 3),
            "confident_acc": round(conf_acc, 3), "unsure_acc": round(unsure_acc, 3),
            "n_train": len(Xtr)}


if __name__ == "__main__":
    print("=== JEP-287: slow letter learning with a teacher (ask-when-unsure) ===", flush=True)
    seeds = [42, 7]
    R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]
        print(f"  seed {s}: ACTIVE acc={r['active_acc']} asked={r['active_asked']}/{r['n_train']} "
              f"({r['ask_fraction']:.0%}) | PASSIVE acc={r['passive_acc']} asked={r['passive_asked']} | "
              f"confident-acc={r['confident_acc']} vs unsure-acc={r['unsure_acc']}", flush=True)

    J287a = all(R[s]['active_acc'] >= 0.85 for s in seeds)
    J287b = all(R[s]['ask_fraction'] <= 0.60 and R[s]['active_acc'] >= R[s]['passive_acc'] - 0.05 for s in seeds)
    J287c = all(R[s]['confident_acc'] > R[s]['unsure_acc'] for s in seeds)
    # J287d: the GUI tool exists + imports
    try:
        import importlib; importlib.import_module("tools.teach_gui"); J287d = True
    except Exception as ex:
        J287d = False; print("  teach_gui import:", ex, flush=True)
    passed = J287a and J287b and J287c

    print("\n--- VERDICT ---", flush=True)
    print(f"J287a learns the alphabet (active acc>=.85): {J287a}", flush=True)
    print(f"J287b ask-when-unsure label-efficient(<=60%): {J287b}", flush=True)
    print(f"J287c confidence tracks correctness         : {J287c}", flush=True)
    print(f"J287d live teaching GUI exists + imports    : {J287d}", flush=True)
    verdict = ("PASS - the 'train slowly, ask me when unsure' teacher loop works and is label-efficient") if passed \
        else "NULL/partial"
    print(f"\nJEP-287: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP287"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps(
        {"rows": {str(s): R[s] for s in seeds}, "J287a": J287a, "J287b": J287b, "J287c": J287c, "J287d": J287d,
         "passed": passed}, indent=2, default=str))
    print("DONE", flush=True)
