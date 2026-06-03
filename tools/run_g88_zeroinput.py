"""G88 — zero-input diagnostic. Quiet + disconnected substrate (G86 config), inject NOTHING during
STIM. Does any region's bridges still latch to high?
- If YES -> the substrate SPONTANEOUSLY latches structure with no input => memory deadlock is
  fundamental (no stable blank state), confirming the close.
- If NO (stays at blank ~1.0) -> control latching in G84-G86 was STIM-COUPLED, a fixable isolation
  route => memory may be reopenable.
Reports stim/control region bridge means + total firings, with NO-INPUT vs STIM arms.
"""
import sys, json, time
import numpy as np
from pathlib import Path
from world.state import World
from world.physics import tick
from tools.run_bet090 import region_mean
from tools.run_bet093 import cull_free_vibrations
from tools.run_bet098 import inject_tight, blank_bridges
from tools.run_bet099 import make_cfg, WARMUP, STIM_END, HALF


def run_arm(name, inject, wall_budget=200):
    cfg = make_cfg()
    object.__setattr__(cfg, 'compartment_boundary', 15.0)   # disconnected
    object.__setattr__(cfg, 'emit_speed', 6.0)              # local
    w = World(cfg); dt = cfg.dt
    box = np.asarray(cfg.box_size); STIM_X, CTRL_X = box[0] * 0.25, box[0] * 0.75
    fires = 0
    log = []
    t0 = time.time()
    for step in range(40000):
        if step == WARMUP:
            object.__setattr__(cfg, 'lambda_gen', 0.0)
            cull_free_vibrations(w, keep_frac=0.0); blank_bridges(w, cfg.bistable_low)
        if WARMUP <= step < STIM_END:
            cull_free_vibrations(w, keep_frac=0.0)          # quiet
            if inject:
                inject_tight(w, cfg, box, STIM_X, n=40)
        if step == STIM_END:
            cull_free_vibrations(w, keep_frac=0.0)
        tick(w, dt)
        if WARMUP <= step < STIM_END:
            fires += sum(1 for tf, ai in w.firing_events if tf >= w.t - dt)
        if step % 1000 == 999:
            sim_s = round((step + 1) * dt, 1)
            sm, _ = region_mean(w, STIM_X, half=HALF); cm, _ = region_mean(w, CTRL_X, half=HALF)
            ph = ("WARM" if step < WARMUP else "STIM" if step < STIM_END else "POST")
            log.append({"sim_s": sim_s, "phase": ph, "stim": round(sm, 2), "ctrl": round(cm, 2)})
        if time.time() - t0 > wall_budget:
            break
    return {"name": name, "fires_during_stim": fires, "log": log}


def peak(log, phase, key):
    vals = [e[key] for e in log if e["phase"] == phase]
    return max(vals) if vals else 0.0


if __name__ == "__main__":
    budget = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    print("=== G88: zero-input diagnostic (quiet + disconnected) ===", flush=True)
    zero = run_arm("ZERO-INPUT", inject=False, wall_budget=budget)
    stim = run_arm("STIM", inject=True, wall_budget=budget)
    z_stim = peak(zero["log"], "STIM", "stim"); z_ctrl = peak(zero["log"], "STIM", "ctrl")
    s_stim = peak(stim["log"], "STIM", "stim"); s_ctrl = peak(stim["log"], "STIM", "ctrl")
    print(f"\nZERO-INPUT: peak stim-region bridge={z_stim:.2f} ctrl={z_ctrl:.2f} | fires={zero['fires_during_stim']}", flush=True)
    print(f"STIM:       peak stim-region bridge={s_stim:.2f} ctrl={s_ctrl:.2f} | fires={stim['fires_during_stim']}", flush=True)
    spontaneous = max(z_stim, z_ctrl) > 3.0
    print("\n--- DIAGNOSIS ---", flush=True)
    if spontaneous:
        print("SPONTANEOUS LATCHING: bridges reach high with ZERO input -> no stable blank state -> "
              "memory deadlock is FUNDAMENTAL (confirms close).", flush=True)
    else:
        print("INPUT-DEPENDENT: zero input leaves bridges blank -> control latching was STIM-COUPLED "
              "-> a fixable isolation route -> memory may be REOPENABLE.", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "G88"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"zero": zero, "stim": stim, "spontaneous": spontaneous}, indent=2, default=str))
    print("DONE", flush=True)
