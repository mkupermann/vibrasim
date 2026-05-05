"""60-second headless smoke test against INITIAL_CONFIG. Excluded from default pytest."""
from __future__ import annotations
import sys
import numpy as np
from world.config import INITIAL_CONFIG
from world.state import World
from world.physics import tick


def main() -> int:
    cfg = INITIAL_CONFIG
    w = World(cfg)
    duration = 60.0
    n_ticks = int(duration / cfg.dt)
    seen = {1: 0, 2: 0, 3: 0, 4: 0}
    for _ in range(n_ticks):
        tick(w, cfg.dt)
        for level in (1, 2, 3, 4):
            seen[level] = max(seen[level],
                              int(np.sum((w.k_level[:w.k_count] == level) &
                                         w.k_alive[:w.k_count])))
    print(f"max counts: e- {seen[1]} | pair {seen[2]} | triad {seen[3]} | atom {seen[4]}")
    failures = []
    if seen[1] < 1: failures.append("no electrons formed")
    if seen[2] < 1: failures.append("no pairs formed")
    if seen[3] < 1: failures.append("no triads formed")
    if failures:
        print("FAIL:", "; ".join(failures))
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
