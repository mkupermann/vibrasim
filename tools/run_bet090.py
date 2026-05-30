"""BET-090: anchored selective memory. Same substrate as BET-089, but freeze
mature lattice sites so bridges keep place-identity. Two arms differ ONLY in
anchor_damping: ON (0.7) vs OFF (0.0, the negative control).

Pre-registered bars in docs/amendments/bet_090_anchored_memory.md.
"""
import sys, json, time
import numpy as np
from pathlib import Path
from world.config import WorldConfig
from world.state import World
from world.physics import tick


def make_cfg(anchor_damping: float) -> WorldConfig:
    return WorldConfig(
        n_initial_vibrations=400, box_size=(30.0, 30.0, 30.0),
        r_1=5.0, r_2=10.0, freq_tolerance=0.03,
        mol_fusion_enabled=False, resonance_coupling=15.0,
        node_thermal_speed=0.3, atom_valence=3,
        node_freq_binding=False, atom_repulsion_k=1.0, curvature_k=1.0,
        bistable_rate=1.0, bistable_low=1.0, bistable_mid=3.0, bistable_high=6.0,
        bistable_well_k=0.04, bistable_flux_gain=0.3, bistable_flux_ref=40.0,
        anchor_damping=anchor_damping, anchor_bond_min=2, anchor_age=50.0,
        pair_decay_time=40.0, triad_decay_time=400.0, dt=0.5,
        n_nodes_max=8192, n_vibrations_max=4096, vibration_soft_cap=500,
        repulsion_k=0.0, lambda_gen=0.006, lambda_dec=0.0,
        neuron_dynamics_enabled=False, stdp_enabled=False,
        slot_recycling_enabled=False, graceful_capacity=True, rng_seed=42,
    )


def inject(world, cfg, box, cx, n=20):
    rng = world.rng
    free = np.where(~world.s_alive[:cfg.n_vibrations_max])[0]
    k = min(n, len(free))
    if k == 0:
        return
    sl = free[:k]
    world.s_pos[sl] = np.column_stack([
        rng.normal(cx, 2.5, k) % box[0],
        rng.normal(box[1] / 2, 4, k) % box[1],
        rng.normal(box[2] / 2, 4, k) % box[2]])
    world.s_vel[sl] = rng.normal(0, 0.8, (k, 3))
    world.s_freq[sl] = world._sample_frequencies(k)
    world.s_pol[sl] = rng.random(k) < 0.5
    world.s_alive[sl] = True
    world.n_alive = max(world.n_alive, int(sl.max()) + 1)


def region_mean(world, cx, half=7.0):
    vals = []
    for b in range(world.b_count):
        if not world.b_alive[b]:
            continue
        i, j = int(world.b_atom_i[b]), int(world.b_atom_j[b])
        if i >= world.k_count or j >= world.k_count:
            continue
        mx = (world.k_pos[i][0] + world.k_pos[j][0]) / 2
        if abs(mx - cx) < half:
            vals.append(world.b_strength[b])
    return (float(np.mean(vals)), len(vals)) if vals else (0.0, 0)


def atom_snapshot(world):
    """Positions of alive level-4 atoms keyed by (stable) index."""
    snap = {}
    for a in range(world.k_count):
        if world.k_alive[a] and world.k_level[a] == 4:
            snap[a] = world.k_pos[a].copy()
    return snap


def mean_disp(snap_a, snap_b):
    """Mean displacement magnitude over atoms present in both snapshots."""
    common = set(snap_a) & set(snap_b)
    if not common:
        return None
    d = [float(np.linalg.norm(snap_b[a] - snap_a[a])) for a in common]
    return float(np.mean(d)), len(common)


