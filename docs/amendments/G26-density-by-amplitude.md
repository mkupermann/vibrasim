# Amendment G26 — Density-by-amplitude injection

**Status: pre-registered, not yet implemented. Gated by `R-22` (combined implementation + 10k-tick verification).**
**Frozen: 2026-05-21. Author: Claude under user mandate 2026-05-19 + R-21 LOGBOOK self-recommendation 2026-05-21T11:50.**

If a future reader finds this file edited after R-22 has been run against it, that is a protocol violation and the run's verdict is void.

---

## 0. Why this exists

The iteration cap pre-registered in `LOGBOOK.md` 2026-05-20 ("if G24-G26 all NULL on content-coupling, pivot to G20-G23") has reached slot 3 of 3:

- **G24** (R-17b + R-18 + R-20): energy-weighted plasticity. Implementation passed; content-coupling NULL at 50k ticks (R-18: KL=0.000); diagnostic NULL at 10k (R-20: KL=0.005 < 0.01 threshold). The substrate's alive-quanta energy field is matched-RMS-determined — content variance in `abs(sample_value)` does not survive the buoyancy + decay dynamics.
- **G25** (R-21): content-driven xy-position. Implementation passed (deterministic, env-gated, legacy unchanged); content-coupling NULL at 10k ticks (KL=0.000215 < 0.1 threshold). The substrate dynamics low-pass-filter the per-sample position variation over the alive-quanta lifetime.

R-21 LOGBOOK 2026-05-21T11:50 explicitly analysed why both NULLs share a failure mode and proposed three G26 candidates. The recommended one is **density-by-amplitude**, on the grounds that count is a substrate-conserved quantity rather than a per-quantum channel, and is therefore not exposed to the mixing-time low-pass filter that washed G24's and G25's channels out.

Quoted from R-21 LOGBOOK:

> Reasoning: it puts content into a quantity (count) the substrate already uses as its primary observable, it avoids the high-bandwidth-channel-gets-low-pass-filtered failure mode G25 exhibits, and it is the only candidate whose effect cannot be averaged away by the binding/plasticity step (count is conserved by injection itself, before any dynamics).

G26 is the last amendment slot before the LOGBOOK 2026-05-20 pre-registered pivot to G20-G23 fires.

---

## 1. The change

### 1.1 N-quanta-per-sample injection

In `agent/flux/audio_raw.py`, `inject_raw_audio_sample` becomes env-var-gated to a density-by-amplitude variant:

```python
USE_DENSITY = os.environ.get("EQMOD_USE_DENSITY_BY_AMPLITUDE", "0") == "1"

if USE_DENSITY:
    n = int(np.clip(np.round(abs(sample_value) * DENSITY_K), 0, DENSITY_N_MAX))
    energy_per_quantum = abs(sample_value) / max(n, 1)
    for i in range(n):
        # ... inject one quantum with energy = energy_per_quantum,
        # ... position = position_hash(sample_index, ...) + tiny offset(i),
        # ... so the N quanta land near the same xy but at distinct sub-voxel
        # ... positions so they don't all stack on a single grid cell.
else:
    # legacy single-quantum injection (unchanged from R-13/R-14)
    ...
```

Where:
- `DENSITY_K = 4` is the linear scale (peak-amplitude samples inject 4 quanta).
- `DENSITY_N_MAX = 4` is the hard cap (prevents Quanta-buffer overflow on pathological inputs).
- `energy_per_quantum = abs(sample_value) / n` keeps the **total injected energy per sample** identical to the legacy case (so T1 conservation holds unchanged).

The result: at RMS=0.25 (the matched value used in R-16, R-18, R-20, R-21), mean `abs(sample_value)` ≈ 0.25, mean `n` ≈ `round(0.25 * 4)` = 1, so the substrate sees the legacy quantum-rate on average. But high-amplitude samples inject 2-4 quanta while silent samples inject 0. The **count distribution** is content-driven even though the per-sample RMS is matched between English and white noise.

### 1.2 What G26 does NOT change

