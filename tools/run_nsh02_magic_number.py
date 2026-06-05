"""NSH-02 — New-Science Hunt step 2: is the substrate's characteristic structure size a sharp 'magic
number'? Run the settling dynamics across many seeds at fixed density; characterize the distribution
of largest-structure sizes. Pre-registered bars in docs/amendments/nsh02_magic_number.md.
"""
import json
from dataclasses import replace
from pathlib import Path
import numpy as np

from world.state import World
from world.physics import tick, _largest_bridged_component
from tools.run_g43_protocell import cfg, SETTLE

N_SEEDS = 30
DENSITY = 300


def largest_structure(seed):
    c = replace(cfg(seed), n_initial_vibrations=DENSITY)
    w = World(c)
    for _ in range(SETTLE):
        tick(w, c.dt)
    comp = _largest_bridged_component(w)
    return len(comp) if comp else 0


if __name__ == "__main__":
    print(f"=== NSH-02: structure-size distribution across {N_SEEDS} seeds (n={DENSITY}) ===", flush=True)
    sizes = []
    for s in range(N_SEEDS):
        sizes.append(largest_structure(1000 + s))
        if (s + 1) % 10 == 0:
            print(f"  ...{s + 1}/{N_SEEDS} done", flush=True)
    sizes = np.array(sizes)
    mean, std = float(sizes.mean()), float(sizes.std())
    cv = std / mean if mean > 0 else 0.0
    # histogram in bins of 10
    lo, hi = (int(sizes.min()) // 10) * 10, (int(sizes.max()) // 10 + 1) * 10
    bins = np.arange(lo, hi + 10, 10)
    hist, edges = np.histogram(sizes, bins=bins)
    modal_i = int(np.argmax(hist))
    modal_center = (edges[modal_i] + edges[modal_i + 1]) / 2
    within = float(np.mean(np.abs(sizes - modal_center) <= 0.10 * modal_center))

    print(f"  sizes: {sorted(sizes.tolist())}", flush=True)
    print(f"  mean={mean:.1f} std={std:.1f} CV={cv:.3f} | modal bin center={modal_center:.0f} "
          f"holds {within*100:.0f}% within +/-10%", flush=True)
    print("  histogram (bin:count): " + " ".join(f"{int(edges[i])}-{int(edges[i+1])}:{hist[i]}"
                                                  for i in range(len(hist))), flush=True)

    NSH02a = cv <= 0.30
    NSH02b = within >= 0.40
    passed = NSH02a and NSH02b
    print("\n--- VERDICT ---", flush=True)
    print(f"NSH02a characteristic (CV<=0.30) : {NSH02a} (CV={cv:.3f})", flush=True)
    print(f"NSH02b clear preferred size      : {NSH02b} ({within*100:.0f}% within +/-10% of mode)", flush=True)
    verdict = ("PASS - the structure size is a sharply-preferred characteristic value (candidate "
               "native quantization)") if passed else "NULL/partial - size distribution is broad (no magic number)"
    print(f"\nNSH-02: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "NSH02"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"sizes": sizes.tolist(), "mean": mean, "std": std, "cv": cv,
                                                  "modal_center": modal_center, "within_10pct": within,
                                                  "passed": passed, "NSH02a": NSH02a, "NSH02b": NSH02b},
                                                 indent=2, default=str))
    print("DONE", flush=True)
