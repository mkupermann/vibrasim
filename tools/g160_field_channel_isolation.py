"""G160 — does the topological (H0) partition contain the FIELD channel too?

Pre-registered in docs/amendments/G160_field_channel_isolation.md (bars FROZEN 2026-06-12).
Field channel = neuron_dynamics integrating charge from EMITTED VIBRATIONS within r_integrate
(no bond involved). G159 proved that in M=2 the bond channel carries ZERO charge across the cut,
so any B firing with the field ON is unambiguously FIELD leakage. Question: does the topological
partition stop field-mediated spread? Prediction (per G86): NO — field is spatial, topology-independent.

Arms: A=leak (M=2, field on, gap 12); B=reachability sanity (M=2, field on, gap 4, must >=5);
C=topology-independence (bonds off, field on, gap 12, M=2 vs M=1 -> expect equal).
NO LLM / transformer / pretrained.

Run: PYTHONPATH=. uv run --python 3.13 python tools/g160_field_channel_isolation.py
"""
from __future__ import annotations
import numpy as np
import world.bridges as wb
from world.config import WorldConfig
from world.state import World
from world.physics import tick

SEEDS = [42, 7, 13]
R2 = 14.0
BAND_Y = 30.0
DRIVE_CHARGE = 10.0
T_CONSOL = 10
T_DRIVE = 300
EMPTY = np.empty(0, dtype=np.int32)


def cfg(seed, bonds_on=True):
    return WorldConfig(
        rng_seed=seed, box_size=(60.0, 60.0, 60.0),
        n_initial_vibrations=0, n_vibrations_max=4096, n_nodes_max=64,
        lambda_gen=0.0, lambda_dec=0.0,
        atom_valence=4, atom_repulsion_k=0.0, repulsion_k=0.0, curvature_k=0.0,
        node_thermal_speed=0.0, anchor_damping=0.0,
        r_1=0.1,                                  # ~no vibration->node binding (keep emitted vibrations free)
        neuron_dynamics_enabled=True, theta_fire=4.0,
        n_emit=8,                                 # FIELD ON: firing emits vibrations
        r_integrate=5.0,
        bridge_charge_prop_rate=(2.0 if bonds_on else 0.0),
        bridge_prop_min_strength=0.0,
        compartment_boundary=0.0,
        stdp_enabled=False, btsp_enabled=False,
        r_2=R2, graceful_capacity=True,
    )


def make_cfb(M, stats):
    def cfb(world):
        c = world.config
        valence = getattr(c, "atom_valence", 0)
        if valence <= 0:
            return 0
        K = world.k_count
        idx = np.where(world.k_alive[:K] & (world.k_level[:K] == 4))[0]
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
            world.b_atom_i[b] = i; world.b_atom_j[b] = j; world.b_strength[b] = 1.0
            world.b_count += 1
            world.k_bond_count[i] += 1; world.k_bond_count[j] += 1
            existing.add(key)
            if not same:
                union(i, j)
        return 0
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


def run(seed, M, gap, bonds_on=True):
    stats = {"rejected": 0}
    wb.form_bridges = make_cfb(M, stats)
    c = cfg(seed, bonds_on=bonds_on)
    w = World(c)
    a_cells = [10.0, 16.0, 22.0]
    b_cells = [22.0 + gap, 28.0 + gap, 34.0 + gap]
    a_slots = [w.allocate_node(np.array([x, BAND_Y, 30.0]), 1.0, True, 4, EMPTY, 0) for x in a_cells]
    b_slots = [w.allocate_node(np.array([x, BAND_Y, 30.0]), 1.0, True, 4, EMPTY, 0) for x in b_cells]
    all_pos = {i: (w.k_pos[i][0], BAND_Y, 30.0) for i in a_slots + b_slots}
    for _ in range(T_CONSOL):
        for i, p in all_pos.items():
            w.k_pos[i] = p; w.k_vel[i] = 0.0
        tick(w, c.dt)
    comps = n_components(w, a_slots + b_slots)

    aset, bset = set(a_slots), set(b_slots)
    a_fire = b_fire = 0
    b_peak = 0.0
    for _ in range(T_DRIVE):
        for i, p in all_pos.items():
            w.k_pos[i] = p; w.k_vel[i] = 0.0
        for i in a_slots:
            w.k_charge[i] = DRIVE_CHARGE
        n0 = len(w.firing_events)
        tick(w, c.dt)
        for (tf, ai) in w.firing_events[n0:]:
            if ai in aset:
                a_fire += 1
            elif ai in bset:
                b_fire += 1
        b_peak = max(b_peak, float(max((w.k_charge[i] for i in b_slots), default=0.0)))
    free_vibs = int(w.s_alive[:w.n_alive].sum()) if hasattr(w, "s_alive") else -1
    return dict(comps=comps, a_fire=a_fire, b_fire=b_fire, b_peak=round(b_peak, 2), free_vibs=free_vibs)


