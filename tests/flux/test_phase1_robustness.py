"""R-1d — Phase-1 joint robustness gate.

Pre-registered acceptance (locked in QUEUE.yaml R-1d):

- ``test_all_T_tests_pass_jointly_on_8_of_10_seeds``:
    For each of the 10 seeds in ``SEEDS``, run T1+T2+T3+T4 sequentially with
    the R-1b pressure-gradient extension active. Assert that on at least
    8 of the 10 seeds, all four T-tests pass with the same identical
    parameter envelope (no per-seed tweaks).

- ``test_no_T_test_regresses_under_extension``:
    For each T-test, count the number of seeds it passes on with the R-1b
    extension active vs with it disabled (pressure_coeff=0 in the thermal
    config; T1/T3/T4 do not pass a ThermalConfig at all, so the extension is
    architecturally inactive in those paths regardless). Assert each test's
    pass-count under the R-1b extension is at least as large as its
    pass-count without.

The four T-tests are the canonical Phase-1 falsifiers:

- T1 — energy conservation over 1000 ticks (``test_T1_conservation_over_1000_ticks``)
- T2 — Bénard horizontal wavelength FFT check (``test_T2_benard_horizontal_wavelength``)
- T3 — crystallization preference for the cold (top) half (``test_T3_crystallization_in_cold_half``)
- T4 — structure decay when injection stops (``test_T4_decay_without_flux``)

Each runner here is a direct port of the canonical test logic with the seed
parameterised through ``np.random.default_rng``. Configuration (cube dims,
buoyancy, injection rates, thresholds) is locked to whatever the canonical
test uses — R-1d is a robustness audit, not a re-tuning opportunity. The
charter forbids loosening thresholds.

The two tests share intermediate state through ``_CACHE`` so a postflight that
runs both nodes in a single pytest invocation does not pay the substrate cost
twice. The cache key is ``(test_name, seed, pressure_coeff)``.
"""
from __future__ import annotations
import numpy as np
import pytest

from world.flux.audit import EnergyAuditor
from world.flux.binding import BindingConfig
from world.flux.boundary import inject_hot_floor
from world.flux.bridges import Bridges
from world.flux.decay import DecayConfig
from world.flux.dynamics import tick
from world.flux.grid import Grid
from world.flux.plasticity import PlasticityConfig
from world.flux.quantum import Quanta
from world.flux.structures import Nodes
from world.flux.thermal import ThermalConfig


SEEDS = [7, 13, 21, 42, 100, 137, 256, 314, 500, 1000]

# Cache keyed by (test_name, seed, pressure_coeff). Stores {'passed', 'reason',
# plus measurement diagnostics}. Reused across the two pre-registered tests so
# a single pytest invocation does not pay the substrate cost twice.
_CACHE: dict[tuple, dict] = {}


def _run_T1(seed: int) -> dict:
    """T1: 1000 ticks of constant injection on a 10x10x10 cube, no binding.

    Mirrors ``tests/flux/test_conservation.py::test_T1_conservation_over_1000_ticks``.
    R-1b extension is architecturally inactive here — no ThermalConfig is
    passed into ``tick()``, so ``apply_pressure_gradient_force`` is never
    called. ``pressure_coeff`` is therefore not a parameter of this runner.
    """
    key = ("T1", seed, None)
    if key in _CACHE:
        return _CACHE[key]

    rng = np.random.default_rng(seed)
    q = Quanta(max_quanta=20_000)
    g = Grid(dims=(10, 10, 10), voxel_size=1.0, T_smoothing=0.1)
    audit = EnergyAuditor(quanta=q, tol=1e-9)
    audit.record_initial()

    QUANTA_PER_TICK = 5
    ENERGY_PER = 1.0
    N_TICKS = 1000
    DT = 0.1

    def injector(quanta, grid):
        injected_count = inject_hot_floor(
            quanta, grid,
            n=QUANTA_PER_TICK, energy_per=ENERGY_PER,
            freq_mean=200.0, vel_z_mean=2.0, rng=rng,
        )
        audit.record_injection(injected_count * ENERGY_PER)
        return injected_count * ENERGY_PER

    try:
        for _ in range(N_TICKS):
            exported = tick(q, g, dt=DT, injector=injector)
            audit.record_export(exported)
            audit.check()
            audit.step()
        audit.check()
        E_in = q.total_energy()
        # Pre-registered accounting check from test_conservation.py
        atol = 1e-9 * max(audit.E_injected_total, 1.0)
        residual = abs(
            (audit.E_initial + audit.E_injected_total)
            - (E_in + audit.E_exported_total)
        )
        passed = (
            audit.E_injected_total > 0
            and audit.E_injected_total <= N_TICKS * QUANTA_PER_TICK * ENERGY_PER
            and E_in >= 0
            and audit.E_exported_total >= 0
            and residual <= atol
        )
        reason = None if passed else f"conservation residual {residual:.3e} > atol {atol:.3e}"
    except Exception as exc:  # noqa: BLE001 — record substrate errors as test failures
        passed = False
        reason = f"{type(exc).__name__}: {exc}"

    out = {"passed": bool(passed), "reason": reason}
    _CACHE[key] = out
    return out


