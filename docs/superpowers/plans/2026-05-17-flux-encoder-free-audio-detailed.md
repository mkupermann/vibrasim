# Flux Substrate — Encoder-Free Audio (Detailed Implementation Plan)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

> **Companion brief:** `docs/superpowers/plans/2026-05-16-flux-encoder-free-audio.md` (R-9 scope statement, scientific framing, hardware footprint). This file is the implementation plan referenced by that brief. R-9 produces this document; R-10 and R-11 implement against it.

**Goal.** Falsify the claim that the flux substrate can self-organise audio representations *without* a hand-engineered cochlea front-end. The F2 cochlea (R-3) and the R-8 training run remain the engineered baseline; this novel path removes the cochlea entirely and injects **one energy quantum per audio sample** directly into the substrate's hot floor. The substrate gets **no frequency information** — all injected quanta share a constant log-frequency `freq = log(SR/2)`. Any spectral structure (harmonics, formants, phonemes) the substrate develops must emerge from temporal correlations in the pulse-rate alone.

This plan locks the encoder-free injection rule and the two falsification gates (R-10 unit-level, R-11 training-run vs no-input control + R-8 cross-comparison). Acceptance thresholds are pre-registered here and not retunable per the autopilot charter (`.eqmod/autopilot/CHARTER.md` §"NULL is a valid verdict").

**Why this matters.** The cochlea encodes a strong inductive bias (log-spaced damped resonator bank → frequency-localised injection). If the substrate learns under R-8, it is unclear how much of the credit belongs to the substrate's plasticity versus how much was already in the cochlea's bank-tuning. Encoder-free removes that ambiguity. A PASS here is a strictly stronger claim than R-8. A NULL with a clean postmortem is also a finding: it documents that DSP-frontend engineering is load-bearing for substrate audio learning. Both outcomes are publishable; the encoder-free path is novel either way (no prior published work demonstrates raw-sample injection into a non-neural physics substrate — closest analogs are Wolfram Physics Project (no audio, no learning), Neural Cellular Automata (each cell is a learned MLP — still neural), Echo State Networks (engineered features in the reservoir input layer), and SNNs (explicit neuron primitives + STDP-like learning); the flux substrate is unusual on each axis simultaneously).

**Architecture sketch — what changes vs F2 and what doesn't.**

- **No new substrate physics.** No file under `world/flux/` changes. The plasticity, decay, binding, bridge, and thermal layers stay exactly as F1b/F1c/F2 left them. The encoder-free path is an *input adapter* only.
- **One new agent-layer module.** `agent/flux/audio_raw.py` exposes `inject_raw_audio_sample(quanta, grid, audio_samples, *, sample_rate_hz, position_hash_seed, rng)` and the higher-level `inject_raw_audio_chunk(...)` that consumes one tick's worth of audio at a time. It reuses `world/flux/boundary.py::inject_hot_floor` via its existing `freq_hz_override` kwarg with `freq_hz_override = SR / 2` (the Nyquist constant; the substrate's stored `freq` is then `log(SR/2) ≈ log(8000) ≈ 8.987` for SR=16 kHz). Position per sample is a deterministic hash of the sample index over the hot-floor xy plane (no random scatter per call — same input → same injection positions, reproducibility for negative-control matching).
- **No cochlea path active.** The F2 cochlea remains in code (R-8 baseline depends on it). The encoder-free path is a SEPARATE entry point. A run is either encoder-free OR cochlea, never both — selected by config flag, not by mutation of the cochlea module.
- **Same learning rule.** F3's spec-§5.5 monotone-flux bridge plasticity is the only learning rule in play. R-11 does not introduce a new rule; it tests whether THAT rule can extract structure from a raw-sample pulse stream with no inductive bias on the input side.
- **Audio I/O reused.** `agent/flux/audio_in.py::read_wav_mono_16k` and `iter_sample_chunks` from F2 are reused unchanged. The corpus is the R-7 English corpus on disk (no new fetch work).

