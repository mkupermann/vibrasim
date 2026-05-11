# Flux Substrate — Phase Log

Append-only build log. Each entry: date, phase, status, key decisions.

## 2026-05-10 — F0 start

- Spec committed at `2bab7a7`.
- Plan: `docs/superpowers/plans/2026-05-10-flux-substrate-F0.md`.
- Target: skeleton + T1 conservation test passes.
- Estimated 1 week solo.

## 2026-05-11 — F0 complete

- 9 plan tasks landed across 12 commits (`09f9488..750337b`).
- 33/33 flux tests pass (`tests/flux/`). 382 legacy tests untouched.
- T1 acceptance test green: energy conservation holds within 1e-9 relative tolerance per-tick across 1000 ticks of constant injection.
- README §"Two substrates" names legacy + flux side by side.

Known carry-overs into F1:
- **Spec §6 tick order**: spec lists `inject → absorb → move`; F0 implements `inject → move → absorb` per the F0 plan. Both preserve conservation. F1 should reconcile when adding `interact` and `structure-flux` steps.
- **`Quanta.add` is a pure-Python O(N) linear scan.** Adequate for F0 at 10×10×10/5 quanta-per-tick; will become the bottleneck after binding + plasticity. Numba-ify in F1 if profiling confirms.
- **Cleanup landed pre-F1**: `Quanta.remove_batch` encapsulates the previously-private cursor reset; `world/flux/__init__.py` now re-exports the public API; type hints unified on PEP-604 style.

F1 plan to be written next.

## 2026-05-11 — F1a start

- F0 closed: 33/33 flux tests + 382 legacy tests + T1 conservation green; commits `09f9488..4d6d1b0`.
- F1a target: T3 (crystallization at cold zones) passes.
  - Binding rule per spec §3: `p_bind = sigmoid(α * pred_coherence + β * (T_crit - T_local))`
  - `pred_coherence` simplified to frequency-equality within ε for F1a (full cross-correlation deferred to F2 when cochlea brings multi-frequency input).
  - Binding is exothermic: fraction `η` of binding energy exported as heat.
  - No bridges, no plasticity, no decay in F1a — those land in F1b.
- Plan: `docs/superpowers/plans/2026-05-11-flux-substrate-F1a.md`.
- Estimated 1–2 weeks solo.

## 2026-05-11 — F1a Task 10 calibration: T3 needs minimal decay (scope expansion)

T3 was the F1a acceptance test. With the plan's default BindingConfig
(`alpha=4, beta=4, T_crit=2, eta=0.1, r=1.5`) the test fails with
ratio ≈ 0.02 — almost all binding happens at the hot floor, the
opposite of what T3 expects.

**Diagnosis (instrumented run, 500 ticks, default cfg):**
- Per-layer mean T_local: z=0 0.036, z=1 0.054, z=5 0.026, z=9 0.007.
- With T_crit=2.0, term `β*(T_crit - T_local) ≈ 4·2 = 8` everywhere →
  `p_bind ≈ 1.0` regardless of altitude. T-gate saturates.
- Most binding events at z=[0,1) happen in voxels with low
  instantaneous T_local (mean 0.09) because injection touches only
  5/100 floor voxels per tick.
- Just-injected quanta cluster at the floor in xy and bind before
  the T-update step (T-update is spec §6 step 8, after binding).

**13 BindingConfig + r + vel_z + injection-rate + tick-order sweeps**
exhausted the pure-calibration space. Best ratio without code change:
1.04 (D10, `alpha=0, beta=200, T_crit=0.05, r=0.3`). Pair density at
the floor dominates regardless of T-gate aggression.

**Scope expansion (user-approved 2026-05-11):** add a minimal
F1a-level node decay. Spec §5.4's full decay couples to bridges
(F1b territory); the F1a stub uses a direct T-based decay:

```
p_decay = sigmoid(gamma * (T_local - T_decay_crit))
```

Decay reads `T_local` as the **xy-mean of grid.T at the node's
z-layer** rather than the per-voxel value. The layer-mean smooths
over the sparse-injection problem and is the F1a proxy for spec
§5.4's bridge-flux-coupled decay. The bridge mechanism (F1b) will
replace this proxy.

**Decay calibration sweeps (1000-tick probes; 5000-tick gates):**

| sweep | gamma | T_dc | total | top | bot | ratio |
|---|---|---|---|---|---|---|
| D16 | 200 | 0.050 | 34 | 13 | 21 | 0.62 |
| D17 | 200 | 0.060 | 162 | 25 | 137 | 0.18 |
| D21 | 500 | 0.025 | 0 | 0 | 0 | — |
| D23 | 700 | 0.030 | 4 | 3 | 1 | 3.0 |
| D26 | 700 | 0.030 | 6 | 6 | 0 | ∞ (PASS, 5k) |
| **D27** | **500** | **0.035** | **10** | **9** | **1** | **9.0 (PASS, locked)** |
| D29 | 400 | 0.035 | 7 | 7 | 0 | ∞ (PASS, 5k) |
| D30 | 600 | 0.032 | 8 | 8 | 0 | ∞ (PASS, 5k) |
| D32 | 300 | 0.035 | 5 | 3 | 2 | 1.5 |
| D34 | 150 | 0.045 | 3 | 2 | 1 | 2.0 |

Locked: **`DecayConfig(gamma=500.0, T_decay_crit=0.035)`** —
ratio 9.0 with 10 surviving nodes after 5000 ticks. Floor layer-mean
T (~0.035–0.054) sits above T_decay_crit so floor nodes decay almost
deterministically per tick; ceiling layer-mean T (~0.007) sits well
below so ceiling nodes survive indefinitely.

**Files touched by scope expansion:**
- new `world/flux/decay.py` — DecayConfig, decay_probability, attempt_decay
- `world/flux/audit.py` — `E_decay_heat_total`, `record_decay_heat`,
  conservation equation extended to include decay heat
- `world/flux/dynamics.py` — `tick(..., decay_cfg=)` kwarg; F1a-mode
  return is now `(exported, binding_heat, decay_heat)` 3-tuple
- `tests/flux/test_conservation.py::test_T1_conservation_with_binding_active`
  unpacks 3-tuple, records decay heat
- `tests/flux/test_dynamics.py` binding-tick test unpacks 3-tuple
- `tests/flux/test_crystallization.py` uses both BindingConfig and DecayConfig

**Result:** 64/64 flux tests pass; 382/382 legacy tests pass; T3 ratio 9.0 > 5.0.
