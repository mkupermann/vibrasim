"""Redesign R3 — composition memory under ACTIVE recall (FINAL iteration).

Pre-registered in docs/redesign/amendments/R3_composition_final.md (bars + STOPPING RULE FROZEN 2026-06-12).
Fixes R2's two flaws (both harder, not easier): (1) containment measured ONLY vs B's own noise null (drop the
broken ||vB||/||vA|| clause); (2) module A is driven CONTINUOUSLY during the recall window = a genuine active
leak source (R2 left A quiet, so containment was never stressed). Store = emergent v_stored, written by an atom's
own firing AND spread along live bonds (propagation-permitted) -> A->B non-leak must EMERGE from C2 (H0 partition)
+ C3 (local flux-sink). NO LLM / transformer / pretrained.

STOPPING RULE: final iteration. NULL/inconclusive -> conclude the composition does not cleanly escape the deadlock.

Run: PYTHONPATH=. uv run --python 3.13 python tools/redesign_r3_composition.py
"""
from __future__ import annotations
import os
import numpy as np
import world.bridges as wb
import world.physics as wp
from world.config import WorldConfig
from world.state import World
from world.physics import tick

SEEDS = [int(x) for x in os.environ.get("R3_SEEDS", "42,7,13").split(",")]  # frozen default {42,7,13}; override for robustness audit
R2BOND = 14.0
BAND_Y = 30.0
A_CELLS = [10.0, 16.0, 22.0]
B_CELLS = [34.0, 40.0, 46.0]
DRIVE = 10.0
TAU_STORE = 10.0
W_SPREAD = 0.5
T_WRITE, T_ACTIVE = 40, 200
ABSORB_RADIUS = 10.0
LAMBDA_ABSORB = 30.0
EMPTY = np.empty(0, dtype=np.int32)
_orig_cull = wp.cull_excess_vibrations


def cfg(seed, M, n_emit):
    return WorldConfig(
        rng_seed=seed, box_size=(60.0, 60.0, 60.0),
        n_initial_vibrations=0, n_vibrations_max=4096, n_nodes_max=64,
        lambda_gen=0.0, lambda_dec=0.0,
        atom_valence=4, atom_repulsion_k=0.0, repulsion_k=0.0, curvature_k=0.0,
        node_thermal_speed=0.0, anchor_damping=0.0, r_1=0.1,
        neuron_dynamics_enabled=True, theta_fire=4.0, n_emit=n_emit, r_integrate=5.0,
        btsp_enabled=False, stdp_enabled=False, bridge_charge_prop_rate=0.0,
        r_2=R2BOND, graceful_capacity=True,
    )


def make_cfb(M):
    def cfb(world):
        c = world.config; val = getattr(c, "atom_valence", 0)
        if val <= 0:
            return 0
        K = world.k_count
        idx = np.where(world.k_alive[:K] & (world.k_level[:K] == 4))[0]
        if len(idx) < 2:
            return 0
        box = np.asarray(c.box_size); r2sq = c.r_2 ** 2
        parent = {int(i): int(i) for i in idx}
        def find(a):
            while parent[a] != a:
                parent[a] = parent[parent[a]]; a = parent[a]
            return a
        def union(a, b):
            ra, rb = find(a), find(b)
            if ra != rb:
                parent[ra] = rb
        ex = set()
        for b in range(world.b_count):
            if world.b_alive[b]:
                i, j = int(world.b_atom_i[b]), int(world.b_atom_j[b])
                if i in parent and j in parent:
                    union(i, j)
                ex.add((min(i, j), max(i, j)))
        def ncomp():
            return len({find(int(i)) for i in idx})
        pos = world.k_pos[idx]; ii, jj = np.triu_indices(len(idx), 1)
        d = pos[ii] - pos[jj]; d -= box * np.round(d / box); d2 = (d * d).sum(1)
        for cc in np.where(d2 < r2sq)[0][np.argsort(d2[d2 < r2sq])]:
            i, j = int(idx[ii[cc]]), int(idx[jj[cc]]); key = (min(i, j), max(i, j))
            if key in ex or world.k_bond_count[i] >= val or world.k_bond_count[j] >= val:
                continue
            if find(i) != find(j) and ncomp() <= M:
                continue
            b = world.b_count
            if b >= world.b_alive.shape[0]:
                break
            world.b_alive[b] = True; world.b_atom_i[b] = i; world.b_atom_j[b] = j
            world.b_strength[b] = 1.0; world.b_count += 1
            world.k_bond_count[i] += 1; world.k_bond_count[j] += 1
            ex.add(key)
            if find(i) != find(j):
                union(i, j)
        return 0
    return cfb


