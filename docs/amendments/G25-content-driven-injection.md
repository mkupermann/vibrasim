# Amendment G25 — Content-driven xy-position in audio injection

**Status: pre-registered, not yet implemented. Gated by `R-21` (implementation + 10k-tick verification combined).**
**Frozen: 2026-05-21. Author: Claude under user mandate 2026-05-19 "selbstbestimmt lernend kommunizierend" criterion + R-20 finding 2026-05-21T02:47.**

If a future reader finds this file edited after R-21 has been run against it, that is a protocol violation and the run's verdict is void.

---

## 0. Why this exists

R-20 (autopilot session 2026-05-21T02:47Z, branch `autopilot/R-20`, commit `35c6991`) returned NULL on the G24 energy-variance diagnostic. The locked measurements:

| # | Test | Threshold | Measured |
|---|---|---:|---:|
| 1 | `quanta.energy` histogram, English vs white noise (matched RMS) | KL > 0.01 | **0.005** |
| 2 | Same-audio negative control (different seed) | KL < 0.005 | **0.000015** |
| 3 | Per-bridge energy-flux, English vs white noise | KL > 0.01 | **0.000042** |

The R-20 LOGBOOK entry mapped this combination to branch (c) of the G24 pre-data correction record: "If test1 FAILS, energy itself does not vary across audio content beyond noise floor — upstream injection is the firewall — G25 must redesign `inject_raw_audio_sample` to make energy genuinely content-dependent or move content into another field (position, polarity)."

R-20 confirmed that content-signal does exist (test 2 was clean at 0.000015, two orders of magnitude under threshold), so the substrate IS reactive to audio content — but only by a factor that is 10× weaker than the locked R-20 threshold of 0.01. The energy-only path G24 introduced was not sufficient; the buoyancy-cleansed alive-quanta population at tick 10_000 represents the *expected* energy field which is matched between English and white noise by RMS construction.

G25 picks the cleanest path under branch (c): keep `quanta.energy = abs(sample_value)` unchanged, but move the audio content into the spatial coordinate too. `position_hash(sample_index, ...)` becomes content-aware: the same sample_index with different sample_value lands at a different xy position. Different audio → different spatial pattern of quanta → different bridge geometry → different bridge spectrum.

---

## 1. The change

### 1.1 New env-var-gated position function

In `agent/flux/audio_raw.py`, add a content-driven sibling to the existing `position_hash`:

```python
def position_hash_content_driven(
    sample_index: int, sample_value: float,
    Lx: float, Ly: float, voxel_size: float, *, seed: int = 0,
) -> tuple[float, float]:
    """Audio-content-dependent xy hash.

    Same total range as position_hash, same determinism: identical
    (sample_index, sample_value) reproduce identical xy. Differs from
    position_hash only in that sample_value enters the hash function,
    so two audio waveforms with matched RMS but different per-sample
    values produce different spatial distributions.

    Implementation: 64-bit splitmix on the bit-mixed combination of
    sample_index and a quantised sample_value (round to int16 to avoid
    float-precision instability under seed-replays).
    """
```

Existing `position_hash` is **unchanged** and stays the default. Legacy F1c/F2 tests that pin position_hash output stay green by construction.

### 1.2 Opt-in via env var in encoder-free injection

`agent/flux/audio_raw.py::inject_raw_audio_sample` gains:

```python
USE_CONTENT_DRIVEN_POSITION = os.environ.get(
    "EQMOD_USE_CONTENT_DRIVEN_POSITION", "0",
) == "1"

if USE_CONTENT_DRIVEN_POSITION:
    x, y = position_hash_content_driven(
        sample_index, sample_value, Lx, Ly, s, seed=position_hash_seed,
    )
else:
    x, y = position_hash(sample_index, Lx, Ly, s, seed=position_hash_seed)
```

Default is the legacy position. The new content-driven path is enabled only by explicit opt-in. R-LR-N items that don't set this env var continue to use the legacy injection.

### 1.3 What G25 does NOT change