def main():
    A = [run(s, M=2, gap=12, bonds_on=True) for s in SEEDS]     # leak test
    B = [run(s, M=2, gap=4, bonds_on=True) for s in SEEDS]      # reachability sanity
    C2 = [run(s, M=2, gap=12, bonds_on=False) for s in SEEDS]   # topo-independence: bonds off, M=2
    C1 = [run(s, M=1, gap=12, bonds_on=False) for s in SEEDS]   # topo-independence: bonds off, M=1

    bA = np.array([r["b_fire"] for r in A], float)
    bB = np.array([r["b_fire"] for r in B], float)
    bC2 = np.array([r["b_fire"] for r in C2], float)
    bC1 = np.array([r["b_fire"] for r in C1], float)

    print("=" * 74)
    print("G160 — does the topological (H0) partition contain the FIELD channel?")
    print(f"  field ON (n_emit=8, r_integrate=5); seeds {SEEDS}; T_drive={T_DRIVE}")
    print("-" * 74)
    print(f"ARM A leak  (M=2, field on, gap=12): B_fire={bA.mean():.1f}+/-{bA.std():.1f}  "
          f"A_fire~{A[0]['a_fire']} comps={A[0]['comps']} B_peak={[r['b_peak'] for r in A]} free_vibs~{A[0]['free_vibs']}")
    print(f"ARM B sanity(M=2, field on, gap= 4): B_fire={bB.mean():.1f}+/-{bB.std():.1f}  "
          f"(field reachability; must >=5)")
    print(f"ARM C indep (bonds OFF, gap=12): B_fire(M=2)={bC2.mean():.1f}  B_fire(M=1)={bC1.mean():.1f}  "
          f"(expect equal -> field ignores topology)")
    print("-" * 74)

    a_fired = all(r["a_fire"] > 0 for r in A + B)
    comps_ok = all(r["comps"] == 2 for r in A + B)
    sanity = bB.mean() >= 5
    indep = abs(bC2.mean() - bC1.mean()) < 1e-9

    print(f"mechanism-fired: A fired? {a_fired}  M=2 comps held? {comps_ok}  "
          f"field-reachability sanity (B>=5)? {sanity}  topo-independence (C2==C1)? {indep}")

    if not (a_fired and comps_ok):
        verdict = "INVALID — mechanism did not fire"
    elif not sanity:
        verdict = f"FAIL-insensitive — field never crossed even at gap 4 (B={bB.mean():.1f} < 5)"
    elif bA.mean() > 1:
        verdict = ("NULL (predicted) — field LEAKS across the topological cut: H0 partition gates the BOND "
                   "channel only; field-mediated spread needs spatial separation (G86), not topology")
    else:
        verdict = ("'isolated-but-not-by-topology' — field spatially contained at gap 12 (required separation "
                   "< 12); NOT a topological effect (arm C shows field ignores M)")
    print(f"VERDICT (vs frozen bars): {verdict}")
    print("SCOPE: does not weaken G159 (different channel); completes the two-channel picture.")
    print("=" * 74)


if __name__ == "__main__":
    main()
