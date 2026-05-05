"""Frequency-histogram observation tool over a snapshot."""
from __future__ import annotations
import argparse
from collections import Counter
import math
from pathlib import Path
import numpy as np
from world.snapshot import load_snapshot


def compute_histogram_text(snapshot_path: Path) -> str:
    w = load_snapshot(snapshot_path)
    lines = [f"Snapshot: {snapshot_path.name} | t = {w.t:.2f}"]

    # Vibrations
    alive_v = w.s_alive
    if alive_v.any():
        decade_counts = Counter(int(math.floor(math.log10(f))) for f in w.s_freq[alive_v] if f > 0)
        lines.append(f"vibrations ({int(alive_v.sum())}): "
                     + ", ".join(f"10^{d}: {c}" for d, c in sorted(decade_counts.items())))
    else:
        lines.append("vibrations: 0")

    # Nodes per level
    for level, name in [(1, "electrons"), (2, "pairs"), (3, "triads"), (4, "atoms")]:
        mask = (w.k_level == level) & w.k_alive
        if mask.any():
            decade_counts = Counter(int(math.floor(math.log10(f))) for f in w.k_freq[mask] if f > 0)
            lines.append(f"{name} ({int(mask.sum())}): "
                         + ", ".join(f"10^{d}: {c}" for d, c in sorted(decade_counts.items())))
        else:
            lines.append(f"{name}: 0")

    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="tools/histogram.py")
    parser.add_argument("snapshot", type=Path)
    parser.add_argument("--format", choices=["text", "png"], default="text")
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args(argv)

    if args.format == "text":
        out = compute_histogram_text(args.snapshot)
        if args.output:
            args.output.write_text(out)
        else:
            print(out)
    elif args.format == "png":
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            print("matplotlib not installed; install via `pip install matplotlib`")
            return 1
        # Simple multi-panel histogram
        w = load_snapshot(args.snapshot)
        fig, axes = plt.subplots(1, 5, figsize=(15, 3))
        for ax, (level, name) in zip(axes, [(0, "vibrations"), (1, "electrons"),
                                              (2, "pairs"), (3, "triads"), (4, "atoms")]):
            if level == 0:
                freqs = w.s_freq[w.s_alive]
            else:
                mask = (w.k_level == level) & w.k_alive
                freqs = w.k_freq[mask]
            if len(freqs) > 0:
                ax.hist(np.log10(freqs[freqs > 0]), bins=20)
            ax.set_title(name)
            ax.set_xlabel("log10(freq)")
        fig.tight_layout()
        fig.savefig(args.output or "histogram.png", dpi=150)
        plt.close(fig)
        print(f"Wrote {args.output or 'histogram.png'}")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
