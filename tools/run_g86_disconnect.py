"""G86 — quiet + local + DISCONNECTION. compartment_boundary=15 cuts cross-boundary bridge formation
(G86 engine change) AND gates cross-boundary charge integration (BET-103). With quiet (cull) + local
emission, stim and control are fully disconnected -> percolation can't reach control -> selective.
The definitive test of the percolation diagnosis (G85).
"""
import sys, json
from pathlib import Path
import tools.run_g84_quiet_memory as g84

_orig = g84.make_cfg
def mc():
    c = _orig()
    object.__setattr__(c, 'emit_speed', 6.0)
    object.__setattr__(c, 'compartment_boundary', 15.0)
    return c
g84.make_cfg = mc

if __name__ == "__main__":
    budget = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    print("=== G86: quiet + local + DISCONNECTION (cut cross-region bridges + charge) ===", flush=True)
    loc = g84.run_arm("LOC", uniform=False, wall_budget=budget)
    uni = g84.run_arm("UNI", uniform=True, wall_budget=budget)
    pm = loc["stim_end_s"] + 2000
    stim = g84.frac(loc["log"], "STIM"); post = g84.frac(loc["log"], "POST", pm); uni_post = g84.frac(uni["log"], "POST", pm)
    G86a = stim >= 0.5; G86b = post >= 0.5; G86c = uni_post < 0.25
    passed = G86a and G86b and G86c
    print(f"\nLOC stim-frac={stim:.2f} post-frac={post:.2f} | UNI post-frac={uni_post:.2f}", flush=True)
    print(f"G86a selective write={G86a} | G86b persistent recall={G86b} | G86c control fails={G86c}", flush=True)
    print(("G86: PASS - SELECTIVE PERSISTENT MEMORY (disconnection breaks the deadlock)" if passed
           else "G86: NULL/partial - deadlock persists even with full disconnection"), flush=True)
    out = Path.home() / ".eqmod" / "bet" / "G86"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"stim": stim, "post": post, "uni_post": uni_post, "passed": passed}, indent=2, default=str))
    print("DONE", flush=True)
