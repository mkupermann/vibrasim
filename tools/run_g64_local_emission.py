"""G64 — local-emission self-limiting write. BET-099 correlation memory, sweeping emit_speed
LOW (4/8/16 vs flooding 30): does short-range emission co-fire local neighbours (write) without
reaching control (no leak) -> selective persistent memory?

Pre-registered bars in docs/amendments/g64_local_emission_write.md.
"""
import sys, json
import numpy as np
from pathlib import Path
import tools.run_bet099 as b99

_orig = b99.make_cfg
SPEED = [30.0]   # set per-run below


def make_cfg_speed():
    cfg = _orig()
    object.__setattr__(cfg, 'emit_speed', SPEED[0])
    return cfg


b99.make_cfg = make_cfg_speed


def frac_selective(log, phase, min_s=None):
    rows = [e for e in log if e["phase"] == phase and (min_s is None or e["sim_s"] >= min_s)]
    if not rows:
        return 0.0
    return sum(1 for e in rows if e["stim_mean"] > 3.0 and e["ctrl_mean"] < 3.0) / len(rows)


if __name__ == "__main__":
    budget = int(sys.argv[1]) if len(sys.argv) > 1 else 150
    speeds = [4.0, 8.0, 16.0]
    print("=== G64: local-emission self-limiting write (emit_speed sweep) ===", flush=True)
    results = {}
    for sp in speeds:
        SPEED[0] = sp
        loc = b99.run_arm("LOC", uniform=False, wall_budget=budget)
        uni = b99.run_arm("UNI", uniform=True, wall_budget=budget)
        pm = loc["stim_end_s"] + 2000
        results[sp] = dict(
            stim=frac_selective(loc["log"], "STIM"),
            post=frac_selective(loc["log"], "POST", pm),
            uni_post=frac_selective(uni["log"], "POST", pm),
            fire_ratio=loc["stim_fire"] / max(loc["ctrl_fire"], 1),
        )
        r = results[sp]
        print(f"  emit_speed={sp}: stim-frac={r['stim']:.2f} post-frac={r['post']:.2f} "
              f"uni-post={r['uni_post']:.2f} fire_ratio={r['fire_ratio']:.1f}", flush=True)

    working = [sp for sp in speeds if results[sp]['stim'] >= 0.5 and results[sp]['post'] >= 0.5 and results[sp]['uni_post'] < 0.25]
    G64a = any(results[sp]['stim'] >= 0.5 for sp in speeds)
    G64b = any(results[sp]['stim'] >= 0.5 and results[sp]['post'] >= 0.5 for sp in speeds)
    G64c = len(working) > 0
    passed = G64c

    print("\n--- VERDICT ---", flush=True)
    print(f"working emit_speed(s) (write+recall+control-fails): {working}", flush=True)
    print(f"G64a some speed writes selectively : {G64a}", flush=True)
    print(f"G64b ...and recalls persistently   : {G64b}", flush=True)
    print(f"G64c ...with control failing        : {G64c}", flush=True)
    verdict = ("PASS - LOCAL EMISSION gives selective persistent memory (deadlock's firing form broken)"
               if passed else "NULL/partial - local emission insufficient; deadlock deeper than emission range")
    print(f"\nG64: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "G64"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"results": {str(k): v for k, v in results.items()},
                                                  "working": working, "passed": passed}, indent=2, default=str))
    print("DONE", flush=True)