- Legacy `inject_raw_audio_sample` path (without the env var) bit-identical to R-13/R-14.
- `position_hash` unchanged (legacy used for the offset base; sub-voxel jitter is RNG-derived).
- Energy total per sample unchanged: `energy_per_quantum * n = abs(sample_value)`.
- Plasticity rules, `count_flux_through`, bridge geometry, conservation/crystallization tests — all untouched.

### 1.3 Optional combinations are NOT enabled

`EQMOD_USE_ENERGY_WEIGHTED_FLUX=1` (G24) and `EQMOD_USE_CONTENT_DRIVEN_POSITION=1` (G25) remain available but are NOT auto-activated when G26 is set. R-22 verification runs G26 alone, so the architectural verdict is clean.

---

## 2. Why this design

### 2.1 Why density and not the other two G26 candidates

R-21 LOGBOOK §"Verdict for G26 design" listed three:

- **Density-by-amplitude** (this amendment). Count is conserved by injection — not subject to the binding/plasticity mixing.
- **Polarity-by-sign**. 1-bit/sample channel; lower bandwidth than position; but polarity is a substrate-primitive that directly drives binding via thermal-mass mismatch. Reserved as fallback if G26 NULLs.
- **Bridge-geometry redesign** (smaller `r_flux`, per-voxel histograms). Addresses the symptom (bridge tube integrates variance away) not the cause (substrate mixes everything). Last-resort.

Density is the only candidate whose content channel survives by construction independent of substrate dynamics. The amendment cap allows only one more slot, so the candidate with the highest a-priori survival probability is the defensible choice.

### 2.2 Why N_MAX = 4 and K = 4