def make_cull(lambda_absorb, dt, stats):
    def cull(world):
        _orig_cull(world)
        if lambda_absorb <= 0:
            return
        c = world.config; K = world.k_count
        atoms = np.where(world.k_alive[:K] & (world.k_level[:K] == 4))[0]   # absorb near any alive atom
        N = world.n_alive
        if len(atoms) == 0 or N == 0:
            return
        sp = world.s_pos[:N]; box = np.asarray(c.box_size)
        near = np.zeros(N, dtype=bool)
        for ci in atoms:
            d = sp - world.k_pos[ci]; d -= box * np.round(d / box)
            near |= (d * d).sum(1) <= ABSORB_RADIUS ** 2
        kill = world.s_alive[:N] & near & (world.rng.random(N) < lambda_absorb * dt)
        world.s_alive[:N][kill] = False
        stats["absorbed"] += int(kill.sum())
    return cull


def bonds_of(world, i):
    out = []
    for b in range(world.b_count):
        if world.b_alive[b]:
            x, y = int(world.b_atom_i[b]), int(world.b_atom_j[b])
            if x == i:
                out.append((y, world.b_strength[b]))
            elif y == i:
                out.append((x, world.b_strength[b]))
    return out


def ncomp(world, idx):
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


def run_arm(seed, M, lambda_absorb, drive_a, n_emit, do_noise):
    stats = {"absorbed": 0}
    c = cfg(seed, M, n_emit)
    wb.form_bridges = make_cfb(M)
    wp.cull_excess_vibrations = make_cull(lambda_absorb, c.dt, stats)
    w = World(c)
    A = [w.allocate_node(np.array([x, BAND_Y, 30.0]), 1.0, True, 4, EMPTY, 0) for x in A_CELLS]
    B = [w.allocate_node(np.array([x, BAND_Y, 30.0]), 1.0, True, 4, EMPTY, 0) for x in B_CELLS]
    pos = {i: (w.k_pos[i][0], BAND_Y, 30.0) for i in A + B}
    v = np.zeros(w.k_count + 8)
    aset, bset = set(A), set(B)
    decay = float(np.exp(-c.dt / TAU_STORE))
    a_fire_active = b_fire = comp_min = 0
    comp_min = 99
    emitted = 0
    rngn = np.random.default_rng(900 + seed)

    def step(drive_atoms, count_active):
        nonlocal a_fire_active, b_fire, comp_min, emitted
        for i, p in pos.items():
            w.k_pos[i] = p; w.k_vel[i] = 0.0
        for i in drive_atoms:
            w.k_charge[i] = DRIVE
        n0 = len(w.firing_events)
        tick(w, c.dt)
        v[:] *= decay
        fired = [ai for (tf, ai) in w.firing_events[n0:]]
        for ai in fired:
            if ai < len(v):
                v[ai] += 1.0
                for (nb, st) in bonds_of(w, ai):
                    if nb < len(v):
                        v[nb] += W_SPREAD * st
            if count_active and ai in aset:
                a_fire_active += 1
            if ai in bset:
                b_fire += 1
        emitted += len(fired) * n_emit
        comp_min = min(comp_min, ncomp(w, A + B))

    # WRITE: establish pattern in A
    for _ in range(T_WRITE):
        step(A, count_active=False)
    peak = v[A].copy()
    # ACTIVE recall: A driven continuously (leak source) + B noise
    for _ in range(T_ACTIVE):
        drv = list(A) if drive_a else []
        if do_noise:
            drv = drv + list(rngn.choice(B, size=1))
        step(drv, count_active=True)

    vA, vB = v[A], v[B]
    cos = float(np.dot(vA, peak) / (np.linalg.norm(vA) * np.linalg.norm(peak) + 1e-12)) if np.linalg.norm(peak) > 0 else 0.0
    alive_free = int(w.s_alive[:w.n_alive].sum())
    eff = 1.0 - alive_free / max(1, emitted)
    return dict(cos=round(cos, 4), normB=round(float(np.linalg.norm(vB)), 4),
                a_fire_active=a_fire_active, b_fire=b_fire, comp_min=comp_min, eff=round(eff, 3))


