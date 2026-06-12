"""G159 — does the topological (H0) partition functionally gate ACTIVITY?

Pre-registered in docs/amendments/G159_topological_isolation_probe.md (bars FROZEN 2026-06-12).
Charge travels ONLY along b_alive bonds (apply_bridge_charge_propagation, BET-105): a firing atom
deposits charge into its bonded neighbours. With no free vibrations and n_emit=0, the bond graph is
the ONLY A->B channel. The G158 H0 rule partitions that graph. Question: does keeping A and B as
separate components (M=2) block charge from reaching B, vs the connected control (M=1)?

HONEST SCOPE: tests the bond-mediated channel only (field channel off by construction); NOT a memory break.
NO LLM / transformer / pretrained.

Run: PYTHONPATH=. uv run --python 3.13 python tools/g159_topological_isolation.py
"""
from __future__ import annotations
import numpy as np
import world.bridges as wb
from world.config import WorldConfig
from world.state import World
from world.physics import tick

SEEDS = [42, 7, 13]
R2 = 14.0
A_CELLS = [10.0, 16.0, 22.0]
B_CELLS = [34.0, 40.0, 46.0]
BAND_Y = 30.0
DRIVE_CHARGE = 10.0
T_CONSOL = 10
T_DRIVE = 300
X_ISO = 0.10           # isolation threshold (frozen)
CTRL_MIN = 5           # control must produce >= this many B firings (frozen sanity)
EMPTY = np.empty(0, dtype=np.int32)


def cfg(seed):
    return WorldConfig(
        rng_seed=seed, box_size=(60.0, 60.0, 60.0),
        n_initial_vibrations=0, n_vibrations_max=64, n_nodes_max=64,
        lambda_gen=0.0, lambda_dec=0.0,
        atom_valence=4, atom_repulsion_k=0.0, repulsion_k=0.0, curvature_k=0.0,
        node_thermal_speed=0.0, anchor_damping=0.0,
        neuron_dynamics_enabled=True, theta_fire=4.0, n_emit=0,   # fire, but emit NO vibrations
        bridge_charge_prop_rate=2.0, bridge_prop_min_strength=0.0,
        compartment_boundary=0.0,                                  # partition is the rule, not a plane
        stdp_enabled=False, btsp_enabled=False,
        r_2=R2, graceful_capacity=True,
    )


def make_constrained_form_bridges(M, stats):
    def cfb(world):
        c = world.config
        valence = getattr(c, "atom_valence", 0)
        if valence <= 0:
            return 0
        K = world.k_count
        amask = world.k_alive[:K] & (world.k_level[:K] == 4)
        idx = np.where(amask)[0]
        if len(idx) < 2:
            return 0
        box = np.asarray(c.box_size, dtype=np.float64)
        r2sq = c.r_2 * c.r_2
        parent = {int(i): int(i) for i in idx}

        def find(a):
            while parent[a] != a:
                parent[a] = parent[parent[a]]; a = parent[a]
            return a

        def union(a, b):
            ra, rb = find(a), find(b)
            if ra != rb:
                parent[ra] = rb

        existing = set()
        for b in range(world.b_count):
            if world.b_alive[b]:
                i, j = int(world.b_atom_i[b]), int(world.b_atom_j[b])
                if i in parent and j in parent:
                    union(i, j)
                existing.add((min(i, j), max(i, j)))

        def ncomp():
            return len({find(int(i)) for i in idx})

        pos = world.k_pos[idx]
        ii, jj = np.triu_indices(len(idx), k=1)
        d = pos[ii] - pos[jj]
        d -= box * np.round(d / box)
        d2 = (d * d).sum(axis=1)
        order = np.where(d2 < r2sq)[0]
        order = order[np.argsort(d2[order])]
        formed = 0
        for cc in order:
            i = int(idx[ii[cc]]); j = int(idx[jj[cc]])
            key = (min(i, j), max(i, j))
            if key in existing:
                continue
            if world.k_bond_count[i] >= valence or world.k_bond_count[j] >= valence:
                continue
            same = find(i) == find(j)
            if (not same) and ncomp() <= M:
                stats["rejected"] += 1
                continue
            b = world.b_count
            if b >= world.b_alive.shape[0]:
                break
            world.b_alive[b] = True
            world.b_atom_i[b] = i
            world.b_atom_j[b] = j
            world.b_strength[b] = 1.0
            world.b_count += 1
            world.k_bond_count[i] += 1
            world.k_bond_count[j] += 1
            existing.add(key)
            if not same:
                union(i, j)
            formed += 1
        return formed
    return cfb


def n_components(world, idx):
    parent = {int(i): int(i) for i in idx}

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]; a = parent[a]
        return a
    for b in range(world.b_count):
        if world.b_alive[b]:
            i, j = int(world.b_atom_i[b]), int(world.b_atom_j[b])
            if i in parent and j in parent and find(i) != find(j):
                parent[find(i)] = find(j)
    return len({find(int(i)) for i in idx})


def bottleneck_alive(world, a_slots, b_slots):
    aset, bset = set(a_slots), set(b_slots)
    for b in range(world.b_count):
        if world.b_alive[b]:
            i, j = int(world.b_atom_i[b]), int(world.b_atom_j[b])
            if (i in aset and j in bset) or (i in bset and j in aset):
                return True, float(world.b_strength[b])
    return False, 0.0