**Tech stack:** Python 3.13, numpy, pytest. No new dependencies. No torch, no librosa, no scipy.signal (the encoder-free path is *cheaper* than F2 — it skips the resonator bank's Crank-Nicolson step entirely; per-tick cost is dominated by substrate physics).

**Spec reference:** `docs/superpowers/specs/2026-05-10-flux-substrate-design.md` — §3 (the single flux principle), §5.2 (vibration `frequency` is log-Hz), §5.5 (monotone-flux plasticity rule, unchanged), §5.6 (cochlea is FIXED — but encoder-free bypasses it entirely; the spec does not forbid additional input adapters). §4.8 (engineered ports are allowed; cochlea is one such port — raw-sample injection is a simpler port that delegates all transduction work to the substrate).

---

## Acceptance contract

### R-9 — this plan (current item)

Pre-registered in `.eqmod/autopilot/QUEUE.yaml::R-9`:

- `tests/test_research_plan_structure.py::test_encoder_free_plan_exists_and_well_formed` PASSES — NEW meta-test added by R-9 session. Verifies this file exists with: required structural headings (`Acceptance contract`, `File structure (locked decisions)`, `Open calibration choices`), at least one `## Task N` section, at least one `tests/flux/test_*.py` acceptance path, explicit negative-control paragraph, explicit comparison to the R-3/R-8 cochlea baseline, the locked energy-mapping rule (`energy = abs(sample)`), the no-frequency-information constraint (`freq = log(SR/2)`, constant), and SR=16000.
- Plan body explicitly commits to: `SR = 16000`, `freq = log(SR/2)` constant for every injected quantum, **one quantum per audio sample**, `energy = abs(sample)` (locked — see "Energy-mapping rule" below).
- Plan declares pytest acceptance paths: `tests/flux/test_audio_raw_injection.py` for R-10; `tests/flux/test_encoder_free_training_run.py` + `tests/flux/test_encoder_free_negative_control.py` for R-11.

### R-10 — encoder-free injector implementation

Pre-registered in `.eqmod/autopilot/QUEUE.yaml::R-10`:

- `tests/flux/test_audio_raw_injection.py::test_raw_injection_one_quantum_per_sample` PASSES — 0.1 s 1 kHz sine at SR=16 kHz → exactly 1600 quanta injected, all with `freq = log(SR/2) = log(8000)` (no scatter), energies tracking the rectified waveform (`|sin(2π·1000·t)|`).
- `tests/flux/test_audio_raw_injection.py::test_raw_injection_silence_injects_zero_energy` PASSES — 0.1 s silence → injected quanta carry energy ≈ 0 (within float epsilon). The injector does not skip silent samples (still 1 quantum per sample) — silent quanta carry zero energy. This keeps the one-quantum-per-sample invariant exact and makes the rate-modulation analysis in R-11 straightforward.
- `tests/flux/test_audio_raw_injection.py::test_raw_injection_amplitude_modulation_visible_in_substrate` PASSES — AM tone (1 kHz carrier, 10 Hz envelope) injected over ≥ 1 s → Pearson correlation between input envelope and substrate hot-floor energy density time-series ≥ 0.70 measured at 10 Hz envelope frequency.
- `tests/flux/test_conservation.py` PASSES — T1 still holds with the new injector active.
- `tests/flux/test_cochlea.py` PASSES — F2 baseline cochlea unmodified (R-8 baseline must survive R-10 changes intact).
- `tests/flux/test_synthesis.py` PASSES — F2 baseline synthesis unmodified.
- `pytest -m "not slow"` PASSES — legacy regression baseline.

### R-11 — encoder-free training run + falsification + R-8 cross-comparison

Pre-registered in `.eqmod/autopilot/QUEUE.yaml::R-11`:

- `tests/flux/test_encoder_free_training_run.py::test_encoder_free_substrate_distinguishable_from_no_input_control` PASSES — KL divergence of the encoder-free substrate's babble-MFCC histogram vs the no-input control's babble-MFCC histogram is > 2σ on 100-bootstrap. The substrate must have learned **something** from the raw audio that the no-input control cannot reproduce. Babble is generated by the F2 synthesis layer reading node firings from the trained substrate (cochlea-free training, synthesis-driven readout — synthesis serves as a passive probe here, not a learned decoder).
- `tests/flux/test_encoder_free_negative_control.py::test_no_input_control_produces_no_substrate_specific_signal` PASSES — matched-wallclock no-input substrate's babble is statistically indistinguishable from white-noise MFCC distribution (one-tailed KS-test p ≥ 0.05). Sanity check: the negative control is honest (it does not accidentally produce structure on its own).
- `docs/flux/phase-log.md` has an R-11 entry with both runs' bootstrap means + stds and the verdict comparison.
- `LOGBOOK.md` has the cross-comparison observation: tabulate KL divergences for cochlea-baseline (R-8) vs encoder-free (R-11). PASS verdict does NOT require encoder-free to beat the R-8 baseline; PASS requires the substrate-vs-no-input gate above. The R-8 comparison is a *measurement* of the gap, not a competitive threshold.

These pytest paths — `tests/flux/test_audio_raw_injection.py`, `tests/flux/test_encoder_free_training_run.py`, `tests/flux/test_encoder_free_negative_control.py` — are the pre-registered R-10 / R-11 acceptance targets. The autopilot charter forbids retuning them post-hoc.

---

## Energy-mapping rule (locked)

The pre-registered choice is **`energy = abs(sample)`**, not `sample²`.

**Why locked to `abs(sample)`:**

1. **Acceptance language alignment.** The R-10 acceptance text states "energies tracking the rectified waveform" — `|sample|` IS the rectified waveform; `sample²` is the half-wave-rectified squared waveform. The test as pre-registered in QUEUE.yaml R-10 reads naturally with `abs`.
2. **Linear amplitude tracking.** A 6 dB amplitude increase doubles `|sample|` but quadruples `sample²`. For substrate plasticity, where the bridge-strengthen rate `γ · flux_through(t)` is linear in flux, a linear amplitude→energy mapping keeps the gradient predictable. Quadratic mapping would compress quiet phonemes and saturate loud ones — a non-trivial nonlinearity that would interfere with the "did the substrate learn?" question.
3. **Conservation accounting.** The auditor records `energy_per * count_injected` per `audit.record_injection` call. With one quantum per sample, the per-tick energy budget is the per-tick `sum(|sample|)`, which is the standard L1 norm — easy to compare against the cochlea path's per-tick injected energy for the R-8-vs-R-11 cross-comparison.
4. **No physical "intensity" claim.** The substrate is not a sound-pressure-to-intensity transducer; the energy quantum is an abstract substrate flux unit. There is no physical principle that mandates `sample²` here. The choice is calibration; locking it to `abs` keeps the linearity intact.

Floating-point silence injects exactly zero energy (`abs(0.0) == 0.0`). The "energy ≈ 0 within float epsilon" wording in R-10's silence test is to accommodate accumulated rounding in the wav-decode path, not to permit a non-zero floor in the mapping itself.

This choice is **frozen** for the duration of R-10 and R-11. Any future variant (e.g. `sample²`, `log(1 + |sample|)`, ramped mappings) requires a new G/R-numbered amendment and a separate plan file. No mid-session retuning.

---

## No-frequency-information constraint (locked)

**Every injected quantum gets `freq = log(SR/2)`.** With `SR = 16000`, this is `log(8000) ≈ 8.987` in the substrate's log-Hz convention (spec §5.2).

**Why this specific constant:**

- It is the Nyquist frequency for SR=16000 — the upper bound of representable frequencies in the audio signal. Putting every quantum there means no "favoured" frequency band is encoded into the substrate's state vector.
- It is well above the cochlea bank's response window (50 Hz – 8 kHz). Cross-comparison with R-8 (cochlea-baseline) is clean: R-8 distributes energy across the bank's log-spaced frequencies; R-11 puts all energy at the Nyquist. Any spectral structure in the encoder-free substrate must come from temporal correlations in the pulse rate, not from the substrate inheriting cochlea-bank structure.
- It is a single locked constant — not a per-sample distribution. The substrate has zero a-priori spectral information.

**What the substrate is NOT given:**

- The audio sample's frequency content (no FFT, no cochlea, no spectrogram).
- A per-sample randomised frequency (which would inject a flat noise floor across log-Hz).
- Multiple "channels" with different freqs (the cochlea is the only multi-frequency input adapter; encoder-free is single-frequency by construction).

The substrate has exactly one degree of freedom on the input side: the *count* of quanta injected per sample window, modulated by `abs(sample)`. Spectral structure, if it emerges, must come from substrate dynamics applied to that time-varying scalar pulse stream alone.

This constraint is **frozen** for R-10 and R-11. Per-quantum frequency jitter (even small) is forbidden — it would inject a frequency prior the substrate could exploit. Cross-sample frequency variation is forbidden for the same reason.

---

## Comparison to R-3/R-8 cochlea baseline

The encoder-free path runs in parallel to the R-3/R-8 cochlea baseline, not in place of it. Both paths must remain intact:

| Concern | R-3/R-8 cochlea baseline | R-11 encoder-free |
|---|---|---|
| Input transducer | 64-channel log-spaced damped-resonator bank (`agent/flux/cochlea.py`) | None — direct sample-to-quantum injection (`agent/flux/audio_raw.py`) |
| Per-sample cost | ~128 FLOPs (resonator bank Crank-Nicolson step) | ~0 FLOPs (one buffer add) |
| Quanta per audio second | ≤ N_resonators × cap × tick_rate ≈ 64 × 8 × 1000 = 512000 | exactly SR = 16000 |
| Frequency information available to substrate | log-spaced 64-channel routing | None — single constant `freq = log(SR/2)` |
| Training rule | F3 spec-§5.5 monotone-flux plasticity | F3 spec-§5.5 monotone-flux plasticity (SAME rule, different input adapter) |
| Acceptance test for the trained substrate | `tests/flux/test_training_run.py` (R-8) | `tests/flux/test_encoder_free_training_run.py` (R-11) |

**Cross-comparison observation (REQUIRED in R-11's LOGBOOK entry, not a verdict threshold):**

```
R-8 cochlea-baseline KL(trained_babble || no_input_babble)     = <measured> ± <bootstrap_std>
R-11 encoder-free  KL(trained_babble || no_input_babble)       = <measured> ± <bootstrap_std>
gap = R-11 − R-8                                                = <measured>
```

The gap will be either positive (encoder-free outperforms, indicating the cochlea was redundant or noise-injecting), zero within bootstrap error (encoder-free matches, indicating the substrate did the spectral work in either case), or negative (encoder-free underperforms, indicating DSP-frontend engineering is load-bearing for substrate audio learning). All three outcomes are findings. The measurement of the gap is the deliverable, not a particular sign.

**What is NOT a competitive threshold:** R-11's PASS does not require encoder-free to match or beat R-8. The PASS condition is only `KL(encoder_free || no_input) > 2σ`. The R-8 baseline column in the LOGBOOK table is observational, per the autopilot charter's "NULL is a valid verdict" principle. The gap's sign is the science; pre-judging it would be a protocol breach.

---

## Negative control (explicit pre-registration)

The matched-wallclock no-input negative control is required by `.eqmod/autopilot/CHARTER.md` §"Negative controls are required" because R-11's acceptance reads the substrate's emergent state (node firings → synthesis-side MFCC histogram).

**Negative control definition (locked):**

- **Same everything as the trained encoder-free run** — same grid, same `BindingConfig`, same `PlasticityConfig`, same `DecayConfig`, same `ThermalConfig`, same `n_ticks_train`, same RNG seed for substrate physics (`seed = 4242` per R-5 convention).
- **One difference: no input.** The encoder-free injector is replaced by a no-op for the entire `n_ticks_train` ticks. The hot-floor receives zero quanta from the audio side. Background thermal/buoyancy still operate as F1c configured them.
- **Same readout.** F2 synthesis layer reads node firings exactly as in the trained run, producing a babble waveform of the same duration. MFCC histogram is computed identically.

**Negative control sanity check (test `test_no_input_control_produces_no_substrate_specific_signal`):**

- Compares the no-input control's babble-MFCC histogram against a white-noise reference MFCC distribution (white noise of the same duration, same wav-write path).
- One-tailed KS test: p ≥ 0.05 means the control's babble is indistinguishable from white noise → the control is honest (it has not accidentally developed structure from background thermal flux alone).
- If the control develops substrate-specific structure WITHOUT input, the test must FAIL — that would indicate the substrate's emergent metric is contaminated by background dynamics, and any trained-substrate result becomes meaningless.

**Why this matters per charter:** "A PASS that has no negative control is a state detector, not a finding. Treat it as NULL." The two-gate design (trained > 2σ above no-input control AND no-input control ≈ white noise) makes both gates necessary. Single-gate designs (trained > control alone) are vulnerable to the failure mode where control drifts low for unrelated reasons and trained "looks high" in comparison.

---

## File structure (locked decisions)

### R-9 creates (this session, in this commit)

| Path | Responsibility |
|---|---|
| `docs/superpowers/plans/2026-05-17-flux-encoder-free-audio-detailed.md` | THIS plan file. |
| `tests/test_research_plan_structure.py` (modified) | Adds `test_encoder_free_plan_exists_and_well_formed` meta-test. Mirrors the F2/F3/training-EN pattern: marked `slow`, run on demand by postflight as R-9's verdict criterion. |

### R-10 creates

| Path | Responsibility |
|---|---|
| `agent/flux/audio_raw.py` | NEW module. `inject_raw_audio_sample(quanta, grid, sample_value, sample_index, *, sample_rate_hz=16000, rng) -> int` injects exactly 1 quantum per call with `energy = abs(sample_value)`, `freq = log(sample_rate_hz / 2)`, deterministic position via `position_hash(sample_index)`. Plus `inject_raw_audio_chunk(quanta, grid, chunk_samples, base_sample_index, *, sample_rate_hz=16000, rng) -> int` that calls the per-sample function in a loop and returns total quanta injected. Plus `position_hash(sample_index, Lx, Ly, voxel_size) -> (x, y)` pure function for testable determinism. |
| `tests/flux/test_audio_raw_injection.py` | The three R-10 acceptance tests + at least one determinism/hash unit test. |

### R-10 modifies

| Path | What changes |
|---|---|
| `agent/flux/__init__.py` | Re-export `inject_raw_audio_sample`, `inject_raw_audio_chunk`, `position_hash`. |
| `docs/flux/phase-log.md` | R-10 entry: scope, calibration record, final test counts. |

### R-10 must NOT modify

- `agent/flux/cochlea.py` (R-8 baseline depends on it being identical).
- `agent/flux/synthesis.py` (R-11 reuses it as a passive readout).
- `world/flux/*` (no substrate physics changes — encoder-free is input-adapter only).
- `docs/marker_protocol.md`, `docs/marker_protocol_G20-G23_addendum.md` (frozen by charter).
- `.eqmod/autopilot/QUEUE.yaml` `preregistered_acceptance:` block of R-10 (locked at in_progress).

### R-11 creates

| Path | Responsibility |
|---|---|
| `tests/flux/test_encoder_free_training_run.py` | R-11's primary acceptance: trained encoder-free substrate vs no-input control, 100-bootstrap KL > 2σ. |
| `tests/flux/test_encoder_free_negative_control.py` | R-11's secondary acceptance: no-input control babble ≈ white-noise MFCC (KS p ≥ 0.05). |
| `agent/flux/encoder_free_training.py` | Driver: orchestrates a training run consuming the R-7 corpus via `inject_raw_audio_chunk`, ticks the substrate for `n_ticks_train`, reads synthesis-side babble, computes MFCC histograms. Counterpart to F3's `agent/flux/learning_run.py` but on the encoder-free path. |

### R-11 reads (does NOT modify)

- `agent/flux/cochlea.py`, `agent/flux/synthesis.py` — used for R-8 baseline cross-comparison data ingest only.
- The R-7 corpus on disk at `~/.eqmod/training/EN/` (manifest at `~/.eqmod/training/EN/manifest.json`).

### R-11 modifies

| Path | What changes |
|---|---|
| `docs/flux/phase-log.md` | R-11 closing entry with bootstrap means + stds + verdict. |
| `LOGBOOK.md` | Cross-comparison observation table (R-8 vs R-11 KL divergences). |

No edits anywhere outside `agent/flux/`, `tests/flux/`, `tests/`, `docs/flux/phase-log.md`, `docs/superpowers/plans/`, `LOGBOOK.md`. Branch-name pattern is `autopilot/R-10` and `autopilot/R-11` per the autopilot charter.

---

## Open calibration choices (locked here — no per-run retuning)

| Param | Value | Locked? | Purpose |
|---|---|---|---|
| `SR` | `16000` | LOCKED | Audio sample rate (matches F2). Cross-comparison parity with R-8 requires identical SR. |
| `freq` (every quantum) | `log(SR/2) ≈ 8.987` | LOCKED | No-frequency-information constraint. |
| `energy(sample)` | `abs(sample)` | LOCKED | Energy-mapping rule. See "Energy-mapping rule" section above. |
| Quanta per audio second | `SR = 16000` | LOCKED | Exactly one quantum per sample. |
| Substrate dims | `80 × 40 × 10` voxels | LOCKED | R-1-calibrated; T2 known fragile but T1/T3/T4 robust. Same as R-8 baseline for cross-comparison parity. |
| Run duration (R-11) | `30 min wall-clock` per training stage | LOCKED for R-11 v1 | Vacation time budget; if R-11 PASS at 30 min, extension is post-vacation. |
| Corpus (R-11) | Reuse R-7 English Stage 1 audiobook + Stage 4 substitute | LOCKED | Cross-comparison parity with R-8. |
| `max_quanta` | `500_000` | LOCKED | 16 kHz × 30 min = 28.8M injections — damping must keep alive population bounded. Peak alive recorded in phase-log. |
| Bootstrap N (R-11) | `100` | LOCKED | Matches F2 evaluator default. |
| `n_ticks_train` (R-11) | derived from 30 min wall-clock at substrate tick rate (~1 kHz) → ~1.8M ticks | LOCKED upper bound: 2M ticks | Above 2M is a charter breach. |
| `seed` (R-11 substrate) | `4242` | LOCKED | Matches R-5 convention. |
| `seed` (R-11 no-input control) | `4242` (same) | LOCKED | Matched-everything-but-input control per charter. |
| `position_hash_seed` | `0` | LOCKED for R-10 v1 | Deterministic per-sample-index position; same seed across trained and control runs. |

**Calibration discipline.** Unlike F3 (which permits up to 5 calibration sweeps within pre-registered ranges), this plan **does not authorise sweeps**. Every value above is frozen. If R-10 or R-11 fails to meet acceptance with these values, the verdict is NULL with a postmortem, per the autopilot charter. No mid-session calibration is permitted because:

1. The acceptance test for R-10 (Pearson r ≥ 0.7 between input envelope and substrate floor energy) is a property of the injection rule, not a tuning target. If it fails, the injection rule itself is wrong.
2. The R-11 acceptance (KL > 2σ) is a property of substrate emergence under the locked rule. The point of pre-registration is exactly that no knob can be turned to rescue it.

If a parameter needs to change, a new R-numbered amendment is required, with a fresh plan and a fresh acceptance contract.

---

## Task 1: R-9 — write this plan and its meta-test

**Files:**
- Create: `docs/superpowers/plans/2026-05-17-flux-encoder-free-audio-detailed.md` (this file)
- Modify: `tests/test_research_plan_structure.py` (add the meta-test)

- [x] **Step 1: Write this plan** with the locked decisions above. (Done — this document.)
- [x] **Step 2: Add `test_encoder_free_plan_exists_and_well_formed`** to `tests/test_research_plan_structure.py`. Pattern mirrors `test_F2_plan_exists_and_well_formed` and `test_F3_plan_exists_and_well_formed`: glob for `*-flux-encoder-free-audio-detailed.md`, run `_assert_structure`, then check additional encoder-free invariants (energy rule, no-frequency-information constraint, R-10/R-11 pytest path declarations, negative control paragraph, R-3 baseline comparison).
- [x] **Step 3: Run** `pytest tests/test_research_plan_structure.py::test_encoder_free_plan_exists_and_well_formed -v`. Expect PASS.
- [x] **Step 4: Run** `pytest -m "not slow"`. Expect the regression baseline to be unaffected by the new (slow-marked) meta-test.
- [x] **Step 5: Commit** on branch `autopilot/R-9`: `flux R-9: encoder-free detailed plan + meta-test`. Postflight script pushes.

---

## Task 2 (R-10): position_hash + per-sample injector — pure functions

**Files:**
- Create: `agent/flux/audio_raw.py` (Step 1 only — chunk-level injector lands in Task 3)
- Create: `tests/flux/test_audio_raw_injection.py` (per-sample section only)

- [ ] **Step 1: Tests first.**

```python
"""Tests for encoder-free audio injection — R-10."""
from __future__ import annotations
import numpy as np
import pytest

from agent.flux.audio_raw import (
    inject_raw_audio_sample, inject_raw_audio_chunk, position_hash,
)
from world.flux.quantum import Quanta
from world.flux.grid import Grid


def test_position_hash_is_deterministic():
    grid = Grid(dims=(80, 40, 10), voxel_size=1.0)
    p1 = position_hash(sample_index=12345, Lx=80, Ly=40, voxel_size=1.0)
    p2 = position_hash(sample_index=12345, Lx=80, Ly=40, voxel_size=1.0)
    assert p1 == p2, "position_hash must be deterministic"


def test_position_hash_covers_floor_plane():
    """Many sample indices → positions cover both x and y axes."""
    xs, ys = [], []
    for i in range(1000):
        x, y = position_hash(sample_index=i, Lx=80, Ly=40, voxel_size=1.0)
        xs.append(x)
        ys.append(y)
    assert min(xs) < 5.0 and max(xs) > 75.0
    assert min(ys) < 5.0 and max(ys) > 35.0
```

- [ ] **Step 2: Implement** `agent/flux/audio_raw.py` with:
  - `position_hash(sample_index, Lx, Ly, voxel_size) -> tuple[float, float]` — deterministic xy on the hot-floor plane via a stable hash (e.g. SplitMix64 of `(sample_index, position_hash_seed)`, mapped to `[0, Lx*voxel_size)` and `[0, Ly*voxel_size)`).
  - `inject_raw_audio_sample(quanta, grid, sample_value, sample_index, *, sample_rate_hz=16000, rng) -> int` — calls `Quanta.add` directly (NOT through `inject_hot_floor`, to keep position deterministic per sample_index — `inject_hot_floor` uses random xy). Returns 1 on success, 0 if buffer full.
  - `inject_raw_audio_chunk(quanta, grid, chunk_samples, base_sample_index, *, sample_rate_hz=16000, rng) -> int` — loop over samples, call per-sample, return total injected.

- [ ] **Step 3: Run** `pytest tests/flux/test_audio_raw_injection.py -v -k hash`. Expect 2/2 pass.

- [ ] **Step 4: Commit** `flux R-10 task 2: position_hash + per-sample injector`.

---

## Task 3 (R-10): one-quantum-per-sample invariant

**Files:**
- Modify: `tests/flux/test_audio_raw_injection.py` (add the invariant tests)

- [ ] **Step 1: Tests.**

```python
def test_raw_injection_one_quantum_per_sample():
    """0.1 s 1 kHz sine @ 16 kHz → exactly 1600 quanta, all freq=log(SR/2),
    energies tracking rectified waveform."""
    SR = 16000
    n = SR // 10  # 0.1 s = 1600 samples
    t = np.arange(n) / SR
    waveform = np.sin(2 * np.pi * 1000.0 * t)
    grid = Grid(dims=(80, 40, 10), voxel_size=1.0)
    q = Quanta(max_quanta=10_000)
    rng = np.random.default_rng(0)
    injected = inject_raw_audio_chunk(
        q, grid, waveform, base_sample_index=0, sample_rate_hz=SR, rng=rng,
    )
    assert injected == 1600
    alive = q.alive
    assert int(alive.sum()) == 1600
    # all freq = log(SR/2)
    expected_freq = float(np.log(SR / 2))
    assert np.allclose(q.freq[alive], expected_freq), (
        "encoder-free quanta must all carry freq=log(SR/2) (no scatter)"
    )
    # energies = |sample|; reconstruct rectified waveform
    energies = q.energy[alive]
    # quanta were injected in sample-index order so energies[i] ≈ |waveform[i]|
    assert np.allclose(energies, np.abs(waveform), atol=1e-7)


def test_raw_injection_silence_injects_zero_energy():
    """0.1 s of silence still injects 1600 quanta, each with energy ≈ 0."""
    SR = 16000
    n = SR // 10
    silence = np.zeros(n, dtype=np.float64)
    grid = Grid(dims=(80, 40, 10), voxel_size=1.0)
    q = Quanta(max_quanta=10_000)
    rng = np.random.default_rng(0)
    injected = inject_raw_audio_chunk(
        q, grid, silence, base_sample_index=0, sample_rate_hz=SR, rng=rng,
    )
    assert injected == 1600
    alive = q.alive
    assert np.max(np.abs(q.energy[alive])) < 1e-12
```

- [ ] **Step 2: Run** `pytest tests/flux/test_audio_raw_injection.py -v`. Expect 4/4 pass (hash + invariant tests).

- [ ] **Step 3: Commit** `flux R-10 task 3: one-quantum-per-sample invariant`.

---

## Task 4 (R-10): amplitude-modulation-visible-in-substrate

**Files:**
- Modify: `tests/flux/test_audio_raw_injection.py` (add the AM test)

The AM test wires the encoder-free injector into the substrate's tick loop and measures whether the input envelope is visible in the substrate's hot-floor energy density time-series. Pearson r ≥ 0.7 at the envelope frequency.

- [ ] **Step 1: Test.**

```python
def test_raw_injection_amplitude_modulation_visible_in_substrate():
    """AM tone (1 kHz carrier, 10 Hz envelope) → Pearson r ≥ 0.7
    between input envelope and substrate floor energy density."""
    from world.flux.dynamics import tick
    from world.flux.grid import Grid
    from world.flux.quantum import Quanta
    from scipy.stats import pearsonr  # if scipy available; else manual
    SR = 16000
    duration_s = 1.0
    n = int(SR * duration_s)
    t = np.arange(n) / SR
    carrier = np.sin(2 * np.pi * 1000.0 * t)
    envelope = 0.5 * (1.0 + np.cos(2 * np.pi * 10.0 * t))
    waveform = envelope * carrier

    grid = Grid(dims=(80, 40, 10), voxel_size=1.0)
    q = Quanta(max_quanta=500_000)
    rng = np.random.default_rng(0)

    chunk = 16  # one substrate tick = 16 audio samples = 1 kHz tick rate
    energy_per_tick = []
    for tick_idx in range(n // chunk):
        s0 = tick_idx * chunk
        buf = waveform[s0:s0 + chunk]
        inject_raw_audio_chunk(
            q, grid, buf, base_sample_index=s0, sample_rate_hz=SR, rng=rng,
        )
        # substrate physics — minimal config for this test (no binding)
        tick(q, grid, rng=rng)  # default tick, no extras
        e = float(q.energy[q.alive & (q.pos[:, 2] < 2.0)].sum())
        energy_per_tick.append(e)
    energy_per_tick = np.array(energy_per_tick)
    # decimate envelope to the same length
    env_decimated = envelope[::chunk][:len(energy_per_tick)]
    r, _ = pearsonr(env_decimated, energy_per_tick)
    assert r >= 0.7, f"AM envelope not visible: r={r:.3f}, expected ≥ 0.7"
```

- [ ] **Step 2: Run** `pytest tests/flux/test_audio_raw_injection.py -v`. Expect 5/5 pass.

- [ ] **Step 3: Verify regression.** `pytest -m "not slow"` PASSES; `pytest tests/flux/test_cochlea.py tests/flux/test_synthesis.py tests/flux/test_conservation.py -v` PASSES (F2 baseline untouched).

- [ ] **Step 4: Commit** `flux R-10 task 4: amplitude modulation visible in substrate`.

---

## Task 5 (R-10): close — re-exports + phase-log

**Files:**
- Modify: `agent/flux/__init__.py`
- Modify: `docs/flux/phase-log.md`

- [ ] **Step 1: Re-export** `inject_raw_audio_sample`, `inject_raw_audio_chunk`, `position_hash` in `agent/flux/__init__.py`.
- [ ] **Step 2: Phase-log R-10-close entry**: test counts, alive-quanta peak across tasks, any surprises.
- [ ] **Step 3: Run** the full R-10 acceptance suite one more time, plus `pytest -m "not slow"`. Commit only if both clean.
- [ ] **Step 4: Commit** `flux R-10 complete: re-exports + phase-log`.

---

## Task 6 (R-11): training-run driver

**Files:**
- Create: `agent/flux/encoder_free_training.py`

The driver mirrors F3's `learning_run.py` but on the encoder-free path. It takes a `EncoderFreeTrainingConfig`, reads R-7 corpus chunks, calls `inject_raw_audio_chunk` per substrate tick, ticks the substrate with binding/plasticity/decay active, periodically samples the synthesis-side babble for MFCC histogram, returns the result.

- [ ] **Step 1: Implement** `EncoderFreeTrainingConfig` (locked defaults from "Open calibration choices" table above) and `run_encoder_free_training(cfg, input_kind: Literal["audio","no_input"]) -> EncoderFreeTrainingResult`. Result carries `babble_samples`, `mfcc_histogram`, `n_ticks`, `wallclock_s`.
- [ ] **Step 2: Smoke test** the driver with `n_ticks=1000` (not the full 1.8M) to check the orchestration. No acceptance assertion yet — that lives in Tasks 7 + 8.
- [ ] **Step 3: Commit** `flux R-11 task 6: encoder-free training driver`.

---

## Task 7 (R-11): trained-vs-no-input acceptance test

**Files:**
- Create: `tests/flux/test_encoder_free_training_run.py`

- [ ] **Step 1: Test.**

```python
def test_encoder_free_substrate_distinguishable_from_no_input_control():
    """Trained encoder-free substrate babble-MFCC histogram differs from
    matched-wallclock no-input control by KL > 2σ on 100-bootstrap."""
    from agent.flux.encoder_free_training import (
        EncoderFreeTrainingConfig, run_encoder_free_training,
    )
    cfg = EncoderFreeTrainingConfig()  # uses locked defaults
    trained = run_encoder_free_training(cfg, input_kind="audio")
    control = run_encoder_free_training(cfg, input_kind="no_input")
    # KL with bootstrap
    kl_samples = []
    for _ in range(100):
        kl_samples.append(bootstrap_kl(trained.mfcc_histogram, control.mfcc_histogram))
    kl_mean = float(np.mean(kl_samples))
    kl_std = float(np.std(kl_samples))
    # 2σ from zero
    assert kl_mean > 2.0 * kl_std, (
        f"encoder-free substrate not distinguishable from no-input: "
        f"KL={kl_mean:.4f} ± {kl_std:.4f}"
    )
```

- [ ] **Step 2: Run.** Expect PASS or NULL (with postmortem) — no retuning.
- [ ] **Step 3: Phase-log R-11 entry** with measured KL ± σ for both runs.
- [ ] **Step 4: Commit** `flux R-11 task 7: trained-vs-no-input acceptance`.

---

## Task 8 (R-11): negative-control sanity test

**Files:**
- Create: `tests/flux/test_encoder_free_negative_control.py`

- [ ] **Step 1: Test.**

```python
def test_no_input_control_produces_no_substrate_specific_signal():
    """No-input control's babble-MFCC histogram statistically
    indistinguishable from white-noise MFCC distribution (KS p ≥ 0.05)."""
    from scipy.stats import ks_2samp
    from agent.flux.encoder_free_training import (
        EncoderFreeTrainingConfig, run_encoder_free_training,
        mfcc_of_white_noise,
    )
    cfg = EncoderFreeTrainingConfig()
    control = run_encoder_free_training(cfg, input_kind="no_input")
    wn_mfcc = mfcc_of_white_noise(
        duration_s=control.babble_duration_s,
        sample_rate_hz=cfg.sample_rate_hz,
        seed=9999,
    )
    # one-tailed KS — H0: same distribution
    _, p = ks_2samp(control.mfcc_histogram, wn_mfcc)
    assert p >= 0.05, (
        f"no-input control produced substrate-specific signal "
        f"(KS p={p:.4f}, expected ≥ 0.05) — control is not honest, "
        f"any trained-substrate result becomes meaningless"
    )
```

- [ ] **Step 2: Run.** Expect PASS.
- [ ] **Step 3: Commit** `flux R-11 task 8: negative-control sanity`.

---

## Task 9 (R-11): close — phase-log + LOGBOOK cross-comparison

**Files:**
- Modify: `docs/flux/phase-log.md`
- Modify: `LOGBOOK.md`

- [ ] **Step 1: Phase-log R-11-close**: bootstrap means + stds for both runs, verdict comparison.
- [ ] **Step 2: LOGBOOK cross-comparison table** — R-8 vs R-11 KL divergences, gap, interpretation paragraph per autopilot charter §"NULL is a valid verdict". The interpretation must state whether the gap is in the implementation, in the hypothesis, or in the acceptance specification — not a deflection.
- [ ] **Step 3: Commit** `flux R-11 complete: phase-log + LOGBOOK cross-comparison`.

---

## Notes for autonomous execution

- **Charter discipline.** No edits to `docs/marker_protocol.md`, `docs/marker_protocol_G20-G23_addendum.md`, or the `preregistered_acceptance:` block of any QUEUE item once it transitions to `in_progress`. Per `.eqmod/autopilot/CHARTER.md` §"Hard prohibitions".
- **Negative control discipline.** R-11 will not be considered PASS without `test_encoder_free_negative_control.py` PASSING. A PASS on the trained-vs-no-input gate alone is NULL per charter (state detector, not finding).
- **No calibration sweeps.** Unlike F3 (which permits 5 sweeps), this plan freezes every parameter. If a test fails with the locked values, the verdict is NULL — write the postmortem and move on. The point of pre-registration is that no knob is turned post-hoc.
- **One quantum per sample — exact, not approximate.** The R-10 invariant test `test_raw_injection_one_quantum_per_sample` asserts exactly 1600 quanta for 1600 input samples. Buffer-full early-exit is a fail-shut FAIL — `max_quanta=500_000` must be sized to hold every injection over the test window (`max_quanta` for R-10 unit tests can be 10_000; R-11 needs the full 500_000 with damping active).
- **Determinism matters for matched-control.** R-11's no-input control must use the SAME RNG seed as the trained run. The encoder-free injector's `position_hash` is deterministic so trained and control inject at identical floor positions (modulo trained injecting and control not injecting at all). Same seed + same dynamics + same readout = matched control.
- **F2 cochlea untouched.** Repeat: do not modify `agent/flux/cochlea.py`. R-8 cross-comparison data depends on the cochlea being byte-identical to the R-3 implementation.
- **Synthesis as passive probe.** F2 synthesis is reused as a readout for R-11. It is not retrained, retuned, or wrapped. The substrate produces node firings; synthesis converts them to a waveform; MFCC over that waveform is the metric. Any "improvement" to synthesis would contaminate the substrate-vs-no-input gate.
- **Compute footprint.** Per-tick cost is the same as R-8 minus the cochlea bank's Crank-Nicolson step (≈ 128 FLOPs saved per tick). Encoder-free is *cheaper* per tick than F2. The 30 min wall-clock training stage at substrate tick rate ≈ 1 kHz fits in the autopilot's 4 h per-session cap.
- **Hardware.** User's existing Mac (Apple Silicon M-series, Python 3.13, .venv at repo root). No GPU. No cluster. Single-threaded numpy + numba-JIT physics tick. Replicable by `git clone && pip install -e .[dev,dashboard,agent] && python -m agent.run_autonomous --config corpus.training-EN.yaml --raw-injection`.