def _run_T2(seed: int, pressure_coeff: float) -> dict:
    """T2: 10000 ticks Bénard convection on an 80x40x10 cube.

    Mirrors ``tests/flux/test_benard.py::test_T2_benard_horizontal_wavelength``.
    The R-1b extension is gated by ``ThermalConfig.pressure_coeff``: at 1.0
    the pressure-gradient horizontal force is active; at 0.0 it is a no-op
    (early-return inside ``apply_pressure_gradient_force``). Every other
    parameter is identical to the canonical T2 test.
    """
    key = ("T2", seed, pressure_coeff)
    if key in _CACHE:
        return _CACHE[key]

    rng_inject = np.random.default_rng(seed)
    LX, LY, LZ = 80, 40, 10
    q = Quanta(max_quanta=200_000)
    g = Grid(dims=(LX, LY, LZ), voxel_size=1.0, T_smoothing=0.1)
    audit = EnergyAuditor(quanta=q, tol=1e-9)
    audit.record_initial()

    tcfg = ThermalConfig(
        buoyancy_g=2.0, damping_mu=0.5, T_ref=0.0,
        T_hot_floor=5.0, T_cold_ceiling=0.0,
        pressure_coeff=pressure_coeff,
    )

    N_PER_TICK = 20
    DT = 0.1
    N_TICKS = 10_000

    def injector(quanta, grid):
        count = inject_hot_floor(
            quanta, grid, n=N_PER_TICK, energy_per=1.0,
            freq_mean=200.0, vel_z_sigma=0.5, vel_xy_sigma=0.5,
            rng=rng_inject,
        )
        audit.record_injection(count * 1.0)
        return count * 1.0

    diagnostic: dict = {}
    try:
        for _ in range(N_TICKS):
            exported = tick(q, g, dt=DT, injector=injector, thermal_cfg=tcfg)
            audit.record_export(exported)
            audit.check()
            audit.step()
        mid_z = LZ // 2
        profile = g.T[:, LY // 2, mid_z]
        fft = np.abs(np.fft.rfft(profile - profile.mean()))
        diagnostic["profile_std"] = float(profile.std())
        if fft.sum() == 0:
            passed, reason = False, "flat horizontal T profile — no convection"
            diagnostic["k_peak"] = 0
            diagnostic["wavelength"] = 0.0
        else:
            k_peak = int(np.argmax(fft))
            diagnostic["k_peak"] = k_peak
            if k_peak == 0:
                passed, reason = False, "FFT peak at DC (k=0)"
                diagnostic["wavelength"] = float("inf")
            else:
                wavelength = LX / k_peak
                expected = 2.0 * LZ  # 20
                tol = 0.30 * expected
                diagnostic["wavelength"] = float(wavelength)
                diagnostic["expected"] = float(expected)
                diagnostic["tol"] = float(tol)
                passed = abs(wavelength - expected) <= tol
                reason = (
                    None if passed
                    else f"wavelength {wavelength:.2f} not within +/-{tol:.2f} of {expected:.2f}"
                )
    except Exception as exc:  # noqa: BLE001
        passed = False
        reason = f"{type(exc).__name__}: {exc}"

    out = {"passed": bool(passed), "reason": reason, **diagnostic}
    _CACHE[key] = out
    return out


def _run_T3(seed: int) -> dict:
    """T3: 5000 ticks crystallization on 10x10x10, full binding/decay/plasticity.

    Mirrors ``tests/flux/test_crystallization.py::test_T3_crystallization_in_cold_half``.
    No ThermalConfig is passed, so R-1b extension is inactive in this path.
    """
    key = ("T3", seed, None)
    if key in _CACHE:
        return _CACHE[key]

    rng_inject = np.random.default_rng(seed)
    rng_bind = np.random.default_rng(seed + 1_000_000)
    q = Quanta(max_quanta=50_000)
    n = Nodes(max_nodes=50_000)
    br = Bridges(max_bridges=500_000)
    g = Grid(dims=(10, 10, 10), voxel_size=1.0, T_smoothing=0.1)
    audit = EnergyAuditor(quanta=q, nodes=n, bridges=br, tol=1e-9)
    audit.record_initial()

    cfg = BindingConfig(
        alpha=4.0, beta=4.0, T_crit=2.0,
        eta=0.1, r=1.5, coherence_eps=1.0,
        r_bridge=2.0, bridge_w0=1.0,
    )
    decay_cfg = DecayConfig(gamma=500.0, T_decay_crit=0.035)
    pcfg = PlasticityConfig(gamma=0.1, lam=0.1, flux_min=1.0,
                            w_min=0.05, r_flux=0.75)

    QUANTA_PER_TICK = 5
    ENERGY_PER = 1.0
    N_TICKS = 5000
    DT = 0.1

    def injector(quanta, grid):
        count = inject_hot_floor(
            quanta, grid, n=QUANTA_PER_TICK, energy_per=ENERGY_PER,
            freq_mean=200.0, vel_z_mean=2.0, rng=rng_inject,
        )
        audit.record_injection(count * ENERGY_PER)
        return count * ENERGY_PER

    diagnostic: dict = {}
    try:
        for t in range(N_TICKS):
            exported, binding_heat, decay_heat = tick(
                q, g, dt=DT, injector=injector,
                nodes=n, binding_cfg=cfg, decay_cfg=decay_cfg,
                bridges=br, plasticity_cfg=pcfg,
                rng=rng_bind, tick_index=t,
            )
            audit.record_export(exported)
            audit.record_binding_heat(binding_heat)
            audit.record_decay_heat(decay_heat)
            audit.check()
            audit.step()
        audit.check()
        alive_mask = n.alive
        n_alive = int(alive_mask.sum())
        diagnostic["n_alive"] = n_alive
        if n_alive == 0:
            passed, reason = False, "no nodes formed"
        else:
            node_z = n.pos[alive_mask, 2]
            Lz_half = g.dims[2] * g.voxel_size / 2.0
            n_top = int((node_z >= Lz_half).sum())
            n_bot = int((node_z < Lz_half).sum())
            diagnostic["n_top"] = n_top
            diagnostic["n_bot"] = n_bot
            if n_bot == 0:
                passed = n_top > 0  # trivially > 5x
                reason = None if passed else "no nodes anywhere"
                diagnostic["ratio"] = float("inf") if passed else 0.0
            else:
                ratio = n_top / n_bot
                diagnostic["ratio"] = ratio
                passed = ratio > 5.0
                reason = None if passed else f"ratio {ratio:.2f} <= 5.0 (top={n_top}, bot={n_bot})"
    except Exception as exc:  # noqa: BLE001
        passed = False
        reason = f"{type(exc).__name__}: {exc}"

    out = {"passed": bool(passed), "reason": reason, **diagnostic}
    _CACHE[key] = out
    return out


def _run_T4(seed: int) -> dict:
    """T4: 5000 ticks injection + 5000 ticks no-injection on 10x10x10.

    Mirrors ``tests/flux/test_decay.py::test_T4_decay_without_flux``. No
    ThermalConfig passed; R-1b extension architecturally inactive here.
    """
    key = ("T4", seed, None)
    if key in _CACHE:
        return _CACHE[key]

    rng_inject = np.random.default_rng(seed)
    rng_bind = np.random.default_rng(seed + 1_000_000)
    q = Quanta(max_quanta=50_000)
    n = Nodes(max_nodes=50_000)
    br = Bridges(max_bridges=500_000)
    g = Grid(dims=(10, 10, 10), voxel_size=1.0, T_smoothing=0.1)
    audit = EnergyAuditor(quanta=q, nodes=n, bridges=br, tol=1e-9)
    audit.record_initial()

    cfg = BindingConfig(alpha=4.0, beta=4.0, T_crit=2.0, eta=0.1,
                        r=1.5, coherence_eps=1.0,
                        r_bridge=2.0, bridge_w0=1.0)
    decay_cfg = DecayConfig(gamma=500.0, T_decay_crit=0.035)
    pcfg = PlasticityConfig(gamma=0.1, lam=0.1, flux_min=1.0,
                            w_min=0.05, r_flux=0.75)

    QUANTA_PER_TICK = 5
    ENERGY_PER = 1.0
    DT = 0.1

    def injector(quanta, grid):
        count = inject_hot_floor(
            quanta, grid, n=QUANTA_PER_TICK, energy_per=ENERGY_PER,
            freq_mean=200.0, vel_z_mean=2.0, rng=rng_inject,
        )
        audit.record_injection(count * ENERGY_PER)
        return count * ENERGY_PER

    diagnostic: dict = {}
    try:
        peak = 0
        for t in range(5000):
            exported, binding_heat, decay_heat = tick(
                q, g, dt=DT, injector=injector,
                nodes=n, binding_cfg=cfg, decay_cfg=decay_cfg,
                bridges=br, plasticity_cfg=pcfg,
                rng=rng_bind, tick_index=t,
            )
            audit.record_export(exported)
            audit.record_binding_heat(binding_heat)
            audit.record_decay_heat(decay_heat)
            audit.check()
            audit.step()
            peak = max(peak, int(n.n_alive()))
        diagnostic["peak"] = peak
        if peak == 0:
            passed, reason = False, "no structures formed in Phase A"
            diagnostic["end"] = 0
            diagnostic["ratio"] = 0.0
        else:
            for t in range(5000, 10000):
                exported, binding_heat, decay_heat = tick(
                    q, g, dt=DT, injector=None,
                    nodes=n, binding_cfg=cfg, decay_cfg=decay_cfg,
                    bridges=br, plasticity_cfg=pcfg,
                    rng=rng_bind, tick_index=t,
                )
                audit.record_export(exported)
                audit.record_binding_heat(binding_heat)
                audit.record_decay_heat(decay_heat)
                audit.check()
                audit.step()
            end_count = int(n.n_alive())
            ratio = end_count / peak
            diagnostic["end"] = end_count
            diagnostic["ratio"] = ratio
            passed = ratio < 0.10
            reason = None if passed else f"end/peak={ratio:.3f} not below 0.10 (peak={peak}, end={end_count})"
    except Exception as exc:  # noqa: BLE001
        passed = False
        reason = f"{type(exc).__name__}: {exc}"

    out = {"passed": bool(passed), "reason": reason, **diagnostic}
    _CACHE[key] = out
    return out


def _summarise_per_seed(results: dict[int, dict[str, dict]]) -> str:
    lines = []
    for s in SEEDS:
        flags = "".join(
            "P" if results[s][t]["passed"] else "F"
            for t in ("T1", "T2", "T3", "T4")
        )
        t2 = results[s]["T2"]
        wl = t2.get("wavelength", float("nan"))
        lines.append(
            f"  seed={s:>4}  T1{flags[0]} T2{flags[1]} T3{flags[2]} T4{flags[3]}"
            f"  (T2 wavelength={wl:.2f})"
        )
    return "\n".join(lines)


@pytest.mark.slow
def test_all_T_tests_pass_jointly_on_8_of_10_seeds():
    """Joint Phase-1 robustness gate.

    With the R-1b pressure-gradient force active (``pressure_coeff=1.0`` in
    T2's ThermalConfig — its locked default), require that T1+T2+T3+T4 all
    pass on at least 8 of the 10 pre-registered seeds. The seed grid and the
    parameter envelope (cube dims, buoyancy, injection rate, thresholds) are
    identical across seeds — no per-seed tweaks. Threshold ``>= 8/10`` is
    pre-registered (QUEUE.yaml R-1d) and may not be moved.
    """
    results: dict[int, dict[str, dict]] = {}
    for s in SEEDS:
        results[s] = {
            "T1": _run_T1(s),
            "T2": _run_T2(s, pressure_coeff=1.0),
            "T3": _run_T3(s),
            "T4": _run_T4(s),
        }

    joint_passes = sum(
        1
        for s in SEEDS
        if all(results[s][t]["passed"] for t in ("T1", "T2", "T3", "T4"))
    )

    detail = _summarise_per_seed(results)
    assert joint_passes >= 8, (
        f"R-1d joint gate FAIL: only {joint_passes}/10 seeds had all four T-tests "
        f"pass simultaneously (pre-registered threshold 8/10).\n"
        f"Per-seed verdict (P=pass, F=fail):\n{detail}"
    )


@pytest.mark.slow
def test_no_T_test_regresses_under_extension():
    """Per-test no-regression gate.

    With the R-1b extension active, each T-test must pass on at least as
    many seeds as it did before R-1b. R-1b's gate is ``ThermalConfig.
    pressure_coeff``: at 1.0 the pressure-gradient force fires; at 0.0 the
    force early-returns and the substrate behaves as it did before R-1b.

    T1, T3, T4 do not pass a ThermalConfig into ``tick()``, so the R-1b
    extension is architecturally inactive in those paths regardless of the
    ``pressure_coeff`` value — those tests are tautologically identical with
    and without R-1b. T2 is the only test whose behavior depends on R-1b's
    activation; the comparison is meaningful only there.
    """
    test_runners_no_extension: dict[str, list[bool]] = {
        "T1": [],
        "T2": [],
        "T3": [],
        "T4": [],
    }
    test_runners_with_extension: dict[str, list[bool]] = {
        "T1": [],
        "T2": [],
        "T3": [],
        "T4": [],
    }
    for s in SEEDS:
        # T1 / T3 / T4 — R-1b architecturally inactive; one run suffices.
        t1 = _run_T1(s)["passed"]
        t3 = _run_T3(s)["passed"]
        t4 = _run_T4(s)["passed"]
        test_runners_no_extension["T1"].append(t1)
        test_runners_with_extension["T1"].append(t1)
        test_runners_no_extension["T3"].append(t3)
        test_runners_with_extension["T3"].append(t3)
        test_runners_no_extension["T4"].append(t4)
        test_runners_with_extension["T4"].append(t4)
        # T2 — the only test whose path the R-1b extension actually changes.
        test_runners_no_extension["T2"].append(
            _run_T2(s, pressure_coeff=0.0)["passed"]
        )
        test_runners_with_extension["T2"].append(
            _run_T2(s, pressure_coeff=1.0)["passed"]
        )

    regressions: list[str] = []
    for t in ("T1", "T2", "T3", "T4"):
        n_off = sum(test_runners_no_extension[t])
        n_on = sum(test_runners_with_extension[t])
        if n_on < n_off:
            regressions.append(
                f"{t}: {n_on}/10 with R-1b vs {n_off}/10 without — REGRESSION"
            )

    assert not regressions, (
        "R-1d no-regression gate FAIL: at least one T-test passes on fewer "
        "seeds under the R-1b pressure-gradient extension than without it.\n"
        + "\n".join(regressions)
        + "\nPer-test pass counts (with R-1b / without R-1b):\n"
        + "\n".join(
            f"  {t}: "
            f"{sum(test_runners_with_extension[t])}/10 / "
            f"{sum(test_runners_no_extension[t])}/10"
            for t in ("T1", "T2", "T3", "T4")
        )
    )
