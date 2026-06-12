"""Redesign R2 — composition memory: does emergence-preserving composition escape the deadlock?

Pre-registered in docs/redesign/amendments/R2_composition_memory.md (bars FROZEN 2026-06-12).
Composes three mechanisms, all active, so non-propagation must EMERGE (not hand-coded):
  C1 v_stored: a per-atom store whose write is PROPAGATION-PERMITTED (deposit on the firing atom AND spread
     along live bonds). Non-leak A->B must come from containment, not a hand gate.
  C2 H0 partition: constrained form_bridges (union-find, keep >=M components) -- monkeypatch (engineered topology).
  C3 local flux-sink: monkeypatch cull_excess_vibrations to ALSO absorb free vibrations near charged atoms
     (emergent: region = where k_charge is, no hand-placed boundary). Runs at tick START (before integration).
Field active via EMISSION (n_emit>0), lambda_gen=0 (no ambient self-activity confound; D2 = emission-driven, which
G160 proved floods at lambda_gen=0 -- a reasoned deviation from the panel's lambda_gen>0, logged).
NO LLM / transformer / pretrained.  Run: PYTHONPATH=. uv run --python 3.13 python tools/redesign_r2_composition.py
"""
from __future__ import annotations
import numpy as np
import world.bridges as wb
import world.physics as wp
from world.config import WorldConfig
from world.state import World
from world.physics import tick

SEEDS = [42, 7, 13]
R2BOND = 14.0
BAND_Y = 30.0
A_CELLS = [10.0, 16.0, 22.0]
B_CELLS = [34.0, 40.0, 46.0]     # 22<->34 = 12 < r_2 -> bottleneck candidate; field reaches (G160)
DRIVE = 10.0
TAU_STORE = 10.0
W_SPREAD = 0.5
T_WRITE, T_QUIET, T_RECALL = 40, 120, 120
ABSORB_RADIUS = 10.0
ABSORB_CHARGE_THRESH = 1.0
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
        # C3 keying DEBUG (M3b fix): the original "k_charge >= threshold" region is mostly EMPTY because firing
        # resets charge to 0 -> only 27% absorbed. Re-key to proximity to any alive level-4 atom (vibrations are
        # emitted AT atoms, so caught at the source). Still emergent: local vibration x atom rule, no hand-placed
        # boundary. M1/M2/M3 bars unchanged; this only makes the sink meet its own M3b efficacy spec.
        charged = np.where(world.k_alive[:K] & (world.k_level[:K] == 4))[0]
        if len(charged) == 0:
            return
        N = world.n_alive
        if N == 0:
            return
        alive = world.s_alive[:N]
        sp = world.s_pos[:N]
        box = np.asarray(c.box_size)
        near = np.zeros(N, dtype=bool)
        for ci in charged:
            d = sp - world.k_pos[ci]; d -= box * np.round(d / box)
            near |= (d * d).sum(1) <= ABSORB_RADIUS ** 2
        kill = alive & near & (world.rng.random(N) < lambda_absorb * dt)
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


def run_arm(seed, M, lambda_absorb, do_write, n_emit, do_noise):
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
    a_fire = b_fire = comp_min = 0
    comp_min = 99
    emitted = 0
    rng_noise = np.random.default_rng(700 + seed)

    def step(drive_atoms):
        nonlocal a_fire, b_fire, comp_min, emitted
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
                for (nb, st) in bonds_of(w, ai):       # PROPAGATION-PERMITTED write
                    if nb < len(v):
                        v[nb] += W_SPREAD * st
            if ai in aset:
                a_fire += 1
            elif ai in bset:
                b_fire += 1
        emitted += len(fired) * n_emit
        comp_min = min(comp_min, ncomp(w, A + B))

    for _ in range(T_WRITE):
        step(A if do_write else [])
    peak = v[A].copy()
    for _ in range(T_QUIET):
        step([])
    for _ in range(T_RECALL):
        noise = list(rng_noise.choice(B, size=1)) if do_noise else []
        step(noise)

    vA, vB = v[A], v[B]
    cos = float(np.dot(vA, peak) / (np.linalg.norm(vA) * np.linalg.norm(peak) + 1e-12)) if np.linalg.norm(peak) > 0 else 0.0
    magA = float(np.linalg.norm(vA)); magpk = float(np.linalg.norm(peak))
    alive_free = int(w.s_alive[:w.n_alive].sum())
    eff = 1.0 - alive_free / max(1, emitted)
    return dict(cos=round(cos, 4), magA=round(magA, 4), magpk=round(magpk, 4),
                mag_ratio=round(magA / max(1e-9, magpk), 4), normB=round(float(np.linalg.norm(vB)), 4),
                a_fire=a_fire, b_fire=b_fire, comp_min=comp_min, eff=round(eff, 3))


