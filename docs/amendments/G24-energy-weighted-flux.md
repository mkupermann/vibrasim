# Amendment G24 — Energy-weighted flux

**Status: pre-registered, not yet implemented. Gated by `R-17` (implementation) and `R-18` (50k-tick verification).**
**Frozen: 2026-05-20. Author: Claude under user mandate 2026-05-19 "Du machst alleine weiter, bis wir eine funktionierende Architektur haben".**

If a future reader finds this file edited after R-17 or R-18 have been run against it, that is a protocol violation and the runs' verdicts are void.

---

## 0. Why this exists

R-16 (autopilot session 2026-05-20T00:33Z, branch `autopilot/R-16`) returned NULL on both pre-registered architectural-firewall diagnostic tests:

- English vs matched-RMS white noise, 50k ticks each: symmetric KL = **0.000000** (threshold 0.01).
- English vs silence, 50k ticks each: symmetric KL = **0.000000** (threshold 0.1).

The R-16 session committed the precise architectural diagnosis: `inject_raw_audio_sample` (in `agent/flux/audio_raw.py`) writes `abs(sample_value)` into `quanta.energy`, but `count_flux_through` (in `world/flux/plasticity.py`) reads only quantum-presence, not quantum-energy. Quantum positions are deterministic per `sample_index` via `position_hash(sample_index, Lx, Ly, s, seed=position_hash_seed)`, independent of the audio waveform. Under identical seed, the substrate produces bit-identical bridges regardless of which audio is fed in. The architectural firewall is total, not partial.

This contradicts the flux-substrate spec's first principle, `docs/superpowers/specs/2026-05-10-flux-substrate-design.md` line 16:

> Energy flows through an open boundary. Structures kondensieren wo sie diesen Fluss effizienter kanalisieren als kein Struktur.

The spec says energy. The code counts presence. G24 brings the code into line with the spec.

R-13 (eca9545, 2026-05-19) was the qualitative forensic identification of this firewall; R-16 is the quantitative confirmation at KL=0.000000.

---

## 1. The change

### 1.1 New energy-weighted plasticity pathway

Add a new function in `world/flux/plasticity.py`:

```python
def count_energy_flux_through(
    bridges: Bridges, nodes: Nodes,
    quanta: Quanta, cfg: PlasticityConfig,
) -> np.ndarray:
    """Return shape (max_bridges,) of FLOAT energy-summed flux.

    For each alive bridge connecting nodes (a, b), sum the energies of
    alive quanta whose perpendicular distance to the segment ab is
    < cfg.r_flux. A self-bridge (a == b) sums quanta energies within
    cfg.r_flux of the node's position.

    Same geometry as count_flux_through, but the return is sum of
    quanta.energy[hits] instead of len(hits). Float64.
    """
```

Existing `count_flux_through` is **unchanged** and stays the default. The legacy F1b → F1c tests (T1 conservation, T2 Bénard, T3 crystallization, T4 decay) all continue using the count-based path. No threshold retuning needed; no regression risk to those tests.

### 1.2 New plasticity-update alongside existing

Add in `world/flux/plasticity.py`:

```python
def apply_plasticity_energy_weighted(
    bridges: Bridges, energy_flux: np.ndarray,
    cfg: PlasticityConfig, tick_index: int,
) -> None:
    """In-place bridge-weight update, per-bridge energy flux input.

    Same rule as apply_plasticity:
        w_new = w_old + gamma * energy_flux - lam * max(0, flux_min - energy_flux)
    but energy_flux is float64 (sum of crossing quanta energies), not
    int64 count. flux_min is treated as a float threshold under the
    same units (energy per tick), not as a quantum count.
    """
```

Same arithmetic shape as `apply_plasticity`; only the input type differs (float energy vs int count).

### 1.3 Opt-in via env var in encoder-free training

`agent/flux/encoder_free_training.py` gains an env-controlled branch:

