"""G158 — topological (H0-persistence) bond-formation rule: emergent vs engineered modularity.

Pre-registered in docs/amendments/G158_topological_bond_rule.md (bars FROZEN 2026-06-12).
HONEST SCOPE: demonstrates that an H0 (connected-component) constraint on bond formation
self-organises a STABLE modular partition of the structural bond graph (partition chosen by
graph topology, not by a hand-placed plane as in G86) and functionally isolates modules in the
TENSION graph. Does NOT address the charge-field channel or the memory starve/erode deadlock.

Mechanism: monkeypatch world.bridges.form_bridges with a union-find-constrained version that
keeps >= M connected components. tick() re-imports the name at call time, so the patch applies.
NO LLM / transformer / pretrained.

Run: PYTHONPATH=. uv run --python 3.13 python tools/g158_topological_bond_rule.py
"""
from __future__ import annotations
import numpy as np
import world.bridges as wb
from world.config import WorldConfig
from world.state import World
from world.physics import tick

SEEDS = [42, 7, 13]
R2 = 14.0                 # r_eq = 7
A_CELLS = [10.0, 16.0, 22.0]      # cluster A
B_CELLS = [34.0, 40.0, 46.0]      # cluster B ; bottleneck candidate = 22<->34 (dist 12 < r_2)
BAND_Y = 30.0
DX = 4.0                  # displacement of cluster A at measurement start
T_CONSOL = 10             # ticks to let the constrained graph self-organise
T_RELAX = 300             # ticks of tension relaxation after perturbing A
EMPTY = np.empty(0, dtype=np.int32)


def cfg(seed):
    return WorldConfig(
        rng_seed=seed, box_size=(60.0, 60.0, 60.0),
        n_initial_vibrations=0, n_vibrations_max=64, n_nodes_max=64,
        lambda_gen=0.0, lambda_dec=0.0,
        atom_valence=4,                 # generous valence; the MODULE rule is the limiter
        atom_repulsion_k=0.0, repulsion_k=0.0, curvature_k=0.0,
        node_thermal_speed=0.0, anchor_damping=0.0,
        neuron_dynamics_enabled=False, stdp_enabled=False, btsp_enabled=False,
        r_2=R2, graceful_capacity=True,
    )


def make_constrained_form_bridges(M, stats):
    """Return a form_bridges(world)->int that keeps >= M connected components.
    `stats` dict is mutated with rejected-merge count.
    """
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
                parent[a] = parent[parent[a]]
                a = parent[a]
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
        cand = np.where(d2 < r2sq)[0]
        order = cand[np.argsort(d2[cand])]          # closest first

        formed = 0
        for c_ in order:
            i = int(idx[ii[c_]]); j = int(idx[jj[c_]])
            key = (min(i, j), max(i, j))
            if key in existing:
                continue
            if world.k_bond_count[i] >= valence or world.k_bond_count[j] >= valence:
                continue
            same = find(i) == find(j)
            if (not same) and ncomp() <= M:          # H0 rule: refuse the bottleneck merge
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


def n_components(world):
    K = world.k_count
    idx = [int(i) for i in np.where(world.k_alive[:K] & (world.k_level[:K] == 4))[0]]
    parent = {i: i for i in idx}

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]; a = parent[a]
        return a
    for b in range(world.b_count):
        if world.b_alive[b]:
            i, j = int(world.b_atom_i[b]), int(world.b_atom_j[b])
            if i in parent and j in parent and find(i) != find(j):
                parent[find(i)] = find(j)
    return len({find(i) for i in idx})


def lambda2(world):
    """Algebraic connectivity of the bond graph (0 if disconnected)."""
    K = world.k_count
    idx = [int(i) for i in np.where(world.k_alive[:K] & (world.k_level[:K] == 4))[0]]
    n = len(idx)
    if n < 2:
        return 0.0
    pos = {v: k for k, v in enumerate(idx)}
    L = np.zeros((n, n))
    for b in range(world.b_count):
        if world.b_alive[b]:
            i, j = int(world.b_atom_i[b]), int(world.b_atom_j[b])
            if i in pos and j in pos:
                a, c = pos[i], pos[j]
                L[a, c] -= 1; L[c, a] -= 1; L[a, a] += 1; L[c, c] += 1
    ev = np.sort(np.linalg.eigvalsh(L))
    return float(ev[1]) if n >= 2 else 0.0


