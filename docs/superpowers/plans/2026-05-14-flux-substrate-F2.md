# Flux Substrate F2 — Cochlea + Synthesis + First Audio Input

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Bolt the audio I/O onto the validated F0–F1c flux substrate. A 1 kHz tone burst fed into the cochlea (§5.6) injects vibrations at the hot floor whose `frequency` property tracks the input spectrum. The substrate's existing dynamics (move + buoyancy + binding + bridges + plasticity + decay) continue to run untouched. The synthesis layer (§5.7) reads bound-node firings and excites the same resonator bank in reverse to produce an output waveform. F2 closes when:

- a 1 kHz tone burst through cochlea → a measurable peak near 1 kHz in the injected vibrations' frequency distribution (`tests/flux/test_cochlea.py`)
- a forced firing pattern of synthesised nodes at 1 kHz → an output waveform with spectral peak near 1 kHz (`tests/flux/test_synthesis.py`)
- T1 conservation, T2 Bénard, T3 crystallization, T4 decay all still pass

**Why this is a separate phase:** F0–F1c is pure substrate. The hot floor was driven by a constant injector or a uniform-frequency one. F2 replaces that injector with a signal-driven one: the cochlea bank converts a 1-D waveform into per-resonator instantaneous amplitudes, and each resonator drives injection at its floor location with its tuned frequency. Symmetrically, synthesis converts bound-node activity back into a waveform via the same bank (additive). No new physics — only an input/output adapter — but a contract that the substrate can be probed with real signals. Binding, decay, plasticity all stay as F1c configured them.

**Architecture sketch (per spec §5, especially §5.6 cochlea + §5.7 synthesis):**

