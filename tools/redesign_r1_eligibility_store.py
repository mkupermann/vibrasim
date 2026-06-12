"""Redesign R1 — decouple the write/store variable from the propagation field.

Pre-registered in docs/redesign/amendments/R1_write_propagate_decouple.md (bars FROZEN 2026-06-12).
Tests whether the per-atom eligibility trace (k_eligibility: slow tau=6s, bumped +1 only on the
firing atom's own index, never propagates) can hold a SELECTIVE, PERSISTENT memory where the charge
field cannot — breaking deadlock D4 (write=leak). Emergence-preserving: reuses an existing primitive
(BTSP eligibility), no hand-built RAM. NO LLM / transformer / pretrained.

Run: PYTHONPATH=. uv run --python 3.13 python tools/redesign_r1_eligibility_store.py
"""
from __future__ import annotations
import numpy as np
from world.config import WorldConfig
from world.state import World
from world.physics import tick

SEEDS = [42, 7, 13]
BAND_Y = 30.0
A_CELLS = [10.0, 16.0, 22.0]
B_FAR = [40.0, 46.0, 52.0]     # contained arms (no field, no bonds -> gap irrelevant, kept far)
B_NEAR = [26.0, 32.0, 38.0]    # uncontained arm: close enough the field reaches
DRIVE = 10.0
T_WRITE = 60
T_RECALL = 120
EMPTY = np.empty(0, dtype=np.int32)


def cfg(seed, contained):
    return WorldConfig(
        rng_seed=seed, box_size=(80.0, 80.0, 80.0),
        n_initial_vibrations=0, n_vibrations_max=4096, n_nodes_max=64,
        lambda_gen=0.0, lambda_dec=0.0,                 # erosion OFF (isolate D4; D3 out of scope)
        atom_valence=(0 if contained else 4),           # contained: no bonds
        atom_repulsion_k=0.0, repulsion_k=0.0, curvature_k=0.0,
        node_thermal_speed=0.0, anchor_damping=0.0, r_1=0.1,
        neuron_dynamics_enabled=True, theta_fire=4.0,
        n_emit=(0 if contained else 8),                 # contained: no field emission
        r_integrate=5.0,
        btsp_enabled=True, btsp_tau_eligibility=6.0, btsp_potentiation=0.0,  # track eligibility; no potentiation side-effects
        bridge_charge_prop_rate=0.0, stdp_enabled=False,
        r_2=14.0, graceful_capacity=True,
    )


def build(w, b_cells):
    a = [w.allocate_node(np.array([x, BAND_Y, 30.0]), 1.0, True, 4, EMPTY, 0) for x in A_CELLS]
    b = [w.allocate_node(np.array([x, BAND_Y, 30.0]), 1.0, True, 4, EMPTY, 0) for x in b_cells]
    return a, b, {i: (w.k_pos[i][0], BAND_Y, 30.0) for i in a + b}


def mean_elig(w, slots):
    return float(np.mean([w.k_eligibility[i] for i in slots]))


def mean_charge(w, slots):
    return float(np.mean([w.k_charge[i] for i in slots]))


def run(seed, contained, drive_a=True, b_cells=None):
    if b_cells is None:
        b_cells = B_FAR if contained else B_NEAR
    c = cfg(seed, contained)
    w = World(c)
    a, b, pos = build(w, b_cells)
    aset, bset = set(a), set(b)
    a_fire = b_fire = 0

    # WRITE
    for _ in range(T_WRITE):
        for i, p in pos.items():
            w.k_pos[i] = p; w.k_vel[i] = 0.0
        if drive_a:
            for i in a:
                w.k_charge[i] = DRIVE
        n0 = len(w.firing_events)
        tick(w, c.dt)
        for (tf, ai) in w.firing_events[n0:]:
            if ai in aset:
                a_fire += 1
            elif ai in bset:
                b_fire += 1
    elig_a_peak = mean_elig(w, a)
    elig_b_peak = mean_elig(w, b)

    # RECALL (no drive)
    for _ in range(T_RECALL):
        for i, p in pos.items():
            w.k_pos[i] = p; w.k_vel[i] = 0.0
        n0 = len(w.firing_events)
        tick(w, c.dt)
        for (tf, ai) in w.firing_events[n0:]:
            if ai in aset:
                a_fire += 1
            elif ai in bset:
                b_fire += 1

    return dict(
        a_fire=a_fire, b_fire=b_fire,
        elig_a_peak=round(elig_a_peak, 4), elig_b_peak=round(elig_b_peak, 4),
        elig_a_end=round(mean_elig(w, a), 4), elig_b_end=round(mean_elig(w, b), 4),
        charge_a_end=round(mean_charge(w, a), 4),
    )