```python
USE_ENERGY_WEIGHTED_FLUX = os.environ.get(
    "EQMOD_USE_ENERGY_WEIGHTED_FLUX", "0"
) == "1"

if USE_ENERGY_WEIGHTED_FLUX:
    energy_flux = count_energy_flux_through(bridges, nodes, quanta, cfg)
    apply_plasticity_energy_weighted(bridges, energy_flux, cfg, tick_index)
else:
    flux = count_flux_through(bridges, nodes, quanta, cfg)
    apply_plasticity(bridges, flux, cfg, tick_index)
```

Default is the legacy count-based path. The new energy-weighted path is enabled only by explicit env-var opt-in. R-LR-8 (already-queued long-run that wires R-14's tuned synthesis) does NOT use G24; only future R-LR-9 will set `EQMOD_USE_ENERGY_WEIGHTED_FLUX=1`.

### 1.4 What G24 does NOT change

- `count_flux_through` stays as it is.
- `apply_plasticity` stays as it is.
- T1 conservation, T2 Bénard, T3 crystallization, T4 decay all stay on the count-based path. Their thresholds do not move.
- `inject_raw_audio_sample` stays as it is — the firewall is on the read side, not the write side, and the fix is to read the energy field that injection already writes.
- Quantum positions stay deterministic per `sample_index`. The G24 fix uses the position-deterministic but energy-content-dependent quantum field that injection produces, without touching positions.

---

## 2. Why this design

### 2.1 Why energy-weighting and not content-driven positioning

R-13's forensic note proposed two paths in the closing recommendation: "(a) energy-weight `_compute_density` or (b) amplitude-mix `position_hash_seed`". G24 picks (a) for these reasons:

- The spec's first principle is energy. Energy-weighting brings the implementation into line with the design document, not the other way around.
- Encoder-free is preserved. No FFT, no content-based positioning, no audio-derived seed.
- Backward compat is clean. The change is additive: new functions next to old, env-var-gated. T1–T4 unaffected by construction.
- It is the smallest change that breaks the firewall. The spec already specifies energy quanta carrying floats; the code already writes those floats; only the plasticity-readout step was integer-coarsened.

### 2.2 Why opt-in via env var, not a default replacement

If `count_flux_through` is replaced by `count_energy_flux_through` at the call site, the legacy T1–T4 tests would all need their `flux_min` / `gamma` / `lam` parameters retuned to the new units (sum-of-energies-per-tick vs count-per-tick). That parameter sweep would be post-hoc and would void the pre-registration on T1–T4. The opt-in design avoids this: legacy path keeps its parameter envelope, new path gets its own envelope determined in R-17 / R-18.

### 2.3 Pre-registered prediction (will be measured by R-18)

If G24 works, R-18 (50k smoke under `EQMOD_USE_ENERGY_WEIGHTED_FLUX=1`) will show:

- English vs matched-RMS white noise: bridge-spectrum KL **above 0.01** (R-16 was 0.000000).
- English vs silence: bridge-spectrum KL **above 0.1** (R-16 was 0.000000).
- T1 conservation: holds (energy-summing is additive, no conservation violation).
- T2 / T3 / T4: not measured — they stay on the count-based path.

If G24 does NOT work, R-18 NULLs on the same two gates, and a separate amendment is needed.

---

## 3. Pre-registered acceptance — R-17 (implementation)

Locked, no retuning. The R-17 autopilot session opens a branch `autopilot/R-17` and must satisfy each of the following tests under the new energy-weighted path. None of these are measured against R-18's real-audio thresholds; R-17 verifies the implementation is mechanically correct, R-18 verifies it produces content-coupling.

| # | Test | Pass condition |
|---|---|---|
| 1 | `tests/flux/test_g24_amendment.py::test_count_energy_flux_through_sums_quanta_energy` | Synthetic substrate with 3 alive quanta of energies `{1.0, 2.0, 4.0}` all within `r_flux` of one alive bridge: `count_energy_flux_through` returns 7.0 for that slot. `count_flux_through` returns 3 for that slot. Both arrays match the F1b shape `(max_bridges,)`. |
| 2 | `tests/flux/test_g24_amendment.py::test_count_energy_flux_through_zero_quanta_returns_zeros` | 0 alive quanta → returns a float array of all zeros (no NaN). |
| 3 | `tests/flux/test_g24_amendment.py::test_apply_plasticity_energy_weighted_strengthens_proportionally` | Two bridges, one receives `energy_flux=10.0`, the other `energy_flux=2.0`, both above `flux_min`. After one apply, the first bridge's weight gain is exactly 5× the second's (matches the linear `gamma * flux` term). |
| 4 | `tests/flux/test_g24_amendment.py::test_apply_plasticity_energy_weighted_decay_below_flux_min` | Bridge with `energy_flux=0.0` and `flux_min=1.0`: weight decreases by `lam * 1.0` per tick. Bridge with `energy_flux=0.5`: weight decreases by `lam * 0.5`. Bridge with `energy_flux=1.5`: weight INcreases (linear in `gamma * 1.5`). |
| 5 | `tests/flux/test_g24_amendment.py::test_env_var_routes_to_weighted_path_in_encoder_free_training` | With `EQMOD_USE_ENERGY_WEIGHTED_FLUX=1` set in environment, `agent.flux.encoder_free_training.training_step` (or current equivalent entry point) calls `count_energy_flux_through` and `apply_plasticity_energy_weighted` instead of the count-based functions. Verified via monkey-patching both functions and asserting the weighted ones are called and the count-based ones are not. |
| 6 | `tests/flux/test_g24_amendment.py::test_env_var_default_keeps_count_based_path` | Without the env var (or set to "0"), the training step calls the count-based functions, not the weighted ones. Verified via the same monkey-patch fixture. |
| 7 | `tests/flux/test_conservation.py PASSES` | T1 holds under the legacy count-based path. |
| 8 | `tests/flux/test_crystallization_robustness.py PASSES` | T3 holds under the legacy count-based path. |
| 9 | `tests/flux/test_bridge_spectrum.py PASSES` | R-15's salvaged tests still pass. |
| 10 | `tests/flux/test_R_LR_8_acceptance.py is collected by pytest` | R-15's scaffold still imports cleanly; G24 changes do not break R-LR-8's pipeline. |
| 11 | `pytest -m 'not slow' PASSES` | Full fast-slice suite green. |

The R-17 session writes `LOGBOOK.md` with the standard 5-line autopilot entry plus a one-paragraph note on whether the implementation matches this amendment doc line-for-line.

Time budget: 4 hours.

---

## 4. Pre-registered acceptance — R-18 (50k-tick verification)

Locked, no retuning. The R-18 autopilot session opens a branch `autopilot/R-18` and runs the same matched-RMS pairs as R-16, but with `EQMOD_USE_ENERGY_WEIGHTED_FLUX=1` set in the test fixture.

| # | Test | Pass condition |
|---|---|---|
| 1 | `tests/flux/test_g24_verification.py::test_50k_english_vs_white_noise_KL_above_0p01_under_weighted_path` | Two encoder-free 50k-tick substrates, identical seed, identical RMS budget, English audio vs matched-RMS white noise, both under `EQMOD_USE_ENERGY_WEIGHTED_FLUX=1`. Symmetric KL of bridge-weight spectra > **0.01**. (Threshold identical to R-16's failed gate; G24 either breaks the firewall here or it does not.) |
| 2 | `tests/flux/test_g24_verification.py::test_50k_english_vs_silence_KL_above_0p1_under_weighted_path` | Same configuration but English vs silence-with-matched-RMS-noise-floor. KL > **0.1**. Threshold identical to R-16's failed gate. |
| 3 | `tests/flux/test_g24_verification.py::test_50k_white_noise_vs_white_noise_independent_seeds_KL_below_0p005_under_weighted_path` | Negative control: two white-noise substrates with INDEPENDENT seeds but the same audio statistics; KL between their bridge spectra < **0.005**. Confirms G24's content-coupling does not produce spurious differences between two same-distribution inputs. |
| 4 | `tests/flux/test_conservation.py PASSES` | T1 robust. |
| 5 | `tests/flux/test_crystallization_robustness.py PASSES` | T3 robust. |
| 6 | LOGBOOK entry must record all three KL numbers and the random seeds used. | Mechanical. |

R-18 PASS condition: gates 1, 2, 3 all pass. R-18 NULL on gates 1 or 2 means G24 does not break the firewall (which is itself an architectural finding — the amendment design is wrong, not the protocol). R-18 NULL on gate 3 means G24 over-fits to seed (the substrate distinguishes inputs it should not).

If R-18 PASSES, queue R-LR-9 in the long-run queue: 1.8M-tick run with `EQMOD_USE_ENERGY_WEIGHTED_FLUX=1` for full-scale architectural verdict.

If R-18 NULLs, a new amendment G25 supersedes this one with the design lesson written into the next pre-registration.

Time budget: 4 hours.

---

## 5. Negative controls

Per `docs/marker_protocol.md` discipline, every G-amendment requires negative controls that *must fail* for the positive result to be defensible.

For G24:
- **R-18 gate 3** (white noise vs white noise, independent seeds, KL < 0.005) is the negative control for the new pathway. If two same-distribution inputs produce distinguishable bridge spectra, the amendment is over-fitting, not content-coupling.
- The legacy count-based path is itself a "control by construction" — running the same 50k smoke without `EQMOD_USE_ENERGY_WEIGHTED_FLUX=1` should reproduce R-16's KL = 0.000000. If the count-based path now produces non-zero KL, R-17 introduced a regression to the legacy path; voids G24.

R-18 implementation must run this legacy-control as part of the same session, and `tests/flux/test_g24_verification.py` includes a fourth test:

| # | Test | Pass condition |
|---|---|---|
| 4a | `tests/flux/test_g24_verification.py::test_legacy_count_based_path_still_returns_KL_zero` | Same 50k pair, but without the env var. KL between English-vs-white-noise spectra ≈ 0.0 (< 1e-6). Reproduces R-16. |

---

## 6. Time-budget commitments

| Item | Estimate | Hard ceiling |
|---|---|---|
| R-17 (implementation) | 2 h | 4 h |
| R-18 (50k smoke) | 1 h | 4 h |
| R-LR-9 (1.8M long-run, conditional on R-18 PASS) | 13 h | 24 h |

Per CLAUDE.md hybrid budget discipline: if any item overruns its hard ceiling, the postflight emits a written FAILED post-mortem in `LOGBOOK.md`. No silent extension.

---

## 7. What this amendment claims and what it does not claim

**It claims:** if R-18 passes, the substrate produces content-coupled topology under raw audio input at 50k-tick scope. That is the architectural-firewall fix R-13 and R-16 forensically identified the need for.

**It does not claim:**
- That the substrate now learns audio-meaningful structure. R-18 is a content-distinguishing test, not a learning test. Distinguishing English from white noise via bridge topology is weaker than learning phonetic structure.
- That R-LR-9 will pass. The 1.8M-tick run may show the 50k content-coupling collapses under noise accumulation, or the energy-weighted path may saturate. Those are real possibilities to be measured, not predicted away.
- That G24 supersedes any other planned amendment. R-LR-6 (activation field overlay, gated on R-12) and the G20–G23 text I/O chain (frozen 2026-05-11) are independent.

The honest framing: G24 is a one-paragraph fix to a documented spec-implementation mismatch that R-13/R-16 quantified. It is not a substrate breakthrough.