def run(seed, M):
    stats = {"rejected": 0}
    wb.form_bridges = make_constrained_form_bridges(M, stats)
    c = cfg(seed)
    w = World(c)
    a_slots = [w.allocate_node(np.array([x, BAND_Y, 30.0]), 1.0, True, 4, EMPTY, 0) for x in A_CELLS]
    b_slots = [w.allocate_node(np.array([x, BAND_Y, 30.0]), 1.0, True, 4, EMPTY, 0) for x in B_CELLS]
    all_pos = {i: (w.k_pos[i][0], BAND_Y, 30.0) for i in a_slots + b_slots}

    for _ in range(T_CONSOL):                         # form the constrained partition (atoms pinned)
        for i, p in all_pos.items():
            w.k_pos[i] = p; w.k_vel[i] = 0.0
        tick(w, c.dt)
    idx = a_slots + b_slots
    comps = n_components(w, idx)
    bn_alive, bn_str = bottleneck_alive(w, a_slots, b_slots)

    a_fire = b_fire = 0
    b_peak = 0.0
    aset, bset = set(a_slots), set(b_slots)
    for _ in range(T_DRIVE):
        for i, p in all_pos.items():                  # pin all atoms
            w.k_pos[i] = p; w.k_vel[i] = 0.0
        for i in a_slots:                             # drive A above threshold
            w.k_charge[i] = DRIVE_CHARGE
        n_before = len(w.firing_events)
        tick(w, c.dt)
        for (tf, ai) in w.firing_events[n_before:]:   # firings appended THIS tick (t-robust)
            if ai in aset:
                a_fire += 1
            elif ai in bset:
                b_fire += 1
        b_peak = max(b_peak, float(max((w.k_charge[i] for i in b_slots), default=0.0)))

    return dict(comps=comps, a_fire=a_fire, b_fire=b_fire, b_peak=round(b_peak, 3),
                rejected=stats["rejected"], bottleneck=bn_alive, bn_str=bn_str, bonds=int(w.b_count))


def main():
    treat = [run(s, M=2) for s in SEEDS]
    ctrl = [run(s, M=1) for s in SEEDS]

    Bt = np.array([r["b_fire"] for r in treat], dtype=float)
    Bc = np.array([r["b_fire"] for r in ctrl], dtype=float)

    print("=" * 72)
    print("G159 — does the topological (H0) partition functionally gate activity?")
    print(f"A={A_CELLS} B={B_CELLS} r_2={R2} drive_charge={DRIVE_CHARGE} T_drive={T_DRIVE}; seeds {SEEDS}")
    print("  channel = bond-mediated charge (BET-105); field channel OFF (n_emit=0, no free vibrations)")
    print("-" * 72)
    print("TREATMENT M=2 (A,B separate components):")
    for s, r in zip(SEEDS, treat):
        print(f"  seed {s:>2}: B_fire={r['b_fire']:>4}  A_fire={r['a_fire']:>4}  comps={r['comps']} "
              f"bottleneck={r['bottleneck']} rejected={r['rejected']} bonds={r['bonds']} B_peak_charge={r['b_peak']}")
    print(f"  B_activity(M=2) = {Bt.mean():.2f} +/- {Bt.std():.2f}")
    print("CONTROL  M=1 (one component, bottleneck present):")
    for s, r in zip(SEEDS, ctrl):
        print(f"  seed {s:>2}: B_fire={r['b_fire']:>4}  A_fire={r['a_fire']:>4}  comps={r['comps']} "
              f"bottleneck={r['bottleneck']}(str={r['bn_str']}) bonds={r['bonds']} B_peak_charge={r['b_peak']}")
    print(f"  B_activity(M=1) = {Bc.mean():.2f} +/- {Bc.std():.2f}")
    print("-" * 72)

    I = (Bt.mean() / Bc.mean()) if Bc.mean() > 0 else float("inf")
    a_fired = all(r["a_fire"] > 0 for r in treat + ctrl)
    comps_ok = all(r["comps"] == 2 for r in treat) and all(r["comps"] == 1 for r in ctrl)
    ctrl_percolates = Bc.mean() >= CTRL_MIN
    print(f"isolation I = B(M=2)/B(M=1) = {I:.4f}   (threshold X = {X_ISO})")
    print(f"mechanism-fired: A fired both arms? {a_fired}   components held (M2=2,M1=1)? {comps_ok}   "
          f"control percolates (B(M1)>={CTRL_MIN})? {ctrl_percolates}")

    if not (a_fired and comps_ok):
        verdict = "INVALID — mechanism did not fire (A silent or components wrong)"
    elif not ctrl_percolates:
        verdict = (f"FAIL — control did not percolate (B(M=1)={Bc.mean():.1f} < {CTRL_MIN}); "
                   f"test insensitive, NOT a pass")
    elif I <= X_ISO:
        verdict = "PASS — emergent H0 partition functionally gates bond-mediated activity percolation"
    elif I <= 0.30:
        verdict = "PARTIAL — partition attenuates but does not fully block"
    else:
        verdict = ("NULL — charge crosses despite the partition => structural bottleneck NOT sufficient; "
                   "active gating required (pre-registered conclusion)")
    print(f"VERDICT (vs frozen bars): {verdict}")
    print("SCOPE: bond-mediated channel only (field channel off); NOT a memory-deadlock break.")
    print("=" * 72)


if __name__ == "__main__":
    main()