def run(seed, M):
    stats = {"rejected": 0}
    wb.form_bridges = make_constrained_form_bridges(M, stats)   # patch (tick re-imports)
    c = cfg(seed)
    w = World(c)
    a_slots = [w.allocate_node(np.array([x, BAND_Y, 30.0]), 1.0, True, 4, EMPTY, 0) for x in A_CELLS]
    b_slots = [w.allocate_node(np.array([x, BAND_Y, 30.0]), 1.0, True, 4, EMPTY, 0) for x in B_CELLS]

    comps = []
    for _ in range(T_CONSOL):                 # self-organise the constrained graph
        tick(w, c.dt)
        comps.append(n_components(w))
    comp_after_consol = n_components(w)
    lam2 = lambda2(w)

    b_start = np.array([w.k_pos[i].copy() for i in b_slots])
    # perturb cluster A: displace it AWAY from B by DX, then HOLD it there (sustained
    # perturbation). Pinning is the sensitivity fix: an unpinned impulse just springs A
    # back and tests nothing; pinning asks whether the held displacement propagates to B
    # through the tension graph. Bars unchanged.
    a_target = {i: float(w.k_pos[i][0]) - DX for i in a_slots}
    for i in a_slots:
        w.k_pos[i] = (a_target[i], BAND_Y, 30.0)
        w.k_vel[i] = 0.0

    for _ in range(T_RELAX):
        for i in a_slots:                       # pin A at the displaced position
            w.k_pos[i] = (a_target[i], BAND_Y, 30.0)
            w.k_vel[i] = 0.0
        tick(w, c.dt)
        comps.append(n_components(w))

    b_end = np.array([w.k_pos[i].copy() for i in b_slots])
    b_disp = float(np.mean(np.linalg.norm(b_end - b_start, axis=1)))
    P = b_disp / DX
    comp_min, comp_max = min(comps), max(comps)
    return dict(P=round(P, 4), b_disp=round(b_disp, 4), comp_after_consol=comp_after_consol,
                comp_min=comp_min, comp_max=comp_max, rejected=stats["rejected"],
                lambda2=round(lam2, 4), bonds=int(w.b_count))


def main():
    treat = [run(s, M=2) for s in SEEDS]      # rule on: keep 2 modules
    ctrl = [run(s, M=1) for s in SEEDS]       # rule off: one component

    Pt = np.array([r["P"] for r in treat])
    Pc = np.array([r["P"] for r in ctrl])

    print("=" * 70)
    print("G158 — topological (H0) bond rule: emergent vs engineered modularity")
    print(f"A={A_CELLS} B={B_CELLS} r_2={R2} (r_eq={R2/2}) displace={DX} relax={T_RELAX}; seeds {SEEDS}")
    print("-" * 70)
    print("TREATMENT M=2 (keep 2 modules):")
    for s, r in zip(SEEDS, treat):
        print(f"  seed {s:>2}: P={r['P']:.4f}  comp(after consol)={r['comp_after_consol']} "
              f"comp[min,max]=[{r['comp_min']},{r['comp_max']}]  rejected_merges={r['rejected']} "
              f"lambda2={r['lambda2']}  bonds={r['bonds']}")
    print(f"  P(M=2) = {Pt.mean():.4f} +/- {Pt.std():.4f}")
    print("CONTROL  M=1 (one component, rule off):")
    for s, r in zip(SEEDS, ctrl):
        print(f"  seed {s:>2}: P={r['P']:.4f}  comp(after consol)={r['comp_after_consol']} "
              f"comp[min,max]=[{r['comp_min']},{r['comp_max']}]  lambda2={r['lambda2']}  bonds={r['bonds']}")
    print(f"  P(M=1) = {Pc.mean():.4f} +/- {Pc.std():.4f}")
    print("-" * 70)

    # mechanism-fired check (pattern 01)
    comps_held = all(r["comp_after_consol"] == 2 and r["comp_max"] == 2 for r in treat)
    rejected_fired = all(r["rejected"] >= 1 for r in treat)
    print(f"mechanism-fired: M=2 holds 2 components across all ticks? {comps_held}   "
          f"rule rejected >=1 bottleneck merge? {rejected_fired}")
    ctrl_merged = all(r["comp_max"] == 1 or r["comp_after_consol"] == 1 for r in ctrl)
    print(f"control collapsed to 1 component? {ctrl_merged}")

    # frozen bars
    if not (comps_held and rejected_fired):
        verdict = "NULL — partition not maintained / rule never fired (mechanism check failed)"
    elif Pc.mean() <= 0.10:
        verdict = "FAIL — control also isolates: partition is geometry, not the rule"
    elif Pt.mean() <= 0.10 and Pc.mean() >= 0.30:
        verdict = "PASS — emergent H0 partition holds and functionally isolates the tension graph"
    elif Pt.mean() <= 0.10 and 0.10 < Pc.mean() < 0.30:
        verdict = "PARTIAL — rule isolates, but the control channel percolates weakly (under-sensitive)"
    else:
        verdict = "NULL — rule fails to isolate (P(M=2) > 0.10)"
    print(f"VERDICT (vs frozen bars): {verdict}")
    print("SCOPE: structural/tension graph only — NOT the charge-field channel, NOT the memory deadlock.")
    print("=" * 70)


if __name__ == "__main__":
    main()