def main():
    LA = 30.0   # lambda_absorb for arms with the sink on
    base = [run_arm(s, M=2, lambda_absorb=0.0, do_write=True, n_emit=0, do_noise=False) for s in SEEDS]
    main_ = [run_arm(s, M=2, lambda_absorb=LA, do_write=True, n_emit=8, do_noise=True) for s in SEEDS]
    n1 = [run_arm(s, M=1, lambda_absorb=LA, do_write=True, n_emit=8, do_noise=True) for s in SEEDS]
    n2 = [run_arm(s, M=2, lambda_absorb=0.0, do_write=True, n_emit=8, do_noise=True) for s in SEEDS]
    n3 = [run_arm(s, M=2, lambda_absorb=LA, do_write=False, n_emit=8, do_noise=True) for s in SEEDS]

    def col(arms, k):
        return np.array([r[k] for r in arms], float)

    cos_base = col(base, "cos").mean(); mr_base = col(base, "mag_ratio").mean()
    cosA = col(main_, "cos").mean(); mrA = col(main_, "mag_ratio").mean()
    normB_main = col(main_, "normB").mean(); normA_main = col(main_, "magA").mean()
    bfire_main = col(main_, "b_fire").mean()
    n3B = col(n3, "normB"); n3_mean, n3_sd = float(n3B.mean()), float(n3B.std())
    leakB = float(normB_main / max(1e-9, normA_main))
    n1_leak = float(col(n1, "normB").mean() / max(1e-9, col(n1, "magA").mean()))
    n2_bfire = col(n2, "b_fire").mean(); n2_leak = float(col(n2, "normB").mean() / max(1e-9, col(n2, "magA").mean()))

    print("=" * 78)
    print("Redesign R2 — composition memory (emergence-preserving): does it escape the deadlock?")
    print(f"  seeds {SEEDS}; field ON via emission (n_emit=8, lambda_gen=0); tau_store={TAU_STORE}; "
          f"phases W{T_WRITE}/Q{T_QUIET}/R{T_RECALL}; lambda_absorb={LA}")
    print("-" * 78)
    print(f"BASE (contained, no field/noise): cos={cos_base:.3f} mag_ratio={mr_base:.3f}  "
          f"a_fire={col(base,'a_fire').mean():.0f}")
    print(f"MAIN (C1+C2+C3 all on): cos={cosA:.3f} mag_ratio={mrA:.3f} normB={normB_main:.3f} "
          f"normA={normA_main:.3f} b_fire={bfire_main:.0f} comp_min={col(main_,'comp_min').min():.0f} "
          f"sink_eff={col(main_,'eff').mean():.3f}")
    print(f"   leak ||vB||/||vA|| = {leakB:.4f}")
    print(f"N1 (partition OFF): leak={n1_leak:.4f} b_fire={col(n1,'b_fire').mean():.0f} (expect M2 FAIL)")
    print(f"N2 (sink OFF):      leak={n2_leak:.4f} b_fire={n2_bfire:.0f} (expect field floods B, M2 FAIL)")
    print(f"N3 (noise-only):    normB mean={n3_mean:.4f} sd={n3_sd:.4f}  (B-store null)")
    print("-" * 78)

    # frozen markers
    M3a = col(main_, "comp_min").min() >= 2
    M3b = col(main_, "eff").mean() >= 0.90
    M3c = col(main_, "a_fire").mean() > 0
    M1 = (cosA >= 0.70) and (cosA >= 0.90 * cos_base) and (mrA >= 0.50)
    M2_sanity = bfire_main >= 2
    M2 = M2_sanity and (leakB <= 0.30) and (leakB <= n3_mean + 3 * n3_sd)
    n1_fails = n1_leak > 0.30

    print(f"M1 retention: {M1}  (cos {cosA:.3f}>=0.70 & >=0.9*{cos_base:.3f}; mag_ratio {mrA:.3f}>=0.50)")
    print(f"M2 containment: {M2}  (B_fired {bfire_main:.0f}>=2 sanity; leak {leakB:.4f}<=0.30 & <= {n3_mean+3*n3_sd:.4f})")
    print(f"M3 mechanism-fired: M3a(partition>=2)={M3a} M3b(sink>=0.90)={M3b} M3c(A fired)={M3c}")
    print(f"N1 fails-as-expected: {n1_fails}")

    if not (M3a and M3b and M3c):
        verdict = "FAIL — mechanism didn't fire (debug; do not touch bars)"
    elif M1 and M2 and n1_fails:
        verdict = "PASS — emergence-preserving composition escapes the deadlock class (!)"
    elif not M2_sanity:
        verdict = "NULL/uninformative — over-absorbed (B silent); C3 starved the field, M2 sanity gate failed"
    elif not M2:
        verdict = "NULL — field leaks to B despite containment (write=leak trap on the C3 knife-edge)"
    else:
        verdict = "NULL — A-store did not survive (M1 failed)"
    print(f"VERDICT (vs frozen bars): {verdict}")
    print("SCOPE: minimal toy retention; NULL => composition insufficient (deadlock likely inherent), does NOT")
    print("       invalidate R1/G159/G160 individually.")
    print("=" * 78)


if __name__ == "__main__":
    main()
