"""G65 — competitive inhibition (global k-WTA) for a selective write. BET-099 correlation memory +
global_wta_k sweep: only the top-K most-charged atoms fire -> stim wins, control suppressed ->
selective persistent memory?

Pre-registered bars in docs/amendments/g65_wta_inhibition_write.md.
"""
import sys, json
from pathlib import Path
import tools.run_bet099 as b99

_orig = b99.make_cfg
KVAL = [0]


def make_cfg_wta():
    cfg = _orig()
    object.__setattr__(cfg, 'global_wta_k', KVAL[0])
    return cfg


b99.make_cfg = make_cfg_wta


def frac_selective(log, phase, min_s=None):
    rows = [e for e in log if e["phase"] == phase and (min_s is None or e["sim_s"] >= min_s)]
    if not rows:
        return 0.0
    return sum(1 for e in rows if e["stim_mean"] > 3.0 and e["ctrl_mean"] < 3.0) / len(rows)


if __name__ == "__main__":
    budget = int(sys.argv[1]) if len(sys.argv) > 1 else 150
    ks = [5, 10, 20]
    print("=== G65: competitive inhibition (global k-WTA) selective write ===", flush=True)
    results = {}
    for k in ks:
        KVAL[0] = k
        loc = b99.run_arm("LOC", uniform=False, wall_budget=budget)
        uni = b99.run_arm("UNI", uniform=True, wall_budget=budget)
        pm = loc["stim_end_s"] + 2000
        results[k] = dict(stim=frac_selective(loc["log"], "STIM"),
                          post=frac_selective(loc["log"], "POST", pm),
                          uni_post=frac_selective(uni["log"], "POST", pm),
                          fire_ratio=loc["stim_fire"] / max(loc["ctrl_fire"], 1))
        r = results[k]
        print(f"  k={k}: stim-frac={r['stim']:.2f} post-frac={r['post']:.2f} uni-post={r['uni_post']:.2f} fire_ratio={r['fire_ratio']:.1f}", flush=True)

    working = [k for k in ks if results[k]['stim'] >= 0.5 and results[k]['post'] >= 0.5 and results[k]['uni_post'] < 0.25]
    G65a = any(results[k]['stim'] >= 0.5 for k in ks)
    G65b = any(results[k]['stim'] >= 0.5 and results[k]['post'] >= 0.5 for k in ks)
    G65c = len(working) > 0
    passed = G65c

    print("\n--- VERDICT ---", flush=True)
    print(f"working k(s) (write+recall+control-fails): {working}", flush=True)
    print(f"G65a some k writes selectively : {G65a}", flush=True)
    print(f"G65b ...and recalls persistently: {G65b}", flush=True)
    print(f"G65c ...with control failing    : {G65c}", flush=True)
    verdict = ("PASS - competitive inhibition gives SELECTIVE PERSISTENT memory (deadlock firing-form broken)"
               if passed else "NULL/partial - inhibition insufficient; deadlock survives")
    print(f"\nG65: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "G65"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"results": {str(k): v for k, v in results.items()},
                                                  "working": working, "passed": passed}, indent=2, default=str))
    print("DONE", flush=True)