def main():
    arm1 = [run(s, contained=True, drive_a=True) for s in SEEDS]
    arm2 = [run(s, contained=True, drive_a=False) for s in SEEDS]                 # neg control
    arm3 = [run(s, contained=False, drive_a=True, b_cells=B_NEAR) for s in SEEDS]  # boundary (field on)

    def agg(arms, key):
        return np.array([r[key] for r in arms], float)

    ea_end = agg(arm1, "elig_a_end"); eb_end = agg(arm1, "elig_b_end")
    ea_peak = agg(arm1, "elig_a_peak")
    S = float(np.mean(eb_end / np.maximum(ea_end, 1e-9)))
    P = float(np.mean(ea_end / np.maximum(ea_peak, 1e-9)))
    ctrl_elig_a = agg(arm2, "elig_a_end").mean()
    b3a = agg(arm3, "elig_a_end"); b3b = agg(arm3, "elig_b_end")
    leak3 = float(np.mean(b3b / np.maximum(b3a, 1e-9)))

    print("=" * 74)
    print("Redesign R1 — eligibility-as-store (decouple write from propagation field)")
    print(f"  seeds {SEEDS}; T_write={T_WRITE} T_recall={T_RECALL} (~2s); erosion OFF (isolates D4)")
    print("-" * 74)
    print("ARM 1 contained (no bonds, no field):")
    for s, r in zip(SEEDS, arm1):
        print(f"  seed {s:>2}: A_fire={r['a_fire']:>4} B_fire={r['b_fire']:>3}  "
              f"elig_A {r['elig_a_peak']}->{r['elig_a_end']}  elig_B={r['elig_b_end']}  charge_A_end={r['charge_a_end']}")
    print(f"  Selectivity S = elig(B)/elig(A) = {S:.4f}   Persistence P = elig(A,end)/peak = {P:.4f}")
    print(f"  charge_A_end (mean) = {agg(arm1,'charge_a_end').mean():.4f}  (field is not a persistent store)")
    print(f"ARM 2 neg-control (no drive): elig(A,end) = {ctrl_elig_a:.4f}  (must <= 0.10)")
    print(f"ARM 3 boundary (field ON, B near): elig leak elig(B)/elig(A) = {leak3:.4f}  "
          f"B_fire={agg(arm3,'b_fire').mean():.0f}  (expected >0.30 -> needs containment)")
    print("-" * 74)

    mech = all(r["a_fire"] > 0 and r["b_fire"] == 0 for r in arm1)
    print(f"mechanism-fired (Arm1: A fires, B silent)? {mech}")
    if not mech:
        verdict = "INVALID — Arm 1 containment failed (A silent or B fired)"
    elif S <= 0.10 and P >= 0.50 and ctrl_elig_a <= 0.10:
        verdict = ("PASS — eligibility holds a SELECTIVE, PERSISTENT store decoupled from the propagation field; "
                   "D4 (write=leak) is breakable with an emergent local variable")
    elif S > 0.10:
        verdict = "NULL — store leaks even with firing contained (S>0.10); decoupling did not help"
    else:
        verdict = "NULL — store does not persist (P<0.50)"
    print(f"VERDICT (vs frozen bars): {verdict}")
    print("SCOPE: isolates D4 only. Erosion (D3) off; containment (D1/D2) needed (Arm 3). One of 3+ breaks.")
    print("=" * 74)


if __name__ == "__main__":
    main()
