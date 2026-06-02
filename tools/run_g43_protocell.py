"""G43 — proto-cell homeostasis. Does the G30+G32 selective membrane maintain a sustained
interior-exterior gradient (interior depleted of foreign/incompatible species) under
continuous ambient pressure, collapsing without the channel?

Pre-registered bars in docs/amendments/g43_protocell_homeostasis.md.
"""
import sys, json, math
from dataclasses import replace
from pathlib import Path
import numpy as np

from world.config import WorldConfig
from world.state import World
from world.physics import tick, _largest_bridged_component, _fit_sphere

SETTLE = 250
MEASURE = 200


def cfg(seed):
    return WorldConfig(
        n_initial_vibrations=300, box_size=(22.0, 22.0, 22.0),
        n_nodes_max=2000, n_vibrations_max=1800,
        graceful_capacity=True, numba_jit_enabled=False, repulsion_k=0.0,
        rng_seed=seed, lambda_gen=0.001, lambda_dec=0.001,
        freq_ratio=0.05, freq_tolerance=0.045, node_freq_binding=True,
        atom_valence=3, fusion_bond_block=2, curvature_k=2.0, atom_repulsion_k=1.0,
        pair_decay_time=12.0, triad_decay_time=80.0,
    )


def membrane_geom(w):
    comp = _largest_bridged_component(w)
    if len(comp) < 8:
        return None
    idx = np.array(comp)
    centre, radius = _fit_sphere(w.k_pos[idx])
    f_mem = float(w.k_freq[idx].mean())
    return centre, radius, f_mem, len(comp)


def incompat_concentration(w, centre, radius, f_mem, c_lo, c_hi, box):
    """Return (interior_conc, exterior_conc) of INCOMPATIBLE free vibrations (count/volume)."""
    alive = w.s_alive[: w.s_pos.shape[0]]
    if not alive.any():
        return 0.0, 0.0
    pos = w.s_pos[alive]
    freq = w.s_freq[alive]
    fmin = np.minimum(freq, f_mem)
    ratio = np.abs(freq - f_mem) / np.maximum(fmin, 1e-12)
    incompatible = ~((ratio >= c_lo) & (ratio <= c_hi))
    d = pos - centre
    d -= box * np.round(d / box)
    r = np.linalg.norm(d, axis=1)
    r_in = 0.6 * radius
    interior = r < r_in
    v_in = (4.0 / 3.0) * math.pi * r_in ** 3
    v_box = box[0] * box[1] * box[2]
    v_out = max(v_box - v_in, 1e-9)
    n_in_incompat = int((interior & incompatible).sum())
    n_out_incompat = int((~interior & incompatible).sum())
    return n_in_incompat / v_in, n_out_incompat / v_out


def run_arm(seed, channel):
    c = cfg(seed)
    w = World(c)
    for _ in range(SETTLE):
        tick(w, c.dt)
    geom = membrane_geom(w)
    if geom is None:
        return None
    centre, radius, f_mem, comp0 = geom
    c_lo = c.freq_ratio - c.freq_tolerance
    c_hi = c.freq_ratio + c.freq_tolerance
    if channel:
        w.config = replace(c, membrane_channel_k=1.0, membrane_channel_mode='atom',
                           membrane_channel_recompute=20)
    box = np.asarray(c.box_size, dtype=np.float64)
    ratios = []
    for t in range(MEASURE):
        tick(w, c.dt)
        if t % 10 == 9:
            ci, ce = incompat_concentration(w, centre, radius, f_mem, c_lo, c_hi, box)
            ratios.append(ci / ce if ce > 1e-12 else (9.9 if ci > 0 else 1.0))
    # last third of the run (steady state)
    last = ratios[-(len(ratios) // 3 or 1):]
    return dict(comp0=comp0, radius=float(radius), f_mem=f_mem,
                mean_ratio=float(np.mean(last)), frac_below=float(np.mean([x <= 0.6 for x in last])),
                all_ratios=ratios)


if __name__ == "__main__":
    print("=== G43: proto-cell homeostasis (selective membrane maintains interior gradient) ===", flush=True)
    seeds = [42, 7]
    on, off = {}, {}
    for s in seeds:
        on[s] = run_arm(s, channel=True)
        off[s] = run_arm(s, channel=False)
        print(f"  seed {s}: comp={on[s]['comp0']} R={on[s]['radius']:.1f} | "
              f"ON mean_ratio={on[s]['mean_ratio']:.2f} frac_below={on[s]['frac_below']:.2f} | "
              f"OFF mean_ratio={off[s]['mean_ratio']:.2f}", flush=True)

    G43a = all(on[s]['comp0'] >= 50 for s in seeds)
    G43b = all(on[s]['mean_ratio'] <= 0.5 for s in seeds)
    G43c = all(on[s]['frac_below'] >= 0.8 for s in seeds)
    G43d = all(off[s]['mean_ratio'] >= 0.8 for s in seeds)
    passed = G43a and G43b and G43c and G43d

    print("\n--- VERDICT ---", flush=True)
    print(f"G43a membrane forms (>=50)        : {G43a}", flush=True)
    print(f"G43b gradient (ON ratio<=0.5)     : {G43b}", flush=True)
    print(f"G43c sustained (>=80% below 0.6)  : {G43c}", flush=True)
    print(f"G43d control equilibrates (>=0.8) : {G43d}", flush=True)
    verdict = ("PASS - selective membrane maintains a sustained interior-exterior gradient "
               "(proto-cell homeostasis); collapses without the channel") if passed else "NULL/partial"
    print(f"\nG43: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "G43"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"on": on, "off": off, "passed": passed,
                                                  "G43a": G43a, "G43b": G43b, "G43c": G43c, "G43d": G43d},
                                                 indent=2, default=str))
    print("DONE", flush=True)