def run_arm(name, anchor_damping, wall_budget=300):
    cfg = make_cfg(anchor_damping)
    world = World(cfg)
    dt = cfg.dt
    box = np.asarray(cfg.box_size)
    STIM_X, CTRL_X = box[0] * 0.25, box[0] * 0.75
    STIM_STEPS = 12000

    log = []
    snaps = {}  # sim_s -> atom_snapshot
    t0 = time.time()
    for step in range(40000):
        if step < STIM_STEPS and step % 4 == 0:
            inject(world, cfg, box, STIM_X, n=20)
        tick(world, dt)
        if step % 2000 == 1999:
            sim_s = round((step + 1) * dt, 1)
            sm, sn = region_mean(world, STIM_X)
            cm, cn = region_mean(world, CTRL_X)
            allv = np.array([world.b_strength[b] for b in range(world.b_count)
                             if world.b_alive[b]])
            ph = "STIM" if step < STIM_STEPS else "POST"
            frac_strong = float(np.mean(allv > cfg.bistable_mid)) if len(allv) else 0.0
            snaps[sim_s] = atom_snapshot(world)
            e = {"sim_s": sim_s, "phase": ph, "stim_mean": round(sm, 2),
                 "stim_n": sn, "ctrl_mean": round(cm, 2), "ctrl_n": cn,
                 "frac_strong": round(frac_strong, 2)}
            log.append(e)
            print(f"[{name}] {sim_s:.0f}s [{ph}]: stim={sm:.2f}(n={sn}) "
                  f"ctrl={cm:.2f}(n={cn}) frac_strong={frac_strong:.2f}", flush=True)
        if time.time() - t0 > wall_budget:
            print(f"[{name}] wall budget hit at step {step}", flush=True)
            break

    # T90a displacement: early window (first two checkpoints) vs late window
    # (last two checkpoints). Anchoring ON should shrink the late displacement.
    times = sorted(snaps)
    disp_early = mean_disp(snaps[times[0]], snaps[times[1]]) if len(times) >= 2 else None
    disp_late = mean_disp(snaps[times[-2]], snaps[times[-1]]) if len(times) >= 2 else None

    return {"name": name, "anchor_damping": anchor_damping, "log": log,
            "disp_early": disp_early, "disp_late": disp_late}


def verdict(res):
    """Evaluate pre-registered bars from an arm's log + displacement."""
    log = res["log"]
    post = [e for e in log if e["phase"] == "POST"]
    # last POST checkpoint at least 2000s after stim end (stim ends at 6000s)
    late_post = [e for e in post if e["sim_s"] >= 8000]
    stim_rows = [e for e in log if e["phase"] == "STIM"]

    out = {}
    de, dl = res["disp_early"], res["disp_late"]
    out["T90a_freeze"] = (de and dl and dl[0] < 0.25 * de[0]) or False
    out["disp_early"], out["disp_late"] = de, dl

    # T90b: selective during STIM (use the strongest stim checkpoint)
    out["T90b_stim_selective"] = any(
        e["stim_mean"] > 3.0 and e["ctrl_mean"] < 3.0 for e in stim_rows)
    # T90c: selective persists >=2000s post
    out["T90c_memory_selective"] = any(
        e["stim_mean"] > 3.0 and e["ctrl_mean"] < 3.0 for e in late_post)
    return out


if __name__ == "__main__":
    budget = int(sys.argv[1]) if len(sys.argv) > 1 else 300
    print("=== BET-090: anchored selective memory ===", flush=True)
    on = run_arm("ON ", anchor_damping=0.7, wall_budget=budget)
    off = run_arm("OFF", anchor_damping=0.0, wall_budget=budget)

    v_on, v_off = verdict(on), verdict(off)
    print("\n--- VERDICT ---", flush=True)
    print("ON (anchored): ", json.dumps(v_on, default=str), flush=True)
    print("OFF (control): ", json.dumps(v_off, default=str), flush=True)

    passed = (v_on["T90a_freeze"] and v_on["T90b_stim_selective"]
              and v_on["T90c_memory_selective"]
              and not v_off["T90c_memory_selective"])  # T90d: control must fail
    print(f"\nBET-090: {'PASS' if passed else 'NULL/FAIL'} "
          f"(T90d control-fails={not v_off['T90c_memory_selective']})", flush=True)

    outdir = Path.home() / '.eqmod' / 'bet' / 'BET-090'
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / 'result.json').write_text(json.dumps(
        {"on": on, "off": off, "verdict_on": v_on, "verdict_off": v_off,
         "passed": passed}, indent=2, default=str))
    print("DONE", flush=True)
