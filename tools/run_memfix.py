"""Generic memory-deadlock mechanism sweep. Patches BET-099's make_cfg with a swept knob (+ fixed
extras) and runs LOC+UNI for each value, reporting selective write/recall fractions. Used to test
directional/self-limiting-write variants in parallel.

Usage: run_memfix LABEL BUDGET KNOB v1,v2,... '{"extra":val,...}'
"""
import sys, json
from pathlib import Path
import tools.run_bet099 as b99

_orig = b99.make_cfg
STATE = {"knob": None, "val": None, "extras": {}}
INT_KNOBS = {"global_wta_k", "n_emit"}


def make_cfg_patched():
    cfg = _orig()
    for k, v in STATE["extras"].items():
        object.__setattr__(cfg, k, int(v) if k in INT_KNOBS else v)
    kn = STATE["knob"]
    val = int(STATE["val"]) if kn in INT_KNOBS else STATE["val"]
    object.__setattr__(cfg, kn, val)
    return cfg


b99.make_cfg = make_cfg_patched


def frac(log, phase, min_s=None):
    rows = [e for e in log if e["phase"] == phase and (min_s is None or e["sim_s"] >= min_s)]
    return (sum(1 for e in rows if e["stim_mean"] > 3.0 and e["ctrl_mean"] < 3.0) / len(rows)) if rows else 0.0


if __name__ == "__main__":
    label = sys.argv[1]
    budget = int(sys.argv[2])
    knob = sys.argv[3]
    values = [float(x) for x in sys.argv[4].split(",")]
    STATE["extras"] = json.loads(sys.argv[5]) if len(sys.argv) > 5 and sys.argv[5] else {}
    STATE["knob"] = knob
    print(f"=== {label}: sweep {knob} {values} extras={STATE['extras']} ===", flush=True)
    results = {}
    for v in values:
        STATE["val"] = v
        loc = b99.run_arm("LOC", uniform=False, wall_budget=budget)
        uni = b99.run_arm("UNI", uniform=True, wall_budget=budget)
        pm = loc["stim_end_s"] + 2000
        results[v] = dict(stim=frac(loc["log"], "STIM"), post=frac(loc["log"], "POST", pm),
                          uni_post=frac(uni["log"], "POST", pm),
                          fire_ratio=loc["stim_fire"] / max(loc["ctrl_fire"], 1))
        r = results[v]
        print(f"  {knob}={v}: stim-frac={r['stim']:.2f} post-frac={r['post']:.2f} uni-post={r['uni_post']:.2f} fire_ratio={r['fire_ratio']:.1f}", flush=True)

    working = [v for v in values if results[v]['stim'] >= 0.5 and results[v]['post'] >= 0.5 and results[v]['uni_post'] < 0.25]
    passed = len(working) > 0
    print("\n--- VERDICT ---", flush=True)
    print(f"working {knob}(s) (write+recall+control-fails): {working}", flush=True)
    print(f"{label}: {'PASS - selective persistent memory' if passed else 'NULL/partial'}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / label; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"results": {str(k): v for k, v in results.items()},
                                                  "working": working, "passed": passed}, indent=2, default=str))
    print("DONE", flush=True)
