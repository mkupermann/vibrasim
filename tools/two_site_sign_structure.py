"""Minimal two-site integrator verifying Law L / C / R sign structure.

Exploratory verification of the analytical model. NOT a registered P0-P3
experiment and NOT scientific evidence for emergence.

Survival S = bond-time. Renewal requires capture income at BOTH sites.
The regime is tuned to sit near the renewal threshold so geometry effects
show up as sign changes in S(chi), not as saturation at the horizon.

  Law L (lock):  chi = k_f. Capture is from field STRUCTURE (difference
                 u0-u1). The lock (spring + difference damping) equalizes
                 that difference, so larger k_f destroys the structured
                 drive.  Expect dS/dk_f <= 0.

  Law C (conductance): chi = live-bond edge conductance from source site
                 to starved site. Without transport, site 1 cannot pay
                 half of E_FORM.  Expect dS/dchi > 0.

  Law R (resonant): chi = matter detuning. Driven damped oscillator
                 capture peaks at resonance.  Expect peak near chi=0.

Usage:
  python tools/two_site_sign_structure.py
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np

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
class State:
    u: np.ndarray
    p: np.ndarray
    q: np.ndarray
    r: np.ndarray
    res: np.ndarray
    e: np.ndarray = field(default_factory=lambda: np.zeros(2))  # Law C energy
    bond_age: float = -1.0
    bond_time: float = 0.0
    captured: float = 0.0
    formed: int = 0
    expired: int = 0
    t: float = 0.0


def make_state(seed: int = 0) -> State:
    rng = np.random.default_rng(seed)
    return State(
        u=rng.normal(0.0, 0.02, 2),
        p=np.zeros(2),
        q=rng.normal(0.0, 0.02, 2),
        r=np.zeros(2),
        res=np.array([E_FORM, E_FORM]),
    )


def make_state_L(seed: int = 0) -> State:
    """Closed-box Law L starts with a structured field pulse (nonzero grad)."""
    s = make_state(seed)
    s.u = np.array([0.85, -0.85]) + 0.02 * s.u
    s.p = np.array([0.15, -0.15])
    return s


def capture(state: State, couple: np.ndarray) -> None:
    requested = ETA * np.maximum(couple * state.r * DT, 0.0)
    available = 0.5 * np.square(state.r)
    debit = np.minimum(requested, available)
    remain = np.maximum(np.square(state.r) - 2.0 * debit, 0.0)
    state.r = np.where(remain <= 0.0, 0.0, np.copysign(np.sqrt(remain), state.r))
    state.res = state.res + debit
    state.captured += float(debit.sum())


def leak(state: State) -> None:
    state.res = state.res - DT * LEAK * state.res
    state.res = state.res - np.maximum(state.res - MAX_RES, 0.0)


def bond(state: State) -> None:
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


# ===========================================================================
# Law L
# Structured capture: matter/capture couple to the field DIFFERENCE
#   grad = u0 - u1.
# Lock: (a) spring toward zero difference, (b) difference-mode damping.
# Together they equalize u0,u1 as k_f grows, so structured capture dies.
# ===========================================================================
def step_L(state: State, k_f: float, *, driven: bool) -> None:
    t = state.t
    # Drive creates structure (push site 0 only).
    source = np.array([0.85 * math.cos(t), 0.0]) if driven else np.zeros(2)

    u, p, q, r = state.u, state.p, state.q, state.r

    field_f = -u + source
    if state.bond_age >= 0.0 and k_f > 0.0:
        delta = u[0] - u[1]
        v_diff = p[0] - p[1]
        # spring equalizes difference
        field_f = field_f + np.array([-k_f * delta, k_f * delta])
        # damping of the difference mode (the "lock" is dissipative enough
        # to kill variance instead of pumping the rectifier)
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
    bond(state)
    state.t += DT


# ===========================================================================
# Law C — energy pools at sites; absorption funds reservoirs; live bond
# raises conductance from site 0 (source) to site 1 (starved).
# ===========================================================================
def step_C(state: State, chi: float) -> None:
    e = state.e
    e[0] += DT * 0.22
    # Site 1 is starved: only a trickle without a live bond. The geometry
    # law is the live-bond conductance boost from site 0 to site 1.
    background = 0.002
    boost = chi if state.bond_age >= 0.0 else 0.0
    flow = DT * (background + boost) * (e[0] - e[1])
    e[0] -= flow
    e[1] += flow

    # Absorption funds reservoirs. Site 1's only real income is transport.
    absorbed = DT * 0.45 * np.maximum(e, 0.0)
    e -= absorbed
    state.res = state.res + absorbed

    # Mechanical channel kept tiny so it cannot bypass the transport law.
    amp = np.sqrt(np.maximum(e, 0.0))
    state.u = amp
    state.p = np.zeros(2)
    prev = state.q.copy()
    state.q = prev + DT * 3.0 * (amp - prev)
    state.r = (state.q - prev) / DT

    leak(state)
    bond(state)
    state.t += DT


# ===========================================================================
# Law R — resonant driven matter.
# ===========================================================================
def step_R(state: State, chi: float, *, omega_drive: float = 1.0) -> None:
    t = state.t
    omega_m = omega_drive + chi
    if omega_m <= 0.05:
        omega_m = 0.05
    gamma = 0.28
    drive = 0.70 * math.cos(omega_drive * t)
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
    capture(state, G * (field_val - q))
    leak(state)
    bond(state)
    state.t += DT


def run_L(k_f: float, *, driven: bool, seed: int) -> float:
    s = make_state(seed) if driven else make_state_L(seed)
    for _ in range(N_STEPS):
        step_L(s, k_f, driven=driven)
    return s.bond_time


def run_C(chi: float, *, seed: int) -> float:
    s = make_state(seed)
    for _ in range(N_STEPS):
        step_C(s, chi)
    return s.bond_time


def run_R(chi: float, *, seed: int) -> float:
    s = make_state(seed)
    for _ in range(N_STEPS):
        step_R(s, chi)
    return s.bond_time


def mean_s(fn, chi, *, seeds=range(8), **kw) -> float:
    return float(np.mean([fn(chi, seed=s, **kw) for s in seeds]))


def slope(xs, ys) -> float:
    x = np.asarray(xs, float)
    y = np.asarray(ys, float)
    if np.allclose(x, x[0]):
        return 0.0
    return float(np.polyfit(x, y, 1)[0])


def main() -> int:
    print("=" * 72)
    print("Two-site sign-structure verification (exploratory, not registered)")
    print(f"DT={DT} HORIZON={HORIZON} E_FORM={E_FORM} TAU_B={TAU_B} "
          f"ETA={ETA} LEAK={LEAK}")
    print("=" * 72)

    l_chis = [0.0, 0.05, 0.1, 0.2, 0.4, 0.8, 1.6, 3.2]
    print("\nLaw L (lock kills structured capture), closed box, chi = k_f")
    l_c = [mean_s(run_L, c, driven=False) for c in l_chis]
    for c, s in zip(l_chis, l_c):
        print(f"  k_f={c:4.2f}   S={s:8.4f}")
    sl_c = slope(l_chis, l_c)
    print(f"  slope={sl_c:+.6f}   expected <= 0")

    print("\nLaw L (lock kills structured capture), driven, chi = k_f")
    l_d = [mean_s(run_L, c, driven=True) for c in l_chis]
    for c, s in zip(l_chis, l_d):
        print(f"  k_f={c:4.2f}   S={s:8.4f}")
    sl_d = slope(l_chis, l_d)
    print(f"  slope={sl_d:+.6f}   expected <= 0")
    print(f"  drop S(0)-S(max) = {l_d[0] - l_d[-1]:.4f}")

    c_chis = [0.0, 0.05, 0.1, 0.2, 0.4, 0.8, 1.5, 3.0]
    print("\nLaw C (transport to starved site), chi = live-bond conductance")
    c_v = [mean_s(run_C, c) for c in c_chis]
    for c, s in zip(c_chis, c_v):
        print(f"  cond={c:4.2f}  S={s:8.4f}")
    sl = slope(c_chis, c_v)
    print(f"  slope={sl:+.6f}   expected > 0")
    print(f"  rise S(max)-S(0) = {c_v[-1] - c_v[0]:.4f}")

    r_chis = [-0.8, -0.5, -0.3, -0.15, 0.0, 0.15, 0.3, 0.5, 0.8, 1.2]
    print("\nLaw R (resonant), chi = detuning")
    r_v = [mean_s(run_R, c) for c in r_chis]
    for c, s in zip(r_chis, r_v):
        print(f"  detune={c:+5.2f}  S={s:8.4f}")
    peak_i = int(np.argmax(r_v))
    peak_chi = r_chis[peak_i]
    left_slope = slope(r_chis[: peak_i + 1], r_v[: peak_i + 1]) if peak_i > 0 else float("nan")
    right_slope = slope(r_chis[peak_i:], r_v[peak_i:]) if peak_i < len(r_chis) - 1 else float("nan")
    print(f"  peak chi*={peak_chi:+.2f}   expected near 0")
    print(f"  left slope={left_slope:+.6f}  expected > 0")
    print(f"  right slope={right_slope:+.6f} expected < 0")

    print("\n" + "=" * 72)
    print("SIGN STRUCTURE VERDICT")
    print("=" * 72)
    checks = [
        ("L closed-box dS/dk_f <= 0", sl_c <= 1e-9),
        ("L driven dS/dk_f <= 0", sl_d <= 1e-9),
        ("L driven drops by > 5", (l_d[0] - l_d[-1]) > 5.0),
        ("C dS/dcond > 0", sl > 0),
        ("C rises by > 5", (c_v[-1] - c_v[0]) > 5.0),
        ("R peak |chi*| <= 0.5", abs(peak_chi) <= 0.5),
        ("R left slope > 0", bool(peak_i > 0) and left_slope > 0),
        ("R right slope < 0", bool(peak_i < len(r_chis) - 1) and right_slope < 0),
        ("R peak-trough > 5", (max(r_v) - min(r_v)) > 5.0),
    ]
    ok = True
    for name, good in checks:
        ok &= good
        print(f"  [{'PASS' if good else 'FAIL'}] {name}")
    print()
    print("Overall:", "ALL THREE SIGN PATTERNS CONFIRMED" if ok else "MISSED — retune model")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