def main():
    main_ = [run_arm(s, M=2, lambda_absorb=LAMBDA_ABSORB, drive_a=True, n_emit=8, do_noise=True) for s in SEEDS]
    n1 = [run_arm(s, M=1, lambda_absorb=LAMBDA_ABSORB, drive_a=True, n_emit=8, do_noise=True) for s in SEEDS]
    n3 = [run_arm(s, M=2, lambda_absorb=LAMBDA_ABSORB, drive_a=False, n_emit=8, do_noise=True) for s in SEEDS]

    def col(a, k):
        return np.array([r[k] for r in a], float)

    cosA = col(main_, "cos").mean()
    normB_main = col(main_, "normB").mean()
    n3B = col(n3, "normB"); n3_mean, n3_sd = float(n3B.mean()), float(n3B.std())
    null_bar = n3_mean + 2 * n3_sd
    normB_n1 = col(n1, "normB").mean()

    print("=" * 80)
    print("Redesign R3 — composition memory under ACTIVE recall (FINAL iteration)")
    print(f"  seeds {SEEDS}; field via emission (n_emit=8, lambda_gen=0); A DRIVEN through recall (leak source)")
    print(f"  phases W{T_WRITE}/Active{T_ACTIVE}; lambda_absorb={LAMBDA_ABSORB}")
    print("-" * 80)
    print(f"MAIN (C1+C2+C3, A active): cos(A,peak)={cosA:.3f}  normB={normB_main:.3f}  "
          f"A_fire_active={col(main_,'a_fire_active').mean():.0f}  B_fire={col(main_,'b_fire').mean():.0f}  "
          f"comp_min={col(main_,'comp_min').min():.0f}  sink_eff={col(main_,'eff').mean():.3f}")
    print(f"N3 (noise-only null): normB = {n3_mean:.3f} +/- {n3_sd:.3f}  -> M2 bar (mean+2SD) = {null_bar:.3f}")
    print(f"N1 (partition OFF):   normB = {normB_n1:.3f}  (expect > {null_bar:.3f} -> M2 fails, test sensitive)")
    print("-" * 80)

    M3a = col(main_, "comp_min").min() >= 2
    M3b = col(main_, "eff").mean() >= 0.90
    M3c = col(main_, "a_fire_active").mean() > 0
    M1 = cosA >= 0.70
    M2 = normB_main <= null_bar
    N1_fails = normB_n1 > null_bar

    print(f"M1 retention (cos>=0.70): {M1}  ({cosA:.3f})")
    print(f"M2 containment (normB <= mean_N3+2SD): {M2}  ({normB_main:.3f} vs {null_bar:.3f})")
    print(f"M3 mechanism: M3a(partition>=2)={M3a} M3b(sink>=0.90)={M3b} M3c(A active)={M3c}")
    print(f"N1 fails-as-expected (sensitive): {N1_fails}")

    if not (M3a and M3b and M3c):
        verdict = "INCONCLUSIVE/FAIL — mechanism didn't fire (per stopping rule: fix once, else treat as NULL)"
    elif M1 and M2 and N1_fails:
        verdict = "PASS — composition supports selective memory under ACTIVE leak source. Deadlock broken (toy task)."
    elif not M1:
        verdict = "NULL — A pattern not retained (M1). STOP: composition insufficient."
    elif not M2:
        verdict = ("NULL — A's active field leaks B above its own noise null (M2). STOP: composition does NOT "
                   "cleanly escape the deadlock; likely inherent to this substrate class.")
    else:
        verdict = "NULL — negative control did not fail (test insensitive). STOP."
    print(f"VERDICT (vs frozen bars; FINAL iteration): {verdict}")
    print("=" * 80)


if __name__ == "__main__":
    main()
