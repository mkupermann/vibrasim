"""G85 — QUIET substrate + LOCAL emission. Combines the two fixes: cull the background every tick
(quiet -> control not self-active, input registers) AND low emit_speed (local -> the write field
stays near stim, never reaches control). G84 showed control latches via fast emission transit
(emit_speed=30 = 15 units/tick = stim->control distance); low emit_speed keeps emissions local.
Sweep emit_speed low. The untested combination at the root of the deadlock.

Pre-registered bars in docs/amendments/g85_quiet_local.md.
"""
import sys, json
from pathlib import Path
import tools.run_g84_quiet_memory as g84

_orig = g84.make_cfg
EMIT = [3.0]


def make_cfg_local():
    c = _orig()
    object.__setattr__(c, 'emit_speed', EMIT[0])
    return c


g84.make_cfg = make_cfg_local


if __name__ == "__main__":
    budget = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    speeds = [3.0, 6.0, 12.0]
    print("=== G85: quiet substrate + LOCAL emission (emit_speed sweep) ===", flush=True)
    results = {}
    for sp in speeds:
        EMIT[0] = sp
        loc = g84.run_arm("LOC", uniform=False, wall_budget=budget)
        uni = g84.run_arm("UNI", uniform=True, wall_budget=budget)
        pm = loc["stim_end_s"] + 2000
        results[sp] = dict(stim=g84.frac(loc["log"], "STIM"),
                           post=g84.frac(loc["log"], "POST", pm),
                           uni_post=g84.frac(uni["log"], "POST", pm))
        r = results[sp]
        print(f"  emit_speed={sp}: stim-frac={r['stim']:.2f} post-frac={r['post']:.2f} uni-post={r['uni_post']:.2f}", flush=True)

    working = [sp for sp in speeds if results[sp]['stim'] >= 0.5 and results[sp]['post'] >= 0.5 and results[sp]['uni_post'] < 0.25]
    passed = len(working) > 0
    print("\n--- VERDICT ---", flush=True)
    print(f"working emit_speed(s): {working}", flush=True)
    verdict = ("PASS - SELECTIVE PERSISTENT MEMORY (quiet + local emission breaks the deadlock at its root)"
               if passed else "NULL/partial - deadlock persists even with quiet + local emission")
    print(f"G85: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "G85"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"results": {str(k): v for k, v in results.items()},
                                                  "working": working, "passed": passed}, indent=2, default=str))
    print("DONE", flush=True)
