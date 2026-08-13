"""BP-C6 (G174) — structure-coupled break of linear strain invariance.

Pre-registered in docs/amendments/bp_c6_congruence_selectivity.md.
Metrics only; verdict against the frozen bars.

Stage 0 (band calibration, U only):
    python tools/run_bp_c6_invariance.py --stage 0
Stage 1 (measurement; bands are READ from the committed amendment file and
the amendment's commit SHA is logged into the verdict artifact):
    python tools/run_bp_c6_invariance.py --stage 1

Output: archive/run-logs/bp_c6/stage{0,1}.json + summary lines.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np

from world.config import WorldConfig
from world.state import World
from world.physics import tick

REPO = Path(__file__).resolve().parent.parent
AMENDMENT = REPO / "docs" / "amendments" / "bp_c6_congruence_selectivity.md"
OUT_DIR = REPO / "archive" / "run-logs" / "bp_c6"
EMPTY = np.empty(0, dtype=np.int32)

SEEDS_STAGE0 = [42, 7, 13]
SEEDS_STAGE1 = [101, 102, 103]
SHORT, LONG, UNIFORM = 6.5, 10.5, 8.5
K = 8.0
KP = K / 3.0          # derived: k_p = k*F*/(1-F*) at F* = 0.25
DAMPING = 0.95
T_PROBE = 800
T_SNAP = 100
T_CONSOL = 8
D_NORM = 4.0
X0 = 15.0
Y0 = 25.0
Z0 = 80.0
LANE_SEP = 20.0        # > bond window 12: cross-lane exclusion

PA_BITS = [0, 0, 1, 1, 0, 1]                 # [S,S,L,L,S,L]
PB_BITS = [1 - b for b in PA_BITS]           # complement


def spac(bits):
    return [LONG if b else SHORT for b in bits]


SP_PA, SP_PB = spac(PA_BITS), spac(PB_BITS)
SP_U = [UNIFORM] * 6
M_VEC = [a - b for a, b in zip(SP_PA, SP_PB)]        # ±4 pattern
Q4 = [UNIFORM - m for m in M_VEC]                    # 4.5 / 12.5
Q4P = [UNIFORM + m for m in M_VEC]

# symmetry walk guards (amendment §4) — hard assertions, not comments
assert list(reversed(SP_PA)) != SP_PB, "mirror degeneracy: reverse(PA)==PB"
assert list(reversed(SP_PB)) != SP_PA, "mirror degeneracy: reverse(PB)==PA"
assert list(reversed(Q4)) != Q4P, "mirror degeneracy: reverse(Q4)==Q4'"
assert abs(KP - K) > 1e-9, "endpoint collapse: k_p == k forbidden"

# cells: name -> (probed chain, target spacings)
CELLS = {
    "PA@QPB": ("PA", SP_PB),
    "PB@QPA": ("PB", SP_PA),
    "U@QPA":  ("U", SP_PA),
    "U@QPB":  ("U", SP_PB),
    "U@Q4":   ("U", Q4),
    "U@Q4p":  ("U", Q4P),
}
F_PRED = {"PA@QPB": 0.25, "PB@QPA": 0.25, "U@QPA": 0.625,
          "U@QPB": 0.625, "U@Q4": 0.25, "U@Q4p": 0.25}


def base_cfg(seed: int) -> WorldConfig:
    return WorldConfig(
        rng_seed=seed, box_size=(120.0, 80.0, 160.0),
        repulsion_cell_size=160.0,
        n_initial_vibrations=0, n_vibrations_max=64, n_nodes_max=64,
        lambda_gen=0.0, lambda_dec=0.0, atom_valence=2,
        atom_repulsion_k=0.0, repulsion_k=0.0, node_thermal_speed=0.0,
        anchor_damping=0.0, neuron_dynamics_enabled=False,
        stdp_enabled=False, btsp_enabled=False, r_2=12.0,
        graceful_capacity=True, per_bond_rest_enabled=True,
        bridge_tension_k=K, bridge_tension_damping=DAMPING,
    )


def chain_positions(spacings, x0=X0):
    L = sum(spacings)
    center = x0 + 6 * UNIFORM / 2
    xs = [center - L / 2]
    for s in spacings:
        xs.append(xs[-1] + s)
    return xs


def census_pairs(w):
    return {(min(int(w.b_atom_i[b]), int(w.b_atom_j[b])),
             max(int(w.b_atom_i[b]), int(w.b_atom_j[b])))
            for b in range(w.b_count) if w.b_alive[b]}


def consolidate(w, pin_map, ticks=T_CONSOL):
    for _ in range(ticks):
        for s, p in pin_map.items():
            w.k_pos[s] = p
            w.k_vel[s] = 0.0
        tick(w, w.config.dt)


def apply_probe(w, slots, targets, dt):
    """Positional gap springs toward targets (mirrors bond-force
    convention: k_vel += dir * k*(dist-target)*dt; no damping term —
    damping belongs to the bonds)."""
    for i in range(6):
        a, b = slots[i], slots[i + 1]
        d = w.k_pos[b] - w.k_pos[a]
        dist = float(np.sqrt((d * d).sum()))
        if dist < 1e-9:
            continue
        direction = d / dist
        f = KP * (dist - targets[i]) * dt
        w.k_vel[a] += direction * f
        w.k_vel[b] -= direction * f


def gaps_of(w, slots):
    return [float(np.sqrt(((w.k_pos[slots[i + 1]] - w.k_pos[slots[i]]) ** 2)
                          .sum())) for i in range(6)]


def run_cell(cell: str, seed: int, config: str) -> dict:
    """config in {'base', 'cb'}. cb = lane order reversed AND chain
    allocation order reversed AND per-chain carrier allocation reversed."""
    probed, targets = CELLS[cell]
    cfg = base_cfg(seed)
    w = World(cfg)

    chains = [("PA", SP_PA), ("PB", SP_PB), ("U", SP_U)]
    lanes = [Z0 - LANE_SEP, Z0, Z0 + LANE_SEP]
    if config == "cb":
        chains = list(reversed(chains))
        lanes = list(reversed(lanes))    # each chain keeps index -> lane
    # lane assignment: position in the (possibly reversed) list
    slot_map = {}
    pin_map = {}
    for (name, sp), z in zip(chains, lanes):
        xs = chain_positions(sp)
        order = range(7) if config == "base" else range(6, -1, -1)
        slots = [None] * 7
        for i in order:
            s = w.allocate_node(np.array([xs[i], Y0, z]), 1.0, True, 4,
                                EMPTY, 0)
            slots[i] = s
            pin_map[s] = (xs[i], Y0, z)
        consolidate(w, pin_map)
        slot_map[name] = (slots, xs, z)

    expected = set()
    for name in slot_map:
        slots, xs, z = slot_map[name]
        expected |= {(min(slots[i], slots[i + 1]), max(slots[i], slots[i + 1]))
                     for i in range(6)}
    write_valid = census_pairs(w) == expected

    # release: probe phase runs free (write channel closed by valence
    # saturation; verified by census after)
    for s in list(pin_map):
        w.k_vel[s] = 0.0

    slots, xs, z = slot_map[probed]
    f_traj = []
    max_gap = 0.0
    min_nonneighbor = float("inf")
    snap = {}
    for t in range(1, T_PROBE + 1):
        apply_probe(w, slots, targets, w.config.dt)
        tick(w, w.config.dt)
        g = gaps_of(w, slots)
        resid = float(np.mean([abs(gi - qi) for gi, qi in zip(g, targets)]))
        f_traj.append(1.0 - resid / D_NORM)
        max_gap = max(max_gap, max(g))
        # min non-neighbor distance within the probed chain
        pos = [w.k_pos[s] for s in slots]
        for i in range(7):
            for j in range(i + 2, 7):
                dd = float(np.sqrt(((pos[j] - pos[i]) ** 2).sum()))
                min_nonneighbor = min(min_nonneighbor, dd)
        if t == T_SNAP:
            snap["F_100"] = f_traj[-1]
            snap["resid_100"] = [abs(gi - qi) for gi, qi in zip(g, targets)]
    snap["F_800"] = f_traj[-1]
    g = gaps_of(w, slots)
    snap["resid_800"] = [abs(gi - qi) for gi, qi in zip(g, targets)]

    cross_valid = census_pairs(w) == expected
    return {
        "cell": cell, "seed": seed, "config": config,
        "F_100": snap["F_100"], "F_800": snap["F_800"],
        "resid_100": snap["resid_100"], "resid_800": snap["resid_800"],
        "f_traj_10": f_traj[::10],
        "write_valid": bool(write_valid), "census_valid": bool(cross_valid),
        "max_gap": max_gap, "window_flag": bool(max_gap >= 11.5),
        "min_nonneighbor": min_nonneighbor,
    }


def stage0() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = {"runs": []}
    plan = [("U@QPA", "base"), ("U@QPB", "base"),
            ("U@Q4", "base"), ("U@Q4p", "base"),
            ("U@Q4", "cb"), ("U@Q4p", "cb")]
    for seed in SEEDS_STAGE0:
        for cell, config in plan:
            r = run_cell(cell, seed, config)
            out["runs"].append(r)
            print(f"# S0 {cell}[{config}]@{seed}: F100={r['F_100']:.4f} "
                  f"F800={r['F_800']:.4f} wv={r['write_valid']} "
                  f"cv={r['census_valid']} maxgap={r['max_gap']:.2f}")
    bands = {}
    for t in ("F_100", "F_800"):
        deltas = []
        for config in ("base", "cb"):
            for pair in (("U@QPA", "U@QPB"), ("U@Q4", "U@Q4p")):
                for seed in SEEDS_STAGE0:
                    a = [r for r in out["runs"] if r["cell"] == pair[0]
                         and r["seed"] == seed and r["config"] == config]
                    b = [r for r in out["runs"] if r["cell"] == pair[1]
                         and r["seed"] == seed and r["config"] == config]
                    if a and b:
                        deltas.append(abs(a[0][t] - b[0][t]))
        points = [abs(r[t] - F_PRED[r["cell"]]) for r in out["runs"]]
        bands[f"band_sym^{t[2:]}"] = max(0.02, 3 * max(deltas))
        bands[f"band_point^{t[2:]}"] = max(0.02, 3 * max(points))
        stds = float(np.std(deltas))
        bands[f"reported_std_delta^{t[2:]}"] = stds
    out["bands"] = bands
    (OUT_DIR / "stage0.json").write_text(json.dumps(out, indent=1))
    print("# BANDS:", json.dumps(bands))
    print(f"# written -> {OUT_DIR / 'stage0.json'}")


def parse_bands_from_amendment() -> dict:
    text = AMENDMENT.read_text()
    m = re.search(r"FROZEN BANDS \(Stage 0, sealed\): band_sym\^100 = "
                  r"([0-9.]+), band_sym\^800 = ([0-9.]+), "
                  r"band_point\^100 = ([0-9.]+), band_point\^800 = "
                  r"([0-9.]+)", text)
    if not m:
        raise SystemExit("SEAL MISSING: frozen bands not found in amendment; "
                         "run stage 0, write bands, commit, then stage 1.")
    sha = subprocess.run(
        ["git", "log", "-n", "1", "--format=%H", "--", str(AMENDMENT)],
        capture_output=True, text=True, cwd=REPO).stdout.strip()
    # the seal only counts if the working copy equals the committed copy
    dirty = subprocess.run(
        ["git", "status", "--porcelain", "--", str(AMENDMENT)],
        capture_output=True, text=True, cwd=REPO).stdout.strip()
    if dirty:
        raise SystemExit("SEAL INVALID: amendment has uncommitted changes.")
    return {"band_sym^100": float(m.group(1)), "band_sym^800": float(m.group(2)),
            "band_point^100": float(m.group(3)),
            "band_point^800": float(m.group(4)), "seal_sha": sha}


def stage1() -> None:
    bands = parse_bands_from_amendment()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = {"bands": bands, "runs": []}
    plan = ([(c, cfgn) for c in ("PA@QPB", "PB@QPA", "U@Q4", "U@Q4p")
             for cfgn in ("base", "cb")]
            + [("U@QPA", "base"), ("U@QPB", "base")])
    for seed in SEEDS_STAGE1:
        for cell, config in plan:
            r = run_cell(cell, seed, config)
            out["runs"].append(r)
            print(f"# S1 {cell}[{config}]@{seed}: F100={r['F_100']:.4f} "
                  f"F800={r['F_800']:.4f} wv={r['write_valid']} "
                  f"cv={r['census_valid']} maxgap={r['max_gap']:.2f} "
                  f"minNN={r['min_nonneighbor']:.2f}")

    def get(cell, seed, config, t):
        for r in out["runs"]:
            if (r["cell"], r["seed"], r["config"]) == (cell, seed, config):
                return r[t]
        return None

    summary = {}
    for t in ("F_100", "F_800"):
        b = bands[f"band_sym^{t[2:]}"]
        dT = {cfgn: [get("PA@QPB", s, cfgn, t) - get("PB@QPA", s, cfgn, t)
                     for s in SEEDS_STAGE1] for cfgn in ("base", "cb")}
        dU4 = {cfgn: [abs(get("U@Q4", s, cfgn, t) - get("U@Q4p", s, cfgn, t))
                      for s in SEEDS_STAGE1] for cfgn in ("base", "cb")}
        dU2 = [abs(get("U@QPA", s, "base", t) - get("U@QPB", s, "base", t))
               for s in SEEDS_STAGE1]
        cb_t = {c: [abs(get(c, s, "base", t) - get(c, s, "cb", t))
                    for s in SEEDS_STAGE1] for c in ("PA@QPB", "PB@QPA")}
        summary[t] = {"band": b, "delta_T": dT, "delta_U4": dU4,
                      "delta_U2": dU2, "CB": cb_t}
    out["summary"] = summary
    (OUT_DIR / "stage1.json").write_text(json.dumps(out, indent=1))
    print("# SUMMARY:", json.dumps(summary))
    print(f"# seal SHA: {bands['seal_sha']}")
    print(f"# written -> {OUT_DIR / 'stage1.json'}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", type=int, required=True, choices=(0, 1))
    args = ap.parse_args()
    (stage0 if args.stage == 0 else stage1)()
