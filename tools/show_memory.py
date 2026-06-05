"""show_memory — answer Michael's question literally: what does the substrate's memory LOOK like, is it a file?

Teaches two facts into a REAL EnergyNet, then dumps exactly what is stored:
  - the weight matrix W (the 'memory') as numbers AND as a picture,
  - the +-1 firing pattern of a fact,
  - recall by energy relaxation (clamp half -> the rest lights up),
  - where (little) gets written to disk.

No transformer, no pretrained model. Run: PYTHONPATH=. .venv/Scripts/python.exe tools/show_memory.py
"""
import os
import numpy as np
from world.energy import EnergyNet

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs", "memory_picture.png")


def code(rng, n):
    return rng.choice([-1.0, 1.0], size=n)


def main():
    rng = np.random.default_rng(0)
    # one dense module so a KEY|VALUE fact is a single attractor that completes from its key half
    net = EnergyNet(n_per_module=80, n_modules=1, seed=0)   # N = 80 little units
    n = net.N // 2

    # two facts as KEY|VALUE bipolar patterns: "poodle is a dog", "salmon is a fish"
    poodle, dog = code(rng, n), code(rng, n)
    salmon, fish = code(rng, n), code(rng, n)
    fact_poodle = np.concatenate([poodle, dog])
    fact_salmon = np.concatenate([salmon, fish])

    # LEARN: nudge W so each fact becomes a low-energy valley (contrastive-Hebbian, local)
    W0 = net.W.copy()
    for _ in range(60):
        net.train_epoch([fact_poodle, fact_salmon], cue_frac=0.5, lr=0.02)

    # RECALL: clamp the KEY half ('poodle'), relax downhill, read the VALUE half
    key_idx = np.arange(n)
    out = net.relax(clamp_idx=key_idx, clamp_val=poodle, steps=40)
    recalled = out[n:]
    acc = float((np.sign(recalled) == np.sign(dog)).mean())

    print("=== WHAT THE SUBSTRATE'S MEMORY IS ===\n")
    print(f"The substrate here = {net.N} little units. Its MEMORY is ONE weight matrix W:")
    print(f"  W.shape       = {net.W.shape}   (an {net.N} x {net.N} grid of numbers)")
    print(f"  it is in RAM  = {type(net.W).__name__} (a numpy array), NOT a file")
    print(f"  before learning: W was all zeros (sum |W| = {np.abs(W0).sum():.1f})")
    print(f"  after learning : W changed       (sum |W| = {np.abs(net.W).sum():.1f})  <- the knowledge IS this change\n")

    print("A 6x6 corner of W (the actual stored numbers):")
    with np.printoptions(precision=2, suppress=True):
        print(net.W[:6, :6], "\n")

    print("A 'fact' is not text or a row -- it's a +-1 firing pattern (first 24 of 80 units):")
    print("  poodle-is-a-dog =", fact_poodle[:24].astype(int), "...\n")

    print(f"RECALL by energy relaxation: clamp 'poodle' -> network settles -> 'dog' half matches {acc:.0%}")
    print("  (no lookup, no filename -- it slides into the nearest valley)\n")

    # picture: render W as a heatmap so the shape of the 'memory' is visible
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(1, 2, figsize=(9, 4.2))
        ax[0].imshow(W0, cmap="RdBu", vmin=-0.5, vmax=0.5); ax[0].set_title("W before learning\n(blank = no memory)")
        ax[1].imshow(net.W, cmap="RdBu", vmin=-0.5, vmax=0.5); ax[1].set_title("W after learning 2 facts\n(the pattern IS the memory)")
        for a in ax:
            a.set_xlabel("unit"); a.set_ylabel("unit")
        fig.suptitle("The substrate's memory = a grid of connection strengths (in RAM, not a file)")
        fig.tight_layout(); fig.savefig(OUT, dpi=110)
        print(f"Picture of the memory written to: {OUT}")
    except Exception as ex:
        print("(matplotlib unavailable, skipped picture:", ex, ")")


if __name__ == "__main__":
    main()
