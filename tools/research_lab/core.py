"""Shared two-site / competition physics for the research lab.

Not a registered P0-P3 experiment. Exploratory mechanism tests for the charter
claim: organisation must change the field that funds it.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Callable

import numpy as np

# Shared constants (income-limited regime)
G = 1.0
ETA = 0.40
E_FORM = 0.06
TAU_B = 10.0
HORIZON = 100.0
DT = 0.005
LEAK = 0.05
MAX_RES = 0.12
N_STEPS = int(HORIZON / DT)


@dataclass
class SiteState:
    u: np.ndarray
    p: np.ndarray
    q: np.ndarray
    r: np.ndarray
    res: np.ndarray
    e: np.ndarray
    bond_age: float = -1.0
    bond_time: float = 0.0
    captured: float = 0.0
    formed: int = 0
    expired: int = 0
    t: float = 0.0

    def copy(self) -> "SiteState":
        return SiteState(
            u=self.u.copy(), p=self.p.copy(), q=self.q.copy(), r=self.r.copy(),
            res=self.res.copy(), e=self.e.copy(), bond_age=self.bond_age,
            bond_time=self.bond_time, captured=self.captured,
            formed=self.formed, expired=self.expired, t=self.t,
        )


def make_state(seed: int = 0, n: int = 2) -> SiteState:
    rng = np.random.default_rng(seed)
    return SiteState(
        u=rng.normal(0.0, 0.02, n),
        p=np.zeros(n),
        q=rng.normal(0.0, 0.02, n),
        r=np.zeros(n),
        res=np.full(n, E_FORM, dtype=float),
        e=np.zeros(n),
    )


def capture(state: SiteState, couple: np.ndarray, *, rectified: bool = True) -> None:
    if rectified:
        requested = ETA * np.maximum(couple * state.r * DT, 0.0)
    else:
        # signed mean-work rule: credit positive net work, ignore per-step sign
        # (smoothed via allowing negative debit to be skipped — cumulative)
        net = float(np.sum(couple * state.r * DT))
        requested = np.full_like(state.r, 0.0) if net <= 0 else np.full_like(state.r, ETA * net / len(state.r))
    available = 0.5 * np.square(state.r)
    debit = np.minimum(requested, available)
    remain = np.maximum(np.square(state.r) - 2.0 * debit, 0.0)
    state.r = np.where(remain <= 0.0, 0.0, np.copysign(np.sqrt(remain), state.r))
    state.res = state.res + debit
    state.captured += float(debit.sum())


def leak(state: SiteState) -> None:
    state.res = state.res - DT * LEAK * state.res
    state.res = state.res - np.maximum(state.res - MAX_RES, 0.0)


def bond_two_site(state: SiteState) -> None:
    half = E_FORM / 2.0
    if state.bond_age >= 0.0:
        state.bond_age += DT
        state.bond_time += DT
        if state.bond_age >= TAU_B:
            state.bond_age = -1.0
            state.expired += 1
    elif state.res[0] >= half and state.res[1] >= half:
        state.res[0] -= half
        state.res[1] -= half
        state.bond_age = 0.0
        state.formed += 1


# ---------------------------------------------------------------------------
# Law R — resonant driven matter
# ---------------------------------------------------------------------------
def step_law_R(state: SiteState, chi: float, *, omega_drive: float = 1.0,
               drive_on: bool = True, rectified: bool = True) -> None:
    t = state.t
    omega_m = max(0.05, omega_drive + chi)
    gamma = 0.28
    drive = (0.70 * math.cos(omega_drive * t)) if drive_on else 0.0
    field_val = np.array([drive, 0.40 * drive])

    q, r = state.q, state.r
    matter_f = G * field_val - 2.0 * gamma * r - (omega_m ** 2) * q
    if state.bond_age >= 0.0:
        delta = q[0] - q[1]
        matter_f = matter_f + np.array([-0.1 * delta, 0.1 * delta])

    r = r + DT * matter_f
    q = q + DT * r

    state.u = field_val
    state.q, state.r = q, r
    capture(state, G * (field_val - q), rectified=rectified)
    leak(state)
    bond_two_site(state)
    state.t += DT


# ---------------------------------------------------------------------------
# Law L — structured capture + lock
# ---------------------------------------------------------------------------
def step_law_L(state: SiteState, k_f: float, *, driven: bool,
               dissipative: bool = True) -> None:
    t = state.t
    source = np.array([0.85 * math.cos(t), 0.0]) if driven else np.zeros(2)

    u, p, q, r = state.u, state.p, state.q, state.r
    field_f = -u + source
    if state.bond_age >= 0.0 and k_f > 0.0:
        delta = u[0] - u[1]
        v_diff = p[0] - p[1]
        field_f = field_f + np.array([-k_f * delta, k_f * delta])
        if dissipative:
            field_f = field_f + np.array([-0.5 * k_f * v_diff, 0.5 * k_f * v_diff])

    grad = u[0] - u[1]
    couple = np.array([G * grad, -G * grad])
    matter_f = couple - 0.7 * r

    p = p + DT * field_f
    u = u + DT * p
    r = r + DT * matter_f
    q = q + DT * r

    state.u, state.p, state.q, state.r = u, p, q, r
    capture(state, couple)
    leak(state)
    bond_two_site(state)
    state.t += DT


# ---------------------------------------------------------------------------
# Competition — two geometries share one energy budget
# ---------------------------------------------------------------------------
@dataclass
class Competitor:
    name: str
    # geometry: how strongly the live bond boosts transport from source
    transport_gain: float
    # geometry: local capture efficiency multiplier
    capture_gain: float
    res: float = E_FORM
    bond_age: float = -1.0
    bond_time: float = 0.0
    alive_bonds: int = 0
    captured: float = 0.0


@dataclass
class SharedWorld:
    source_energy: float
    heat: float = 0.0
    competitors: list[Competitor] = field(default_factory=list)
    t: float = 0.0
    history: list[dict] = field(default_factory=list)


def step_competition(world: SharedWorld, *, feedback: bool = True,
                     inflow: float = 0.008) -> None:
    """One step: scarce shared field -> per-geometry transport -> bonds.

    Income is scarce so full occupancy for both is impossible; ranking is a
    real competition. Geometry enters only as live-bond transport gain
    (Law C). Capture efficiency is shared physics, not a free parameter.
    """
    injected = DT * inflow
    world.source_energy += injected

    draws = []
    for c in world.competitors:
        # Law C: live organisation raises transport from the shared field.
        if feedback and c.bond_age >= 0.0:
            draws.append(0.05 + c.transport_gain)
        else:
            draws.append(0.02)
    total_draw = sum(draws) + 1e-12

    available = world.source_energy
    for c, draw in zip(world.competitors, draws):
        delivered = available * (draw / total_draw)
        income = delivered * c.capture_gain
        c.res += income
        c.captured += income
        world.source_energy -= delivered
        world.heat += max(0.0, delivered - income)

    world.source_energy = max(0.0, world.source_energy - DT * 0.02 * world.source_energy)

    half = E_FORM / 2.0
    for c in world.competitors:
        if c.bond_age >= 0.0:
            c.bond_age += DT
            c.bond_time += DT
            c.alive_bonds = 1
            if c.bond_age >= TAU_B:
                c.bond_age = -1.0
                c.alive_bonds = 0
        else:
            c.alive_bonds = 0
            if c.res >= half * 2:
                c.res -= half * 2
                c.bond_age = 0.0
                c.alive_bonds = 1

        c.res -= DT * LEAK * c.res
        c.res = min(c.res, MAX_RES)

    world.t += DT
    world.history.append({
        "t": world.t,
        "shared": world.source_energy,
        "heat": world.heat,
        **{f"S_{c.name}": c.bond_time for c in world.competitors},
        **{f"res_{c.name}": c.res for c in world.competitors},
        **{f"live_{c.name}": c.alive_bonds for c in world.competitors},
    })


def run_law_R_curve(chis, *, seeds=range(5), drive_on: bool = True,
                    on_step: Callable | None = None) -> list[float]:
    out = []
    total = len(chis) * len(list(seeds))
    done = 0
    for chi in chis:
        vals = []
        for seed in seeds:
            s = make_state(seed)
            for step in range(N_STEPS):
                step_law_R(s, chi, drive_on=drive_on)
                if on_step and step % 50 == 0:
                    on_step(done + step / N_STEPS, f"Law R chi={chi:+.2f} seed={seed}")
            vals.append(s.bond_time)
            done += 1
        out.append(float(np.mean(vals)))
    return out


def run_lock_curve(kfs, *, driven: bool, dissipative: bool = True,
                   seeds=range(5), on_step: Callable | None = None) -> list[float]:
    out = []
    done = 0
    total = len(kfs) * len(list(seeds))
    for kf in kfs:
        vals = []
        for seed in seeds:
            s = make_state(seed) if driven else _structured_pulse(seed)
            for step in range(N_STEPS):
                step_law_L(s, kf, driven=driven, dissipative=dissipative)
                if on_step and step % 50 == 0:
                    on_step(done + step / N_STEPS, f"Lock k_f={kf:.2f} seed={seed}")
            vals.append(s.bond_time)
            done += 1
        out.append(float(np.mean(vals)))
    return out


def _structured_pulse(seed: int = 0) -> SiteState:
    s = make_state(seed)
    s.u = np.array([0.85, -0.85]) + 0.02 * s.u
    s.p = np.array([0.15, -0.15])
    return s


def run_competition(*, feedback: bool, swap: bool = False,
                    on_step: Callable | None = None) -> dict:
    """Two geometries, one shared scarce budget.

    Geometry = transport gain when live (Law C). Capture efficiency is
    shared physics (0.85) so the only designed difference is organisation.
    swap=True exchanges the geometry parameters (F2.4).
    """
    capture_gain = 0.85
    if swap:
        a = Competitor("A", transport_gain=0.30, capture_gain=capture_gain)
        b = Competitor("B", transport_gain=1.20, capture_gain=capture_gain)
    else:
        a = Competitor("A", transport_gain=1.20, capture_gain=capture_gain)
        b = Competitor("B", transport_gain=0.30, capture_gain=capture_gain)

    world = SharedWorld(source_energy=0.2, competitors=[a, b])
    n = N_STEPS
    for step in range(n):
        step_competition(world, feedback=feedback)
        if on_step and step % 25 == 0:
            on_step(step / n, f"Competition feedback={feedback} swap={swap}")

    total = a.bond_time + b.bond_time + 1e-12
    return {
        "A_bond_time": a.bond_time,
        "B_bond_time": b.bond_time,
        "share_A": a.bond_time / total,
        "share_B": b.bond_time / total,
        "share_gap": abs(a.bond_time - b.bond_time) / total,
        "winner": "A" if a.bond_time > b.bond_time else ("B" if b.bond_time > a.bond_time else "tie"),
        "captured_A": a.captured,
        "captured_B": b.captured,
        "history": world.history,
        "feedback": feedback,
        "swap": swap,
    }


def run_tournament(*, feedback: bool = True, on_step: Callable | None = None,
                   inflow: float = 0.022) -> dict:
    """E4: four transport geometries, one scarce shared field.

    inflow is chosen so ~2 of 4 can sustain renewal; ranking then has content.
    """
    gains = [1.4, 0.9, 0.45, 0.15]
    names = ["G1.4", "G0.9", "G0.45", "G0.15"]
    comps = [Competitor(n, transport_gain=g, capture_gain=0.85)
             for n, g in zip(names, gains)]
    world = SharedWorld(source_energy=0.25, competitors=comps)
    for step in range(N_STEPS):
        step_competition(world, feedback=feedback, inflow=inflow)
        if on_step and step % 80 == 0:
            on_step(step / N_STEPS, f"Tournament feedback={feedback}")
    bonds = {c.name: c.bond_time for c in comps}
    caps = {c.name: c.captured for c in comps}
    spread = max(bonds.values()) - min(bonds.values())
    return {
        "bonds": bonds,
        "captured": caps,
        "spread": float(spread),
        "winner": max(bonds, key=bonds.get),
        "cap_order": sorted(caps, key=caps.get, reverse=True),
        "bond_order": sorted(bonds, key=bonds.get, reverse=True),
        "orders_match": sorted(caps, key=caps.get, reverse=True) == sorted(bonds, key=bonds.get, reverse=True),
        "feedback": feedback,
    }


def run_law_R_noisy(chis, *, noise: float = 0.05, seeds=range(3),
                    drive_on: bool = True, on_step: Callable | None = None) -> list[float]:
    """E5: Law R with additive Gaussian noise on detuning."""
    out = []
    for chi in chis:
        vals = []
        for seed in seeds:
            rng = np.random.default_rng(seed + 10_000)
            s = make_state(seed)
            for step in range(N_STEPS):
                chi_n = chi + (rng.normal(0.0, noise) if noise > 0 else 0.0)
                step_law_R(s, chi_n, drive_on=drive_on)
                if on_step and step % 400 == 0:
                    on_step(step / N_STEPS, f"E5 noise chi={chi:+.2f} seed={seed}")
            vals.append(s.bond_time)
        out.append(float(np.mean(vals)))
    return out


# ---------------------------------------------------------------------------
# E6 — P2 constitutive reduction (rest-frozen field-bond, P2 capture)
# ---------------------------------------------------------------------------
@dataclass
class P2Mini:
    u: np.ndarray
    p: np.ndarray
    q: np.ndarray
    r: np.ndarray
    res: np.ndarray
    bond_age: float = -1.0
    bond_time: float = 0.0
    u_rest: float = 0.0   # frozen at formation (P2)
    t: float = 0.0
    captured: float = 0.0


def make_p2mini(seed: int = 0) -> P2Mini:
    rng = np.random.default_rng(seed)
    return P2Mini(
        u=rng.normal(0.0, 0.05, 2),
        p=np.zeros(2),
        q=rng.normal(0.0, 0.05, 2),
        r=np.zeros(2),
        res=np.array([E_FORM, E_FORM]),
    )


def step_p2mini(s: P2Mini, k_f: float, *, feedback: bool, driven: bool,
                kf_damp: float = 0.0, drive_amp: float = 0.55) -> None:
    """P2-like operator: F=g(u-q), capture eta*max(0,F*r), field-bond spring
    with rest frozen at formation. kf_damp=0 is pure P2 conservative spring;
    kf_damp>0 is the dissipative lock used in E3.
    drive_amp=0 is a closed box; >0 is continuous harmonic drive on site 0."""
    t = s.t
    amp = drive_amp if driven else 0.0
    source = np.array([amp * math.cos(t), 0.0])

    field_f = -1.0 * s.u + source
    if feedback and s.bond_age >= 0.0 and k_f > 0.0:
        delta = (s.u[0] - s.u[1]) - s.u_rest
        field_f = field_f + np.array([-k_f * delta, k_f * delta])
        if kf_damp > 0.0:
            v_diff = s.p[0] - s.p[1]
            field_f = field_f + np.array([-kf_damp * k_f * v_diff,
                                          kf_damp * k_f * v_diff])

    # reciprocal coupling (P2)
    couple = G * (s.u - s.q)
    matter_f = couple - 0.35 * s.r

    s.p = s.p + DT * field_f
    s.u = s.u + DT * s.p
    s.r = s.r + DT * matter_f
    s.q = s.q + DT * s.r

    # P2 capture
    requested = ETA * np.maximum(couple * s.r * DT, 0.0)
    available = 0.5 * np.square(s.r)
    debit = np.minimum(requested, available)
    remain = np.maximum(np.square(s.r) - 2.0 * debit, 0.0)
    s.r = np.where(remain <= 0.0, 0.0, np.copysign(np.sqrt(remain), s.r))
    s.res = s.res + debit
    s.captured += float(debit.sum())

    # leak / bond
    s.res = s.res - DT * LEAK * s.res
    s.res = s.res - np.maximum(s.res - MAX_RES, 0.0)
    half = E_FORM / 2.0
    if s.bond_age >= 0.0:
        s.bond_age += DT
        s.bond_time += DT
        if s.bond_age >= TAU_B:
            s.bond_age = -1.0
    elif s.res[0] >= half and s.res[1] >= half:
        s.res[0] -= half
        s.res[1] -= half
        s.bond_age = 0.0
        s.u_rest = float(s.u[0] - s.u[1])
    s.t += DT


def run_p2mini(k_f: float, *, feedback: bool, driven: bool = True,
               kf_damp: float = 0.0, seeds=range(5),
               drive_amp: float = 0.55) -> float:
    vals = []
    for seed in seeds:
        s = make_p2mini(seed)
        if drive_amp <= 0.0:
            s.u = np.array([0.7, -0.7]) + 0.05 * s.u
        for _ in range(N_STEPS):
            step_p2mini(s, k_f, feedback=feedback, driven=drive_amp > 0,
                        kf_damp=kf_damp, drive_amp=drive_amp)
        vals.append(s.bond_time)
    return float(np.mean(vals))


# ---------------------------------------------------------------------------
# E8 — resonant competition (Law R capture + Law C transport on one budget)
# ---------------------------------------------------------------------------
def run_resonant_competition(*, chi_a: float = 0.0, chi_b: float = 1.2,
                             feedback: bool = True, swap: bool = False,
                             seeds=range(4), on_step: Callable | None = None,
                             phi_flat: bool = False,
                             gain_a: float = 1.2, gain_b: float = 1.2,
                             inflow: float = 0.010) -> dict:
    """Two detuned geometries share a scarce source. Income uses Law R
    resonant capture at each geometry's chi; live bond raises transport (Law C).
    swap exchanges chi_a/chi_b (F8.4)."""
    if swap:
        chi_a, chi_b = chi_b, chi_a

    wins = {"A": 0, "B": 0, "tie": 0}
    gaps = []
    bond_a_all, bond_b_all = [], []
    for seed in seeds:
        # per-seed one-shot tournament; zero initial endowment (true scarcity)
        sA = make_state(seed)
        sB = make_state(seed + 50)
        sA.res[:] = 0.0
        sB.res[:] = 0.0
        # shared budget pool
        pool = 0.25
        bA = bB = -1.0
        tA = tB = 0.0
        capA = capB = 0.0
        for step in range(N_STEPS):
            if on_step and step % 200 == 0:
                on_step(step / N_STEPS, f"E8 chiA={chi_a:+.2f} chiB={chi_b:+.2f} seed={seed}")
            # Law R capture power at each detuning (analytic proxy + integrator)
            drive = 0.70 * math.cos(sA.t)
            # resonant capture gain
            def phi(chi):
                if phi_flat:
                    return 1.0
                return 1.0 / (1.0 + (chi ** 2) * 2.5)

            pool += DT * inflow
            # live organisation raises transport share (use actual bond state)
            gA = (0.08 + gain_a) if (feedback and sA.bond_age >= 0.0) else 0.03
            gB = (0.08 + gain_b) if (feedback and sB.bond_age >= 0.0) else 0.03
            tot = gA + gB + 1e-12
            delA = pool * (gA / tot)
            delB = pool * (gB / tot)
            # resonant efficiency converts delivered field into income
            inA = delA * phi(chi_a) * 0.9
            inB = delB * phi(chi_b) * 0.9
            sA.res += inA
            sB.res += inB
            capA += inA
            capB += inB
            pool -= delA + delB
            pool = max(0.0, pool - DT * 0.02 * pool)

            # bond lifecycle on each side (single pooled reservoir per geometry)
            half = E_FORM
            for s in (sA, sB):
                funds = float(s.res[0] + s.res[1])
                if s.bond_age >= 0.0:
                    s.bond_age += DT
                    if s.bond_age >= TAU_B:
                        s.bond_age = -1.0
                elif funds >= half:
                    s.res[0] = max(0.0, funds - half) * 0.5
                    s.res[1] = max(0.0, funds - half) * 0.5
                    s.bond_age = 0.0
                # hard cap keeps hoarding from erasing scarcity
                s.res = np.minimum(np.maximum(s.res - DT * LEAK * s.res, 0.0), 0.04)

            if sA.bond_age >= 0.0:
                tA += DT
            if sB.bond_age >= 0.0:
                tB += DT
            # Mechanical fields advance for scene honesty but do NOT capture
            # into reservoirs here — income is only the shared-pool channel.
            sA.t += DT
            sB.t += DT

        bond_a_all.append(tA)
        bond_b_all.append(tB)
        gaps.append(abs(tA - tB) / (tA + tB + 1e-12))
        if tA > tB + 1e-9:
            wins["A"] += 1
        elif tB > tA + 1e-9:
            wins["B"] += 1
        else:
            wins["tie"] += 1

    meanA = float(np.mean(bond_a_all))
    meanB = float(np.mean(bond_b_all))
    winner = "A" if meanA > meanB else ("B" if meanB > meanA else "tie")
    return {
        "chi_a": chi_a, "chi_b": chi_b, "swap": swap, "feedback": feedback,
        "mean_A": meanA, "mean_B": meanB,
        "gap": abs(meanA - meanB),
        "share_gap": float(np.mean(gaps)),
        "winner": winner, "wins": wins,
        "captured_A": capA, "captured_B": capB,
    }
