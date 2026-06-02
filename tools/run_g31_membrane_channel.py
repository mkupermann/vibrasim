"""G31 — selective permeability INTEGRATED into the engine, tested on the REAL emergent
G30 membrane.

Build the G30 rich substrate, let the ~110-atom shell form, derive its geometry
(centre, radius, f_mem) from the actual bridged lattice, then inject two bands of tracer
free vibrations (compatible + incompatible) launched inward from outside the shell.
Run with the channel OFF (control) and ON, measuring per band the fraction that achieve
>=1 inward crossing, plus whether the shell survives the channel.
"""
import json
from dataclasses import replace
from pathlib import Path
import numpy as np

from world.config import WorldConfig
from world.state import World
from world.physics import tick, _largest_bridged_component, _fit_sphere

N_TRACERS = 200
GAP = 4.0          # launch this far outside the shell
SPEED = 8.0
SETTLE = 250       # ticks to form the membrane (matches G30)
MEASURE = 120      # ticks with tracers in flight


def cfg(seed):
    # EXACTLY the G30 config (reproduces the ~110-atom shell). Do not change formation
    # params — the channel is added only in the measurement phase.
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


def _minimage_r(p, centre, box):
    d = p - centre
    d -= box * np.round(d / box)
    return np.linalg.norm(d, axis=1), d


def _sample_outside(centre, radius, box, n, rng):
    """Rejection-sample positions genuinely OUTSIDE the shell (min-image r in (R+1.5, R+6)).
    The emergent shell spans the periodic box, so 'outside' lives in the corner regions;
    naive radial placement would wrap to the inside. Return (pos, inward_velocity)."""
    pos = np.empty((0, 3)); vel = np.empty((0, 3))
    lo, hi = radius + 1.5, radius + 6.0
    while len(pos) < n:
        cand = rng.uniform(0.0, 1.0, size=(n * 4, 3)) * box
        r, d = _minimage_r(cand, centre, box)
        ok = (r > lo) & (r < hi)
        cand = cand[ok]; d = d[ok]; r = r[ok]
        if len(cand):
            n_hat = d / r[:, None]
            v = -n_hat * SPEED            # launch inward along the min-image radial
            pos = np.vstack([pos, cand]); vel = np.vstack([vel, v])
    return pos[:n], vel[:n]


def inject_tracers(w, centre, radius, f_mem, rng):
    """Place 2*N tracers genuinely outside the shell, moving inward. Returns (slots, band)."""
    box = np.asarray(w.config.box_size, dtype=np.float64)
    need = 2 * N_TRACERS
    free = np.where(~w.s_alive)[0]
    if len(free) < need:
        # Free up slots by killing the farthest-from-centre ambient free vibrations
        # (they are unbound; removing far-field ambient does not touch the membrane).
        alive_idx = np.where(w.s_alive)[0]
        r, _ = _minimage_r(w.s_pos[alive_idx], centre, box)
        order = alive_idx[np.argsort(-r)]
        kill = order[: (need - len(free))]
        w.s_alive[kill] = False
        free = np.where(~w.s_alive)[0]
    slots = free[:need]
    pos, vel = _sample_outside(centre, radius, box, need, rng)
    freqs = np.empty(need)
    freqs[:N_TRACERS] = f_mem * 1.05    # band 0 = compatible (ratio 0.05, inside [0.005,0.095])
    freqs[N_TRACERS:] = f_mem * 3.0     # band 1 = incompatible (ratio 2.0, far outside)
    band = np.concatenate([np.zeros(N_TRACERS, int), np.ones(N_TRACERS, int)])
    w.s_pos[slots] = pos
    w.s_vel[slots] = vel
    w.s_freq[slots] = freqs
    w.s_pol[slots] = rng.random(need) < 0.5
    w.s_alive[slots] = True
    return slots, band, centre