- `K=4` means peak amplitudes inject 4 quanta. With samples_per_tick=16, peak-loud regions deliver up to 64 quanta/tick (vs 16 quanta/tick legacy). The Quanta buffer is sized at 8192 in encoder-free configs; 64/tick × 10000 ticks = 640000 inject attempts, but most quanta decay within a few hundred ticks under T4, so buffer pressure peaks at a few thousand. 4× headroom.
- `N_MAX=4` caps the hard ceiling. Even a pathological `abs(sample_value)=10.0` (which shouldn't occur after RMS normalization) injects at most 4 quanta. Buffer protection.
- The R-22 session is free to lower K if it sees evidence of buffer pressure, but **only before** the verification tests run, and the choice must be documented in the LOGBOOK entry. Per pre-registration, K cannot be tuned in response to a failing test verdict.

### 2.3 Pre-registered prediction

If G26 works, R-22 will show:

- alive-quanta count at tick 10_000 differs between English and matched-RMS white noise (KL on count histograms > 0.05, OR mean-count ratio outside [0.9, 1.1]).
- Bridge-formation count or bridge-spectrum KL between EN and WN > 0.01 (downstream propagation).
- T1 conservation holds (energy total per sample unchanged by construction).
- Same-audio different-seed negative control passes (counts similar across seeds).

If G26 NULLs on the count tests, the LOGBOOK 2026-05-20 pre-registered pivot fires: G24-G26 cap exhausted, switch to G20-G23 implementation on the legacy substrate.

---

## 3. Pre-registered acceptance — R-22

Locked, no retuning. R-22 is a single item combining implementation and 10k-tick verification (4-hour budget).

| # | Test | Pass condition |
|---|---|---|
| 1 | `tests/flux/test_g26_amendment.py::test_density_count_proportional_to_amplitude` | With `DENSITY_K=4`, `DENSITY_N_MAX=4`: `n(sample_value=0.0)=0`, `n(0.125)=1`, `n(0.4)=2`, `n(0.7)=3`, `n(1.0)=4`. Bit-deterministic count formula. |
| 2 | `tests/flux/test_g26_amendment.py::test_density_preserves_total_energy_per_sample` | With `sample_value=0.6`, density mode injects 2 quanta with `energy=0.3` each: sum = 0.6 = `abs(sample_value)`. T1 conservation by construction across all `n ≥ 1`. (For `n=0` no energy is injected — same as legacy zero-amplitude case.) |
| 3 | `tests/flux/test_g26_amendment.py::test_legacy_injection_unchanged` | Without `EQMOD_USE_DENSITY_BY_AMPLITUDE`, `inject_raw_audio_sample` returns 1 quantum at the legacy `position_hash` xy with `energy=abs(sample_value)` — bit-identical to four pinned R-13/R-14 fixtures. |
| 4 | `tests/flux/test_g26_amendment.py::test_env_var_routes_to_density_path` | With `EQMOD_USE_DENSITY_BY_AMPLITUDE=1`, `inject_raw_audio_sample` calls the density path (monkey-patch verifies count). |
| 5 | `tests/flux/test_g26_verification.py::test_10k_alive_quanta_count_differs_under_english_vs_whitenoise` | Two 10k-tick encoder-free substrates, identical seed, matched-RMS English vs white noise, both with `EQMOD_USE_DENSITY_BY_AMPLITUDE=1`. At tick 10000 the alive-quanta count histograms (32 bins on [0, max_count_observed]) differ by symmetric KL > 0.05. Threshold 0.05 is HALVED from R-20's 0.01-energy threshold deliberately: count is lower-bandwidth than energy (max 4 distinct values per sample vs continuous) but should preserve a much larger fraction of the variance through mixing. |
| 6 | `tests/flux/test_g26_verification.py::test_10k_alive_quanta_count_negative_control_same_audio_diff_seed` | Same English audio fed to two substrates with different RNG seeds; count-histogram KL < 0.01. Discriminator that the test-5 variance is content-driven not seed-driven. |
| 7 | `tests/flux/test_g26_verification.py::test_10k_bridge_count_differs_under_english_vs_whitenoise` | At tick 10000 of the test-5 substrates, total alive-bridge count differs by > 10% between EN and WN substrates, OR symmetric KL of bridge-weight spectra > 0.01. Either is acceptable; the OR captures that density may propagate to bridges via count (count-channel) or weight (spectrum-channel). |
| 8 | `tests/flux/test_conservation.py PASSES` | T1 robust. Energy-per-sample invariant verified by construction (test 2) AND by the conservation suite. |
| 9 | `tests/flux/test_crystallization_robustness.py PASSES` | T3 robust. |
| 10 | `tests/flux/test_audio_raw_injection.py PASSES` | Legacy injection tests (R-10/R-11) still green; the env-var-gated branch must not regress them. |
| 11 | LOGBOOK entry must record count-KL (test 5), neg-control-KL (test 6), bridge-count delta (test 7), and the empirically-observed peak Quanta-buffer fill from one of the verification runs. If all three primary content tests PASS, the entry must recommend R-LR-11 as next long-run for 1.8M-tick verification under G26 (this is the only G-amendment whose 10k pass would justify a long-run committment). |

R-22 PASS condition: tests 1-10 all pass. R-22 NULL on any of them maps as:

- Tests 1-4 fail → implementation bug. Fix and retry as R-22b.
- Test 5 fails (count KL < 0.05) → density-channel doesn't propagate to alive-quanta steady state. Same mixing-time problem as G24/G25 in a new guise. **G26 cap exhausted, pivot fires.**
- Test 6 fails (count KL ≥ 0.01 between same-audio seeds) → density formula over-fits to seed; mechanical bug. Fix and retry as R-22b.
- Test 7 fails (bridge response < 10% AND bridge-KL < 0.01) → content reaches alive-quanta count but bridge layer averages it away. This was R-21's secondary failure mode — points at bridge geometry. Notable but does not block: density succeeded at the alive-quanta level even if not at the bridge level.

Time budget: 4 hours. Iteration-cap accounting: G26 = slot 3 of 3.

---

## 4. Iteration cap finalisation

After R-22 NULL: pivot to G20-G23 implementation per LOGBOOK 2026-05-20 pre-registered decision. G20-G23 is the text I/O chain frozen 2026-05-11 in `docs/amendments/G20-G23.md` and is designed for the legacy substrate which already satisfies the "lernend" component of the success criterion (G14-G18 engrams, dreams, cross-modal recall — all PASSED under their own pre-registration). G20-G23 adds the symbolic-output layer that the success criterion's "kommunizierend" component requires.

After R-22 PASS: queue R-LR-11 (1.8M-tick verification under G26 path). Don't queue any further G-amendment in the iteration cap. The G24-G26 cap is finalised at three slots; the pre-registration was binding even if R-22 succeeds.