- **Resonator bank.** `N_cochlea = 64` second-order damped resonators, log-spaced from 50 Hz to 8 kHz. Each resonator has a tuned `freq_hz`, a quality factor `Q`, and instantaneous state `(amp, vel_amp)`. State update per audio-sample is the classical biquad: `amp'' + (ω/Q) amp' + ω² amp = ω² x(t)` (driven harmonic oscillator), discretised by a stable RK2 or trapezoid step. No FFT, no learned weights.
- **Cochlea → injection.** Each substrate tick consumes `n_audio_samples_per_tick` audio samples (default 16, i.e. 16 kHz audio @ 1 kHz tick rate). The bank is advanced sample-by-sample over that window; per resonator the *peak* abs(amp) over the window controls the count of vibrations injected at that resonator's floor location this tick. Vibrations get `frequency = log(freq_hz)` (matching the substrate's log-Hz convention from spec §5.2) and a randomised xy position within a small disc around the resonator's floor slot.
- **Synthesis ← node firings.** Each bound node has a `frequency` (inherited from its constituent vibrations' centroid frequency at bind time). At each tick the substrate emits node "firings" — proxied as the change in bound-node bridge flux above a threshold — and routes each firing to the resonator whose `freq_hz` is closest in log-space. The resonator is driven by a brief impulse proportional to firing strength. The output sample is the sum of all resonators' `amp` at that audio-sample, then audio is reconstructed at the same `n_audio_samples_per_tick` rate.
- **No learning of the bank.** Spec §5.6: "The cochlea is fixed, not learned." The bank's centre frequencies, Q, and floor positions are locked at config time. Plasticity in F1b only touches bridges between nodes; it does not touch the cochlea or the synthesis bank.
- **Audio I/O at the file boundary.** Plan supplies `agent/flux/audio_in.py` (read wav, resample to 16 kHz mono, iterate sample-chunks) and `agent/flux/audio_out.py` (accumulate samples, write wav). These are dumb glue — most of the F2 work is the resonator bank and its hookup to inject/synthesis.

**Tech stack:** Python 3.13, numpy, pytest. `scipy.signal` for filter design + `soundfile` (or `wave` stdlib) for wav I/O. `soundfile` is a permitted new dep — preferred for resampling support. No torch, no librosa.

**Spec reference:** `docs/superpowers/specs/2026-05-10-flux-substrate-design.md` — §5.6 (cochlea), §5.7 (synthesis), §5.2 (vibration `frequency` is log-Hz), §6 tick order (cochlea-driven injection slots into step 2 "Inject", synthesis is a read-only consumer at step 9-ish), §9 F2 row of the roadmap ("1 kHz tone burst injected → frequency-matched ringing in output"). The §5 architecture chapter is the load-bearing one.

**Estimated wallclock:** 4–8 weeks solo per spec §9 F2 row; compressed under autonomous-build with the well-defined acceptance.

**Acceptance contract (binary):**
- `uv run pytest tests/flux/test_cochlea.py -v` passes — covers single-resonator dynamics, log-spaced bank construction, and the 1 kHz-tone-burst → injected-frequency-distribution end-to-end test
- `uv run pytest tests/flux/test_synthesis.py -v` passes — covers single-resonator impulse response, forced-firing-pattern → output-spectrum end-to-end test, and round-trip (cochlea + synthesis with binding disabled passes through frequency content within tolerance)
- `uv run pytest tests/flux/test_conservation.py -v` still passes (T1: cochlea injection energy still audited; synthesis is read-only and doesn't touch energy)
- `uv run pytest tests/flux/test_benard.py -v` still passes (T2: cochlea is OFF in this test; substrate-only physics unchanged)
- `uv run pytest tests/flux/test_crystallization.py -v` still passes (T3)
- `uv run pytest tests/flux/test_decay.py -v` still passes (T4)
- `uv run pytest -m "not slow"` still passes (legacy regression baseline)

These pytest paths — `tests/flux/test_cochlea.py` and `tests/flux/test_synthesis.py` — are the pre-registered F2 acceptance targets. R-3 implements against this contract.

---

## What F2 deliberately defers

| Concept | Status in F2 | Where it lands |
|---|---|---|
| Real audio corpus (not just synthetic tones) | NOT in scope | R-6/R-7/R-8 (training phase) |
| Learning rule that exploits the cochlea/synthesis loop | NOT in scope | F3 (R-4/R-5) |
| Attention reallocate (PE-driven compute budget) | NOT in scope | F4+ |
| Cochlea adaptation (frequency curve learning) | EXPLICITLY out of spec | never — spec §5.6 fixes it |
| Phoneme probe | NOT in scope | F4 (Tier-2 falsifier) |
| Multi-channel audio | NOT in scope | beyond Phase-1 |

F2 is the adapter layer. No new physics, no learning rule, no claims about emergence. Its only job: make signal-in / signal-out work end-to-end while every Phase-1 test still passes.

---

## Open calibration choices (call these out in phase-log)

Spec §10 lists `N_cochlea = 64` as an open question; F2's other open knobs follow. Default values below; tune during the 1 kHz round-trip test and record in phase-log per the F1a/F1b/F1c pattern.

| Param | Default | Purpose |
|---|---|---|
| `N_cochlea` | `64` | Number of resonators in the bank. Spec §5.6 default. |
| `freq_min_hz` | `50.0` | Low edge of log-spaced bank. Spec §5.6. |
| `freq_max_hz` | `8000.0` | High edge. Spec §5.6. |
| `Q` | `5.0` | Resonator quality factor. Mid value: high enough for selectivity, low enough that a 1 kHz tone visibly excites the 1 kHz channel within ~100 samples. |
| `audio_sample_rate_hz` | `16000` | Mono. Resample input wavs to this. |
| `n_audio_samples_per_tick` | `16` | Audio samples consumed per substrate tick → tick rate = 1 kHz substrate-time. |
| `cochlea_inject_gain` | `1.0` | Maps resonator peak-amp to vibration-injection count. |
| `cochlea_inject_max_per_tick` | `8` | Per-resonator cap on injection count per tick (prevents one loud channel from saturating `max_quanta`). |
| `synth_firing_threshold` | `0.1` | Min bridge-flux delta to register as a "node firing". |
| `synth_impulse_gain` | `1.0` | Maps firing strength to resonator drive impulse. |
| `synth_output_gain` | `1.0` | Final output sample scaling. |
| `cochlea_floor_disc_radius` | `1.0` | Radius around each resonator's floor slot in which to randomise injected-vibration xy. |

If the 1 kHz round-trip in Task 6 fails, sweep in order: `Q` → `cochlea_inject_gain` → `synth_impulse_gain` → `N_cochlea` (more channels = finer freq resolution at higher cost). Up to 5 sweeps before escalating per the F1a/F1b/F1c protocol.

---

## File structure (locked decisions)

New files:

| Path | Responsibility |
|---|---|
| `agent/flux/cochlea.py` | `CochleaConfig` dataclass + `Resonator` array + `Cochlea` bank class + `step_resonators(bank, samples)` + `cochlea_inject(quanta, grid, bank, cfg, rng)` |
| `agent/flux/synthesis.py` | `SynthesisConfig` dataclass + `Synthesizer` bank class (mirrors cochlea bank) + `route_node_firings(nodes, bridges, prev_flux, current_flux, bank, cfg)` + `read_output_sample(bank)` |
| `agent/flux/audio_in.py` | `read_wav_mono_16k(path) -> np.ndarray` + sample-chunk iterator |
| `agent/flux/audio_out.py` | Append-and-flush wav writer at 16 kHz mono |
| `tests/flux/test_cochlea.py` | Single-resonator dynamics, bank construction, tone-burst → injection-frequency-distribution end-to-end |
| `tests/flux/test_synthesis.py` | Single-resonator impulse response, forced-firings → output-spectrum, round-trip (cochlea + synthesis) on a 1 kHz tone burst |

Modified files:

| Path | What changes |
|---|---|
| `world/flux/dynamics.py` | New optional kwargs `cochlea_bank`, `synth_bank`, `audio_in_chunk`, `audio_out_buffer` on `tick`. When supplied, tick (a) steps the cochlea bank by `n_audio_samples_per_tick` samples, (b) routes its per-resonator peak-amps into cochlea-driven injection, (c) after binding + plasticity, routes node-firings into the synthesis bank, (d) reads `n_audio_samples_per_tick` output samples into `audio_out_buffer`. Defaults all `None` so F0–F1c tests are unaffected. |
| `agent/flux/__init__.py` | Re-export `Cochlea`, `CochleaConfig`, `Synthesizer`, `SynthesisConfig`, `read_wav_mono_16k`. |
| `world/flux/boundary.py` | `inject_hot_floor` gains an optional `freq_hz_override` kwarg (single-vibration variant). Used by cochlea injection to pin frequency per resonator. Default behaviour preserved. |
| `docs/flux/phase-log.md` | F2-start, per-sweep, F2-close entries. |
| `pyproject.toml` | Add `soundfile` to deps (only if `wave` stdlib insufficient — decide in Task 4). |
| `README.md` | One-line status update on F2. |

**Conservation accounting note:** the cochlea is purely a routing layer — it generates new vibrations whose energy is recorded by the auditor exactly as today's `inject_hot_floor` does (via `audit.record_injection`). The synthesis layer is read-only; it does not consume substrate energy. So no auditor changes are needed for F2.

---

## Task 1: F2 start — phase-log entry

**Files:** Modify `docs/flux/phase-log.md`.

- [ ] Append the F2-start block describing scope, open calibration choices, deferred items, and the locked pytest acceptance paths (`tests/flux/test_cochlea.py`, `tests/flux/test_synthesis.py`).
- [ ] Commit: `flux F2 start: phase-log entry`.

---

## Task 2: Single damped resonator (pure function)

**Files:**
- Create: `agent/flux/cochlea.py` (Resonator + step function only — bank wiring lands in Task 3)
- Create: `tests/flux/test_cochlea.py` (single-resonator section only — bank + injection sections land in Task 3 + 4)

A second-order damped resonator obeying `amp'' + (ω/Q) amp' + ω² amp = ω² x(t)`. Discretise with trapezoid (semi-implicit Euler also OK): given state `(amp, vel)` and drive sample `x`,
```
acc = ω² * (x - amp) - (ω/Q) * vel
vel += acc * dt
amp += vel * dt
```
where `dt = 1 / audio_sample_rate_hz` and `ω = 2π * freq_hz`.

- [ ] **Step 1: Tests first.**

```python
"""Tests for cochlea — F2."""
from __future__ import annotations
import numpy as np
import pytest

from agent.flux.cochlea import Resonator, step_resonator


def test_resonator_rings_at_its_tuned_frequency():
    """An impulse into a 1 kHz resonator produces a ringing whose
    zero-crossing rate matches ~1 kHz."""
    sr = 16000
    r = Resonator(freq_hz=1000.0, Q=10.0)
    out = np.zeros(2000, dtype=np.float64)
    # impulse drive
    out[0] = step_resonator(r, drive=1.0, sr=sr)
    for i in range(1, len(out)):
        out[i] = step_resonator(r, drive=0.0, sr=sr)
    # zero crossings of the tail (after initial transient)
    tail = out[200:1200]
    zc = np.sum(np.diff(np.sign(tail)) != 0)
    # 1000 Hz over 1000 samples @ 16 kHz = 62.5 ms => ~125 zero crossings
    assert 100 < zc < 150, f"zc={zc} not consistent with 1 kHz ringing"


def test_resonator_decays_under_Q():
    """A finite-Q resonator's envelope decays over time."""
    sr = 16000
    r = Resonator(freq_hz=500.0, Q=5.0)
    samples = []
    samples.append(step_resonator(r, drive=1.0, sr=sr))
    for _ in range(1, 4000):
        samples.append(step_resonator(r, drive=0.0, sr=sr))
    early = np.max(np.abs(samples[:500]))
    late = np.max(np.abs(samples[-500:]))
    assert late < 0.2 * early, f"envelope did not decay: early={early}, late={late}"


def test_resonator_selectivity_off_band():
    """Driving a 1 kHz resonator with a 4 kHz sine produces a smaller
    response than driving it with a 1 kHz sine."""
    sr = 16000
    n = 4000

    def drive(freq):
        r = Resonator(freq_hz=1000.0, Q=10.0)
        out = []
        for i in range(n):
            x = np.sin(2 * np.pi * freq * i / sr)
            out.append(step_resonator(r, drive=x, sr=sr))
        return np.max(np.abs(out[-1000:]))

    on_band = drive(1000.0)
    off_band = drive(4000.0)
    assert on_band > 3.0 * off_band, (
        f"resonator not selective: on={on_band}, off={off_band}"
    )
```

- [ ] **Step 2: Implement** `agent/flux/cochlea.py` with the `Resonator` dataclass and `step_resonator(r, drive, sr) -> float`.

- [ ] **Step 3: Run** `uv run pytest tests/flux/test_cochlea.py -v -k resonator`. Expect 3/3 pass.

- [ ] **Step 4: Commit** `flux F2 task 2: damped resonator + selectivity tests`.

---

## Task 3: Log-spaced cochlea bank + waveform step

**Files:**
- Modify: `agent/flux/cochlea.py` (add `CochleaConfig`, `Cochlea` bank class, `step_resonators`)
- Modify: `tests/flux/test_cochlea.py` (add bank-section tests)

- [ ] **Step 1: Tests.**

```python
def test_cochlea_bank_log_spaced_frequencies():
    from agent.flux.cochlea import Cochlea, CochleaConfig
    cfg = CochleaConfig(n_resonators=64, freq_min_hz=50.0, freq_max_hz=8000.0, Q=5.0)
    bank = Cochlea(cfg)
    freqs = bank.freqs_hz
    assert len(freqs) == 64
    assert freqs[0] == pytest.approx(50.0, rel=1e-3)
    assert freqs[-1] == pytest.approx(8000.0, rel=1e-3)
    # log spacing: ratios constant
    ratios = freqs[1:] / freqs[:-1]
    assert np.std(ratios) / np.mean(ratios) < 1e-6


def test_cochlea_bank_peaks_at_input_frequency():
    """A 1 kHz tone through the full bank → the resonator nearest
    1 kHz has the largest peak amplitude over the window."""
    from agent.flux.cochlea import Cochlea, CochleaConfig, step_resonators
    cfg = CochleaConfig(
        n_resonators=64, freq_min_hz=50.0, freq_max_hz=8000.0,
        Q=10.0, sample_rate_hz=16000,
    )
    bank = Cochlea(cfg)
    sr = cfg.sample_rate_hz
    n = 4000
    t = np.arange(n) / sr
    x = np.sin(2 * np.pi * 1000.0 * t)
    peaks = step_resonators(bank, samples=x)
    # idx of resonator closest to 1 kHz
    idx_target = int(np.argmin(np.abs(bank.freqs_hz - 1000.0)))
    idx_actual = int(np.argmax(peaks))
    # within +/-1 resonator slot (log spacing means neighbours are close)
    assert abs(idx_actual - idx_target) <= 1, (
        f"bank peak at idx={idx_actual} (freq={bank.freqs_hz[idx_actual]:.1f}), "
        f"expected near idx={idx_target} (freq={bank.freqs_hz[idx_target]:.1f})"
    )
```

- [ ] **Step 2: Implement.** `Cochlea(cfg)` builds 64 `Resonator` instances with log-spaced freqs. `step_resonators(bank, samples) -> np.ndarray` advances all resonators by the audio buffer and returns the per-resonator *peak* abs(amp) over the buffer.

- [ ] **Step 3: Run** `uv run pytest tests/flux/test_cochlea.py -v`. Expect 5/5 pass.

- [ ] **Step 4: Commit** `flux F2 task 3: log-spaced cochlea bank`.

---

## Task 4: Cochlea-driven injection + audio_in

**Files:**
- Modify: `agent/flux/cochlea.py` (add `cochlea_inject`)
- Create: `agent/flux/audio_in.py`
- Modify: `world/flux/boundary.py` (add `freq_hz_override` to `inject_hot_floor`)
- Modify: `tests/flux/test_cochlea.py` (add injection-section tests)

- [ ] **Step 1: Add the `freq_hz_override` kwarg** to `inject_hot_floor` so callers can pin a specific frequency per injected vibration. Existing tests with no override unchanged.

- [ ] **Step 2: Implement `cochlea_inject(quanta, grid, bank, cfg, rng) -> int`** which: (a) takes the `bank.last_peaks` array from the most recent `step_resonators` call, (b) for each resonator slot, computes injection count `= min(round(peak * cochlea_inject_gain), cochlea_inject_max_per_tick)`, (c) injects that many vibrations at a randomised position within `cochlea_floor_disc_radius` of the resonator's floor slot, with `frequency = log(resonator.freq_hz)`. Returns total energy injected for the auditor.

- [ ] **Step 3: Implement `read_wav_mono_16k(path) -> np.ndarray`** in `agent/flux/audio_in.py`. Use `soundfile` if added; else `wave` + manual resample. Plus `iter_sample_chunks(samples, chunk_size)` generator.

- [ ] **Step 4: End-to-end test.** A 200 ms 1 kHz sine wave → through cochlea bank → through `cochlea_inject` → check that the injected vibrations' `log(freq_hz)` mode is at the resonator closest to 1 kHz.

```python
def test_cochlea_inject_routes_1khz_tone_to_correct_floor_slot():
    from world.flux.quantum import Quanta
    from world.flux.grid import Grid
    from agent.flux.cochlea import (
        Cochlea, CochleaConfig, step_resonators, cochlea_inject,
    )
    rng = np.random.default_rng(0)
    cfg = CochleaConfig(
        n_resonators=64, freq_min_hz=50.0, freq_max_hz=8000.0,
        Q=10.0, sample_rate_hz=16000, inject_gain=2.0, inject_max_per_tick=8,
    )
    bank = Cochlea(cfg)
    q = Quanta(max_quanta=10_000)
    g = Grid(dims=(30, 30, 60), voxel_size=1.0)
    sr = cfg.sample_rate_hz
    n_samples = 3200  # 200 ms
    t = np.arange(n_samples) / sr
    waveform = np.sin(2 * np.pi * 1000.0 * t)
    # 200 ticks @ 16 samples/tick
    for tick_idx in range(200):
        chunk = waveform[tick_idx * 16:(tick_idx + 1) * 16]
        step_resonators(bank, samples=chunk)
        cochlea_inject(q, g, bank, cfg, rng=rng)
    alive_freqs_log = q.freq[q.alive]
    # freq stored is log(freq_hz); back-convert
    alive_freqs_hz = np.exp(alive_freqs_log)
    target = 1000.0
    # mode within +/-20% of 1 kHz
    median_hz = float(np.median(alive_freqs_hz))
    assert 0.8 * target < median_hz < 1.2 * target, (
        f"injected freq median {median_hz:.1f} Hz not near 1 kHz target"
    )
```

- [ ] **Step 5: Run** `uv run pytest tests/flux/test_cochlea.py -v`. Expect 6/6 pass.

- [ ] **Step 6: Commit** `flux F2 task 4: cochlea-driven injection + audio_in`.

---

## Task 5: Synthesis bank + audio_out

**Files:**
- Create: `agent/flux/synthesis.py`
- Create: `agent/flux/audio_out.py`
- Create: `tests/flux/test_synthesis.py`

The synthesis bank uses the SAME resonator dynamics as the cochlea — only the driver source changes. Cochlea's resonators are driven by the input waveform; synthesis's resonators are driven by node-firing impulses.

A node fires when its inbound bridge-flux delta exceeds `synth_firing_threshold`. The firing routes to the bank resonator whose `freq_hz` is closest in log-space to `exp(node.frequency)`, with drive impulse `= synth_impulse_gain * firing_strength`. After all firings, the bank is advanced by `n_audio_samples_per_tick` samples with drive=0 (impulses already injected), and the per-sample `sum(resonator.amp for r in bank)` is appended to the output buffer.

- [ ] **Step 1: Tests.**

```python
"""Tests for synthesis — F2."""
from __future__ import annotations
import numpy as np
import pytest

from agent.flux.synthesis import (
    Synthesizer, SynthesisConfig, drive_resonator_impulse, read_output_samples,
)


def test_synthesis_impulse_produces_ringing_at_resonator_freq():
    cfg = SynthesisConfig(
        n_resonators=64, freq_min_hz=50.0, freq_max_hz=8000.0,
        Q=10.0, sample_rate_hz=16000,
    )
    bank = Synthesizer(cfg)
    idx_1k = int(np.argmin(np.abs(bank.freqs_hz - 1000.0)))
    drive_resonator_impulse(bank, slot=idx_1k, strength=1.0)
    out = read_output_samples(bank, n_samples=2000)
    # spectrum peak near 1 kHz
    spec = np.abs(np.fft.rfft(out))
    freqs = np.fft.rfftfreq(len(out), d=1.0 / cfg.sample_rate_hz)
    peak_hz = freqs[int(np.argmax(spec))]
    assert 800.0 < peak_hz < 1200.0, f"peak at {peak_hz} Hz, expected ~1000"


def test_synthesis_routes_node_firings_to_nearest_resonator():
    """A forced node-firing pattern at log(1000) -> output spectrum peak
    near 1 kHz."""
    from agent.flux.synthesis import route_node_firings_explicit
    cfg = SynthesisConfig(
        n_resonators=64, freq_min_hz=50.0, freq_max_hz=8000.0,
        Q=10.0, sample_rate_hz=16000, impulse_gain=1.0,
    )
    bank = Synthesizer(cfg)
    # explicit (freq_log, strength) firing list -- bypass the dynamics-coupled
    # path so this test isolates the routing math
    firings = [(float(np.log(1000.0)), 1.0)] * 20
    route_node_firings_explicit(bank, firings)
    out = read_output_samples(bank, n_samples=4000)
    spec = np.abs(np.fft.rfft(out))
    freqs = np.fft.rfftfreq(len(out), d=1.0 / cfg.sample_rate_hz)
    peak_hz = freqs[int(np.argmax(spec))]
    assert 800.0 < peak_hz < 1200.0, f"peak at {peak_hz} Hz, expected ~1000"
```

- [ ] **Step 2: Implement** `agent/flux/synthesis.py` with `Synthesizer`, `SynthesisConfig`, `drive_resonator_impulse`, `read_output_samples`, `route_node_firings_explicit`, `route_node_firings(nodes, bridges, prev_flux, current_flux, bank, cfg)`.

- [ ] **Step 3: Implement** `agent/flux/audio_out.py` with an append-and-flush wav writer.

- [ ] **Step 4: Run** `uv run pytest tests/flux/test_synthesis.py -v`. Expect 2/2 pass at this point.

- [ ] **Step 5: Commit** `flux F2 task 5: synthesis bank + audio_out`.

---

## Task 6: 1 kHz round-trip integration test

**Files:** Modify `tests/flux/test_synthesis.py` (add the integration test) + `world/flux/dynamics.py` (cochlea/synth kwargs on `tick`).

Spec §9 F2 acceptance: "1 kHz tone burst injected → frequency-matched ringing in output." This test is the substantive proof of F2.

Use a configuration with binding disabled (so the dynamics path is: cochlea injects → free quanta drift up → synthesis reads… but since binding is off there are no bound nodes to fire). Two flavours of the test:

(a) **Cochlea-only feed-through.** Disable binding entirely. Feed a 1 kHz tone burst. Capture per-tick the per-resonator peaks from the cochlea bank, then re-drive a matching synthesis bank with those peaks as impulses (a cochlea→bank→synth shortcut to validate routing). Output spectrum peak must be near 1 kHz. This isolates cochlea + synthesis from substrate dynamics.

(b) **Through-substrate round-trip.** Enable binding with a tuned `BindingConfig` so the 1 kHz injection produces bound nodes; the synthesis then reads node firings. Output spectrum peak near 1 kHz within wider tolerance (±50%). This is the looser test — substrate dynamics can broaden the peak.

- [ ] **Step 1: Add `cochlea_bank`, `synth_bank`, `audio_chunk_in`, `audio_buffer_out` kwargs** to `world/flux/dynamics.py::tick`. When supplied, the tick: steps cochlea bank by chunk → calls `cochlea_inject`; after binding/plasticity, calls `route_node_firings` → reads `n_audio_samples_per_tick` synthesis samples into the output buffer.

- [ ] **Step 2: Write the integration test.**

```python
def test_F2_1khz_burst_roundtrip_cochlea_only():
    """Tone burst through cochlea -> bank-shortcut -> synthesis.
    Isolates F2 routing from substrate dynamics."""
    from agent.flux.cochlea import Cochlea, CochleaConfig, step_resonators
    from agent.flux.synthesis import (
        Synthesizer, SynthesisConfig, drive_resonator_impulse, read_output_samples,
    )
    sr = 16000
    ccfg = CochleaConfig(n_resonators=64, freq_min_hz=50.0, freq_max_hz=8000.0,
                         Q=10.0, sample_rate_hz=sr)
    scfg = SynthesisConfig(n_resonators=64, freq_min_hz=50.0, freq_max_hz=8000.0,
                           Q=10.0, sample_rate_hz=sr)
    coch = Cochlea(ccfg)
    synth = Synthesizer(scfg)
    n_samples = sr // 2  # 500 ms
    t = np.arange(n_samples) / sr
    x = np.sin(2 * np.pi * 1000.0 * t)
    chunk = 16
    out_total = []
    for i in range(0, n_samples, chunk):
        buf = x[i:i + chunk]
        peaks = step_resonators(coch, samples=buf)
        for slot, p in enumerate(peaks):
            if p > 0.01:
                drive_resonator_impulse(synth, slot=slot, strength=float(p))
        out_total.extend(read_output_samples(synth, n_samples=chunk))
    out = np.array(out_total[-(sr // 4):])  # last 250 ms (skip transients)
    spec = np.abs(np.fft.rfft(out))
    freqs = np.fft.rfftfreq(len(out), d=1.0 / sr)
    peak_hz = freqs[int(np.argmax(spec))]
    assert 800.0 < peak_hz < 1200.0, (
        f"round-trip peak at {peak_hz} Hz, expected ~1000"
    )
```

- [ ] **Step 3: Run** `uv run pytest tests/flux/test_synthesis.py -v`. Expect 3/3 pass.

- [ ] **Step 4: Up to 5 calibration sweeps** if the round-trip fails. Order: `Q` (selectivity) → `cochlea_inject_gain` → `synth_impulse_gain` → `N_cochlea` → resonator dt-stepping scheme (try trapezoid vs RK2). Document each sweep in phase-log.

- [ ] **Step 5: Commit** `flux F2 task 6: 1 kHz round-trip passes`.

- [ ] **Step 6: BLOCKER** — if the round-trip fails after 5 sweeps, escalate. The resonator dynamics may need a higher-order integrator, or the impulse-drive scaling may need to compensate for the bank's gain-vs-Q relationship.

---

## Task 7: Verify T1 + T2 + T3 + T4 + legacy still pass

The F2 work is additive: tick gains optional kwargs, all default to None. Existing Phase-1 tests should be unaffected — but verify.

- [ ] **Step 1: Run** `uv run pytest tests/flux/ -v`. All previous tests (F0–F1c, expected ~87) + new cochlea (6) + new synthesis (3) = ~96 pass.

- [ ] **Step 2: Run legacy suite.** Expect 382 pass.

- [ ] **Step 3: If T2 Bénard regressed**, the most likely cause is the `inject_hot_floor` signature change in Task 4 (the new `freq_hz_override` kwarg). Bisect by reverting just that kwarg's call sites.

- [ ] **Step 4: Commit (if any fixups)** `flux F2 task 7: regressions fixed`.

---

## Task 8: `__init__` re-exports + README + F2 close

**Files:**
- Modify: `agent/flux/__init__.py` (re-export `Cochlea`, `CochleaConfig`, `Synthesizer`, `SynthesisConfig`, `cochlea_inject`, `route_node_firings`, `read_wav_mono_16k`)
- Modify: `world/flux/__init__.py` (no new exports, but bump module docstring's "stabilises after F1" line to mention F2-adapter status)
- Modify: `README.md`
- Modify: `docs/flux/phase-log.md`

- [ ] **Step 1: Update `agent/flux/__init__.py`** with the F2 symbols and a clean `__all__`.

- [ ] **Step 2: README "Two substrates" status line**:

```
Status as of <date>: F0 + F1a + F1b + F1c + F2 complete (Phase 1 +
cochlea + synthesis). 1 kHz tone-burst round-trip passes. F3 (learning
rule derived from the flux principle) is next.
```

- [ ] **Step 3: Phase-log F2-close entry:** task summary, final `CochleaConfig` + `SynthesisConfig`, measured round-trip peak Hz, test counts (Phase-1 + cochlea + synthesis + legacy).

- [ ] **Step 4: Run** `uv run pytest tests/flux/ -v` (all green) and the legacy suite (382). Commit only if both clean.

- [ ] **Step 5: Commit** `flux F2 complete: re-exports + README status + phase-log`.

---

## Notes for autonomous execution

- **Per spec §5.6 the cochlea is FIXED.** Do not introduce any adaptation of `freq_hz`, `Q`, or floor positions. If a task seems to require it, the task is mis-specified — escalate.
- **Per spec §5.7 the synthesis bank IS the cochlea bank, used in reverse.** Do not introduce a separate set of frequencies. The two banks share their `freqs_hz` array by construction.
- **Resonator stability under high Q.** Q=10 with trapezoid stepping at 16 kHz is comfortably stable; Q=100+ may blow up with a naive explicit Euler. If a resonator goes NaN under sweep, switch the discretisation, not the test threshold.
- **Conservation audit unchanged.** Cochlea injection records its quanta count × `energy_per` via `audit.record_injection`, same as `inject_hot_floor`. Synthesis is read-only — it doesn't extract energy from the substrate, just observes flux deltas. The auditor needs no new field.
- **FFT interpretation pitfalls.** The round-trip test reads the *last 250 ms* of output to skip startup transients. Reading the whole window will include the resonator ring-up artefact and may shift the spectral peak.
- **Binding stays optional.** Tasks 2–5 build the I/O layer in isolation. Task 6 part (a) explicitly bypasses the substrate. Only Task 6 part (b) (if attempted) runs through dynamics. The pre-registered acceptance is the cochlea-only round-trip in Task 6 part (a) — that is what `tests/flux/test_synthesis.py::test_F2_1khz_burst_roundtrip_cochlea_only` covers.
- **5-sweep cap from F1a/F1b/F1c still applies.** If Task 6 won't pass with 5 sweeps' worth of tuning, escalate to a HUMAN_NEEDED entry. The resonator-bank approach is well-established and should pass without exotic tuning — failure to pass suggests an implementation bug, not a parameter issue.
- **No new science in F2.** F2 is plumbing. The substantive claims (emergence, learning) come in F3 (R-4/R-5). Do not insert any "interesting" cross-talk between cochlea and synthesis here; the loop is closed via the substrate's existing dynamics, not via a synthesis-side shortcut.