- `position_hash` legacy stays as it is.
- `quanta.energy = abs(sample_value)` unchanged (G24's energy assignment remains; it's not the primary content channel anymore but it doesn't conflict).
- T1 conservation, T2 Bénard, T3 crystallization, T4 decay all stay on the count-based / legacy paths.
- `count_flux_through` + `apply_plasticity` (G24's energy-weighted variants too) all stay available — orthogonal to G25.

---

## 2. Why this design

### 2.1 Why position and not amplitude→density

Branch (c) of the G24 correction record listed two possible content channels: position, or polarity, or density-by-amplitude. G25 picks position because:

- It is the smallest change that puts content into a field the bridge geometry can actually distinguish (xy-spatial distribution determines which bridges form).
- Density-by-amplitude (more quanta per high-amplitude sample) introduces a quanta-budget management problem (the Quanta buffer can overflow on loud passages).
- Polarity-by-sign captures only one bit of content per sample and would still average out under matched RMS.

### 2.2 Why a separate function and not modifying position_hash

`position_hash` is pinned in 4 existing tests across F1b/F1c/F2 acceptance suites. Modifying it in place would void those tests' pre-registration (R-1, R-1b, R-2, R-3 all locked under the legacy position function). The opt-in design preserves the legacy envelope.

### 2.3 Pre-registered prediction (measured by R-21)

If G25 works, R-21 will show:

- 10k-tick spatial histogram of alive quanta positions: KL between English and matched-RMS white noise > **0.1** (10× stronger than R-20's failed 0.01 threshold, reflecting that position is a much higher-bandwidth content channel than energy).
- Same-audio different-seed: position KL < 0.005 (the same negative-control test R-20 passed).
- Bridge count or weight KL > 0.01 between EN and WN (downstream propagation of the position-channel content).
- T1 conservation: holds.
- T3 crystallization: holds.

If G25 does NOT work, R-21 NULLs and we're in the G25-of-3-amendment-slot territory of the pre-registered iteration cap. G26 would then be density-by-amplitude or polarity, with one more shot before the pivot to G20-G23 fires.

---

## 3. Pre-registered acceptance — R-21

Locked, no retuning. R-21 is a single item that combines implementation AND verification, because the implementation is small (one helper function + one env-gated branch) and the verification fits in the same 4-hour budget.

| # | Test | Pass condition |
|---|---|---|
| 1 | `tests/flux/test_g25_amendment.py::test_content_driven_position_hash_returns_different_xy_for_different_sample_values` | With sample_index=12345 fixed: position_hash_content_driven(12345, 0.1, ...) and position_hash_content_driven(12345, 0.8, ...) return xy coordinates whose Euclidean distance > 0.5 * voxel_size. |
| 2 | `tests/flux/test_g25_amendment.py::test_content_driven_position_hash_deterministic` | Same (sample_index, sample_value, seed) inputs return bit-identical xy. |
| 3 | `tests/flux/test_g25_amendment.py::test_legacy_position_hash_unchanged` | position_hash(12345, ...) returns the same xy it did in R-13/R-14 commits (numerical regression pinned by 4 fixture samples). |
| 4 | `tests/flux/test_g25_amendment.py::test_env_var_routes_to_content_driven_path` | With EQMOD_USE_CONTENT_DRIVEN_POSITION=1, inject_raw_audio_sample calls position_hash_content_driven, NOT position_hash. Verified via monkey-patch. |
| 5 | `tests/flux/test_g25_verification.py::test_10k_quanta_position_KL_above_0p1_english_vs_whitenoise` | Two 10k-tick encoder-free substrates, identical seed, matched-RMS English vs white noise, both with EQMOD_USE_CONTENT_DRIVEN_POSITION=1. 2D position histogram of alive quanta at tick 10000; symmetric KL > 0.1. Threshold chosen pre-data to be 10× stronger than R-20's failed energy-KL threshold because position is higher-bandwidth than amplitude. |
| 6 | `tests/flux/test_g25_verification.py::test_10k_negative_control_same_audio_different_seed_position_KL_below_0p005` | Same English audio fed to two substrates with different RNG seeds; position-histogram KL < 0.005. |
| 7 | `tests/flux/test_g25_verification.py::test_10k_bridge_count_differs_under_english_vs_whitenoise` | At tick 10000 of the test-5 substrates, KL between their bridge-weight spectra > 0.01 (downstream confirmation that the position-channel content reaches the bridge layer). |
| 8 | `tests/flux/test_conservation.py PASSES` | T1 robust. |
| 9 | `tests/flux/test_crystallization_robustness.py PASSES` | T3 robust. |
| 10 | LOGBOOK entry records position-KL (test 5), neg-control-KL (test 6), and bridge-spectrum-KL (test 7) explicitly. If all three pass, the entry must recommend R-LR-10 as next long-run item for 1.8M-tick verification under G25. |

R-21 PASS condition: tests 1–9 all pass. R-21 NULL on any of them maps as follows:
- Tests 1–4 fail → implementation bug. Fix and retry as R-21b.
- Test 5 fails (position KL < 0.1) → position-channel alone is not enough; G26 needs density or polarity in addition.
- Test 6 fails (position KL ≥ 0.005 between same-audio seeds) → position function over-fits to seed, the apparent content-coupling is artifact. Redesign.
- Test 7 fails → content reaches the position field but bridge layer averages it away. G26 = bridge-geometry redesign.

Time budget: 4 hours.

---

## 4. Iteration cap accounting

- G24 = slot 1 of 3 (implementation R-17b passed; verification R-18 + diagnostic R-20 both NULL).
- G25 = slot 2 of 3 (R-21 implementation + verification combined).
- G26 = slot 3 of 3, designed only if R-21 NULLs.

After G26 the LOGBOOK 2026-05-20 pre-registration says: pivot to G20–G23 (text I/O chain) on the legacy substrate.