def run_arm(seed, channel_k):
    c = cfg(seed)
    w = World(c)
    for _ in range(SETTLE):
        tick(w, c.dt)
    geom = membrane_geom(w)
    if geom is None:
        return None
    centre, radius, f_mem, comp0 = geom
    rng = np.random.default_rng(1000 + seed)   # identical tracer launch across arms
    slots, band, centre = inject_tracers(w, centre, radius, f_mem, rng)

    # Measurement phase: freeze regeneration (lambda_gen=0) so tracer slots stay stable;
    # set the channel mode for this arm.
    w.config = replace(c, lambda_gen=0.0, membrane_channel_k=channel_k,
                       membrane_channel_recompute=20, membrane_channel_width=1.5)
    box = np.asarray(c.box_size, dtype=np.float64)
    ever_in = np.zeros(len(slots), dtype=bool)
    for _ in range(MEASURE):
        tick(w, c.dt)
        alive = w.s_alive[slots]
        d = w.s_pos[slots] - centre
        d -= box * np.round(d / box)
        r = np.linalg.norm(d, axis=1)
        ever_in |= alive & (r < radius)
    comp_final = membrane_geom(w)
    final_size = comp_final[3] if comp_final else 0
    fc = float(ever_in[band == 0].mean())
    fi = float(ever_in[band == 1].mean())
    return dict(comp0=comp0, radius=float(radius), f_mem=f_mem,
                crossed_compatible=fc, crossed_incompatible=fi, final_size=final_size)


if __name__ == "__main__":
    print("=== G31: membrane channel in the engine, on the REAL emergent shell ===", flush=True)
    seeds = [42, 7]
    off, on = {}, {}
    for s in seeds:
        o = run_arm(s, 0.0)
        n = run_arm(s, 1.0)
        off[s], on[s] = o, n
        print(f"  seed {s} comp0={o['comp0']} R={o['radius']:.1f} f_mem={o['f_mem']:.3f}", flush=True)
        print(f"    OFF: comp={o['crossed_compatible']:.3f} incomp={o['crossed_incompatible']:.3f} final={o['final_size']}", flush=True)
        print(f"    ON : comp={n['crossed_compatible']:.3f} incomp={n['crossed_incompatible']:.3f} final={n['final_size']}", flush=True)

    off_c = np.mean([off[s]['crossed_compatible'] for s in seeds])
    off_i = np.mean([off[s]['crossed_incompatible'] for s in seeds])
    on_c = np.mean([on[s]['crossed_compatible'] for s in seeds])
    on_i = np.mean([on[s]['crossed_incompatible'] for s in seeds])

    G31a = (off_c > 0.5 and off_i > 0.5 and abs(off_c - off_i) < 0.20)
    G31b = on_i < 0.20
    G31c = on_c > 0.60
    G31d = (on_c - on_i) >= 0.40
    G31e = all(on[s]['final_size'] >= 0.6 * off[s]['final_size'] for s in seeds)
    passed = G31a and G31b and G31c and G31d and G31e
    print("\n--- VERDICT ---", flush=True)
    print(f"G31a control transparent       : {G31a} (c={off_c:.3f}, i={off_i:.3f})", flush=True)
    print(f"G31b blocks incompatible       : {G31b} ({on_i:.3f})", flush=True)
    print(f"G31c passes compatible         : {G31c} ({on_c:.3f})", flush=True)
    print(f"G31d selective on real shell   : {G31d} ({on_c-on_i:+.3f})", flush=True)
    print(f"G31e shell survives channel    : {G31e}", flush=True)
    verdict = ("PASS - selective permeability composes with the emergent membrane in the "
               "real engine and does not destabilise it") if passed else "NULL/partial"
    print(f"\nG31: {verdict}", flush=True)
    d = Path.home() / ".eqmod" / "bet" / "G31"; d.mkdir(parents=True, exist_ok=True)
    (d / "result.json").write_text(json.dumps(
        {"off_c": off_c, "off_i": off_i, "on_c": on_c, "on_i": on_i,
         "off": off, "on": on, "passed": passed}, indent=2, default=str))
    print("DONE", flush=True)
