# Flux Substrate F2 — Cochlea + Synthesis + First Audio Round-Trip

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the first audio I/O layer of the flux substrate per spec §5.6 (cochlea) and §5.7 (synthesis). A 1 kHz tone burst, fed through the cochlea as injection driver, must produce a synthesised output waveform whose dominant FFT bin is at 1 kHz ±20%. T1 (conservation), T2 (Bénard), T3 (crystallization), T4 (decay) must all remain green.

**Why this is a separate phase:** F0–F1c built the thermodynamic substrate (quanta + grid + binding + decay + plasticity + buoyancy/damping). The substrate has been validated by injecting *thermally distributed* quanta from a constant source. F2 replaces that constant injector with a *driven* injector — a fixed bank of damped resonators that convert audio samples into frequency-matched quantum injections. F2 also adds the inverse path: synthesis reads quanta near the floor and excites the same resonator bank in reverse to produce an output waveform. F2 is the smallest standalone unit of "audio in, audio out" that exercises every layer of the substrate end-to-end without invoking learning. Learning (plasticity beyond the existing flux-driven rule) is deferred to F3.

**Spec reference:** `docs/superpowers/specs/2026-05-10-flux-substrate-design.md` — §5 (architecture), specifically §5.6 (cochlea, input), §5.7 (synthesis, output). §5.2 (vibrations carry `frequency`), §5.3 (hot floor as injecting boundary), §6 (tick order — injection is step 2, absorption is step 3), §7 (Phase-1 contract: T1+T2+T3+T4 must remain green when cochlea + synthesis are wired in), §9 F2 binary contract ("1 kHz tone burst injected → frequency-matched ringing in output").

**Tech stack:** Python 3.13, numpy (already a dep), pytest. No new dependencies — second-order resonators are recurrence-friendly, no FFT in hot loop. FFT only in the acceptance test via `numpy.fft`.

**Estimated wallclock:** 4–8 weeks solo per spec §9; compressed under autonomous-build to one R-3 session.

---

## Acceptance contract

The R-3 session that implements this plan PASSES if and only if every line below holds.

- `uv run pytest tests/flux/test_cochlea.py -v` passes (unit tests for resonator dynamics, cochlea bank construction, frequency-rate-of-injection coupling).
- `uv run pytest tests/flux/test_synthesis.py -v` passes (unit tests for synthesis resonator excitation, output sample generation, AND the 1 kHz round-trip acceptance test described in Task 6).
- `uv run pytest tests/flux/test_conservation.py -v` still passes (T1 — cochlea injection accounts via the auditor; synthesis is read-only on quantum state and does not create or destroy energy).
- `uv run pytest tests/flux/test_benard.py -v` still passes (T2 — F2 thermal layer untouched; cochlea is opt-in via injector, default tick path unchanged).
- `uv run pytest tests/flux/test_crystallization.py -v` still passes (T3).
- `uv run pytest tests/flux/test_decay.py -v` still passes (T4).
- `uv run pytest -m "not slow"` passes overall (legacy regression baseline holds).

The binary acceptance test (Task 6) is: feed a 100 ms, 1 kHz sinusoid burst into a `Cochlea` driving a fresh substrate; record the `Synthesis` output samples for 200 ms; take the FFT of the recorded output; the dominant non-DC bin's centre frequency must be within ±20% of 1000 Hz. Below that, the F2 round-trip has failed and the verdict is NULL (not "loosen the ±20%").

**Pre-registered for R-3 contract:** acceptance file paths are `tests/flux/test_cochlea.py` and `tests/flux/test_synthesis.py`. This is the contract between R-2 (this plan) and R-3 (the implementation session). R-3 is free to add additional test files but must NOT rename or split these two.

---

## What F2 deliberately defers

| Concept | Status in F2 | Where it lands |
|---|---|---|
| Cochlea tuning learned over training | NOT in scope — fixed log-spaced bank per spec §5.6 | Out of project (cochlea is biological-fixed analog) |
| Learned decoder for synthesis | NOT in scope per spec §5.7 ("no learned decoder, no KMeans-to-STFT") | Out of project |
| Attention reallocate (PE-driven compute budget §5.8) | NOT in scope | F3 or F4 |
| Multi-frequency learning / phoneme structure | NOT in scope | F3 (learning) + F4 (Tier-2 probe) |
| Real audio corpus | NOT in scope — F2 uses synthetic tone bursts only | R-7 (corpus build) + R-8 (training run) |
| Bound-node-driven synthesis (per spec §5.7 "node firings cause amplitude excitations") | DEFERRED to the bound-node mode in Task 4. F2 default synthesis reads free quanta near the floor on their way to absorption; bound-node-driven synthesis is the optional path enabled when nodes are present | Stays in F2 as optional, exercised by R-3 if binding emerges in the 1 kHz test; otherwise unused but wired |
| Phase locking between cochlea and synthesis resonators | NOT in scope — both banks are independent oscillators | F3 if needed for tier-2 stability |
| `pred_coherence` as windowed cross-correlation | still F1a stub, untouched in F2 | F3 (when learning needs it) |

Multi-way binding (3+ quanta → 1 node) and node-to-node binding via bridges are also still deferred from F1c; they may light up incidentally if the 1 kHz tone produces a coherent stream, but no Task in this plan requires them.

---

## Open calibration choices

These are spec §10 open questions. Defaults below; R-3 sweeps and records in `docs/flux/phase-log.md` per the F1a/F1b/F1c pattern. The 5-sweep cap (`sweep budget`) from F1a/F1b/F1c carries over: if 5 sweeps don't make Task 6 pass, escalate per the BLOCKER step rather than tuning indefinitely.

| Param | Default | Purpose |
|---|---|---|
| `N_cochlea` | `64` | Number of resonators per spec §5.6. May reduce to 32 if hot-loop CPU is a problem on Apple Silicon; do not go above 128. |
| `f_lo`, `f_hi` | `50.0`, `8000.0` Hz | Log-spaced bank endpoints per spec §5.6. |
| `audio_sample_rate` | `16000` Hz | One sample per substrate tick at `dt = 1/16000 s` — keeps `freq` field interpretable as Hz and matches the F0–F1c convention that `freq` is in Hz, not normalised. |
| `dt` | `1/audio_sample_rate` | Coupling between substrate clock and audio clock. F2 locks these 1:1 so synthesis can write one output sample per tick without resampling. |
| `Q_resonator` | `8.0` | Quality factor for the 2nd-order resonators. Higher Q = sharper tuning but slower ring-up. Sweep 4 / 8 / 16 if Task 6 fails. |
| `inject_gain` | `5.0` | Quanta-per-tick per unit resonator amplitude. Sweep 1 / 5 / 20 if injection rate is too low or audit headroom is breached. |
| `synth_gain` | `1.0` | Output-waveform amplitude scale per quantum read. Calibrate so synthesised RMS is in a sensible numerical range (1e-3 .. 1e+1). |
| `synth_read_zone` | `2.0` voxels | Floor-relative read depth: quanta with `z < synth_read_zone` contribute to the synthesis sample. |
| `freq_match_tol_octaves` | `0.5` | A quantum at frequency f contributes to the synth resonator whose centre is within ±freq_match_tol_octaves of `log2(f)`. Wider = blurrier output. |
| `cube_dims` | `(20, 20, 40)` | Smaller than F1c's 30×30×60 to keep test wallclock under 90 seconds. Tall enough that an injected quantum makes a few ticks before absorption. |
| `max_quanta` | `100_000` | Pre-allocated buffer. Sweep up if `add()` returns -1 in Task 6. |

Cochlea+synthesis must not require new parameters not listed above; if R-3 finds another knob is needed, that's a deviation from the plan and lands as a phase-log note.

---

## File structure (locked decisions)

R-3 must implement against these paths. Renaming is a plan deviation.

New files:

| Path | Responsibility |
|---|---|
| `agent/flux/cochlea.py` | `CochleaConfig` dataclass + `Cochlea` class wrapping a bank of damped 2nd-order resonators. Public surface: `Cochlea(cfg).step(audio_sample) -> None`, `Cochlea.injector_for(quanta, grid, audit) -> Injector`. The injector closure is what gets passed to `tick(... injector=...)`. |
| `agent/flux/synthesis.py` | `SynthesisConfig` dataclass + `Synthesis` class with its own resonator bank (centres MUST match the cochlea bank). Public surface: `Synthesis(cfg).step(quanta, grid) -> float` returns the synthesised audio sample for this tick. Optional `Synthesis.step_with_nodes(nodes, quanta, grid)` exercises the bound-node-driven path of spec §5.7. |
| `agent/flux/resonator.py` | `make_log_spaced_centres(n, f_lo, f_hi) -> np.ndarray` + `Resonator2ndOrder` SoA helper (state arrays of length N). Used by BOTH `cochlea.py` and `synthesis.py`. Single source of truth for the bank topology. |
| `tests/flux/test_cochlea.py` | Unit tests for resonator bank construction, resonator step dynamics (sinusoidal drive → resonant amplitude at f0, attenuation off-band), and `Cochlea.injector_for` producing the expected rate and frequency of injected quanta. |
| `tests/flux/test_synthesis.py` | Unit tests for synthesis bank construction, free-quanta read path, output-sample accumulation, AND the end-to-end 1 kHz round-trip acceptance test of Task 6. |

Modified files:

| Path | What changes |
|---|---|
| `agent/flux/__init__.py` | Re-export `Cochlea`, `CochleaConfig`, `Synthesis`, `SynthesisConfig`. Add `__all__`. |
| `world/flux/__init__.py` | UNCHANGED. F2 lives entirely in `agent/flux/` per spec §8. World substrate is frontend-agnostic. |
| `docs/flux/phase-log.md` | F2-start and F2-close entries; per-sweep notes if calibration is needed. |
| `README.md` | One-line F2 status update after Task 7. |

**Energy-conservation note:** the cochlea creates new quanta with `energy=energy_per` per injection event. The `Cochlea.injector_for` closure MUST call `audit.record_injection(n_injected * energy_per)` *inside* the tick so T1 closes. Synthesis is read-only on `quanta.energy` (it does not consume or transfer energy). Verify this in the Task 6 round-trip by running it under the `EnergyAuditor` with the default `tol=1e-9`.

**Threading-with-F1c note:** Task 6 is run on top of the F1c thermal stack (buoyancy + damping + thermal-boundary enforcement). The plan ASSUMES R-1's F1c branch has been merged into the R-3 working branch before Task 6 runs. If not, R-3 cherry-picks F1c onto the R-3 base. The cochlea injects at the hot floor with random xy positions and quasi-thermal-direction velocity (small gaussian in all axes); buoyancy then pushes warm-floor quanta upward as in T2.

---

## Task 1: F2 start — phase-log entry

**Files:** Modify `docs/flux/phase-log.md`.

- [ ] Append the F2-start block: scope (cochlea + synthesis + 1 kHz round-trip), open calibration choices from the table above, deferred items.
- [ ] Commit: `flux F2 task 1: phase-log start entry`.

---

## Task 2: Resonator bank — shared math primitive

**Files:**
- Create: `agent/flux/resonator.py`
- (Tests for `resonator.py` live in `tests/flux/test_cochlea.py` — see Task 3 step 1. We do not create a separate `test_resonator.py` to keep the file count bounded.)

A discrete 2nd-order resonator (high-Q bandpass) with state `(y, y_prev)` and drive `x`:

```
α = 2π f0 / fs                            # angular freq in samples
β = exp(-π f0 / (Q * fs))                  # decay per sample
y[n+1] = 2 β cos(α) y[n] - β² y[n-1] + (1-β) x[n]
```

This is the standard bandpass biquad with bandwidth `f0 / Q`. SoA-shaped so the full bank is vectorised in one numpy call per tick.

- [ ] **Step 1: Implement `agent/flux/resonator.py`.**

  Public surface:

  ```python
  def make_log_spaced_centres(n: int, f_lo: float, f_hi: float) -> np.ndarray:
      """Return centres[n], log-spaced from f_lo to f_hi, in Hz."""

  class Resonator2ndOrder:
      """Bank of N 2nd-order resonators sharing fs but each with own f0, Q.

      Attributes (all shape (N,)):
          f0, Q, alpha, beta, beta2, two_beta_cos_alpha,
          y, y_prev, amp_envelope  (envelope = |y| low-pass smoothed,
          used by the cochlea to convert resonator excitation to
          injection rate; not needed by synthesis output but harmless).

      Methods:
          step(drive: float | np.ndarray) -> np.ndarray
              # advances all resonators by one sample; returns y after step.
          reset() -> None
      """
  ```

  Decision: a single `drive` scalar is broadcast to all resonators (cochlea is mono → all see the same audio sample). For synthesis, `drive` is per-resonator (each resonator is excited by quanta near its tuned freq).

- [ ] **Step 2:** Document the analytic frequency response in a docstring (cite Steiglitz, *A Digital Signal Processing Primer*, biquad bandpass §10.5) so a reader can verify by hand that the bandwidth is `f0/Q` Hz.

- [ ] **Step 3: Commit** `flux F2 task 2: resonator bank primitive`.

---

## Task 3: Cochlea — driven injector

**Files:**
- Create: `agent/flux/cochlea.py`
- Create: `tests/flux/test_cochlea.py`

- [ ] **Step 1: Tests first.** `tests/flux/test_cochlea.py`:

  1. `test_cochlea_bank_log_spaced` — `make_log_spaced_centres(64, 50, 8000)` returns 64 values with `centres[0] == 50`, `centres[-1] == 8000`, and the ratio between successive entries is constant within 1e-9 (log-spacing).
  2. `test_resonator_responds_at_centre_freq` — single resonator at f0=1000 Hz, fs=16000, Q=8, driven by a 1 kHz unit sine for 50 ms. After 50 ms the resonator's `y` peak-to-peak should be at least 5× the steady-state response when driven by a 1 Hz signal. (Selectivity sanity check.)
  3. `test_resonator_rejects_off_band` — drive a 1 kHz resonator (Q=8) with a 100 Hz sine. Steady-state envelope must be < 30% of the on-band envelope from test 2.
  4. `test_cochlea_step_sample_advances_state` — `Cochlea(cfg).step(sample)` mutates the bank's `y` array, all 64 entries change between two consecutive non-zero samples.
  5. `test_cochlea_injector_rate_proportional_to_amplitude` — drive with 1 kHz at amplitude 1.0 for 200 samples (T_warmup), then run `injector` once on a fresh `Quanta`+`Grid`; count of injected quanta must be > 0 AND a roughly linear function of `inject_gain` (test at two values, factor 4 gain should yield 2–6× quanta within Poisson noise).
  6. `test_cochlea_injected_freq_matches_resonator_centre` — drive at 1 kHz, run injector; among injected quanta, the slot whose source resonator was the 1 kHz bin must carry `freq` within ±5% of 1000 Hz. (Tests the per-resonator `freq` tagging in the injection event.)
  7. `test_cochlea_injector_records_into_auditor` — wrap with an `EnergyAuditor`; after N=10 injection ticks driven by 1 kHz, `audit.E_injected_total > 0` and equals `(sum of n_injected per tick) * energy_per`.
  8. `test_cochlea_silent_input_no_injection` — drive with zeros for 1000 samples; injector returns 0 quanta. (Sanity: cochlea is not a free-running oscillator.)

- [ ] **Step 2: Implement `agent/flux/cochlea.py`.**

  ```python
  @dataclass
  class CochleaConfig:
      n_cochlea: int = 64
      f_lo: float = 50.0
      f_hi: float = 8000.0
      audio_sample_rate: float = 16000.0
      Q: float = 8.0
      inject_gain: float = 5.0          # quanta per unit |y| per tick
      energy_per: float = 1.0
      vel_z_mean: float = 2.0           # carried through to inject_hot_floor
      vel_xy_sigma: float = 0.5
      x_layout: str = "log"             # "log" places resonators along x by log(f),
                                        # so neighbour-frequency quanta are spatial
                                        # neighbours at the floor (helps potential
                                        # F3 binding); alt = "uniform"

  class Cochlea:
      def __init__(self, cfg: CochleaConfig, rng: np.random.Generator | None = None): ...
      def step(self, audio_sample: float) -> None:
          # advance bank by one sample
      def injector_for(self, quanta, grid, audit) -> Injector:
          # returns closure that, when called as injector(quanta, grid),
          # uses self.bank.y to decide how many quanta to inject per
          # resonator on this tick, calls inject_hot_floor for each,
          # records into audit, returns total energy injected.
  ```

  Key contract: `injector_for` returns a closure compatible with the `Injector = Callable[[Quanta, Grid], float]` type from `world/flux/dynamics.py`. The closure consumes the bank's *current* `y` state — it does NOT advance the bank. The caller must call `cochlea.step(sample)` once per tick BEFORE invoking the injector. (Document this loudly. Don't merge advance + inject; that couples the two state machines and makes time-base bugs invisible.)

- [ ] **Step 3: Run** `uv run pytest tests/flux/test_cochlea.py -v`. Expect 8/8 pass.

- [ ] **Step 4: Commit** `flux F2 task 3: cochlea + log-spaced resonator bank`.

---

## Task 4: Synthesis — inverse path

**Files:**
- Create: `agent/flux/synthesis.py`
- Extend: `tests/flux/test_synthesis.py` (unit tests; round-trip lives in Task 6)

The synth bank has the SAME centres as the cochlea bank (constructed via `make_log_spaced_centres`). Each tick:

1. Find alive free quanta with `z < synth_read_zone`.
2. For each such quantum, find the resonator whose `log2(f0)` is within `freq_match_tol_octaves` of `log2(quantum.freq)`. If multiple, distribute proportionally by inverse-octave-distance.
3. Add the quantum's energy as a drive impulse into that resonator(s) for this tick.
4. Advance the bank one sample (re-uses `Resonator2ndOrder.step`).
5. Output sample = `synth_gain * sum(bank.y)` (summed waveform across all resonators).

Optional bound-node path: if `step_with_nodes(nodes, quanta, grid)` is called and `nodes` is non-empty, each bound node within `synth_read_zone` of the floor adds drive `nodes.energy[n]` to the resonator matching its dominant constituent frequency. This is the spec §5.7 "node firings cause amplitude excitations" path. F2 ships it but the Task 6 acceptance test doesn't require it to fire.

- [ ] **Step 1: Tests first.** `tests/flux/test_synthesis.py`:

  1. `test_synth_bank_centres_match_cochlea_centres` — `Synthesis(cfg)` and `Cochlea(cfg)` constructed with the same `(n, f_lo, f_hi)` produce identical `centres` arrays.
  2. `test_synth_zero_quanta_zero_output` — fresh substrate with no quanta; `Synthesis.step(quanta, grid)` returns 0.0.
  3. `test_synth_excites_correct_resonator` — inject one quantum with `freq=1000 Hz` at `z=0.5` (in read zone). After ~50 ticks of `Synthesis.step`, the 1 kHz bank resonator's `y` envelope must exceed the 100 Hz resonator's envelope by ≥5×.
  4. `test_synth_freq_match_tolerance_respected` — quantum at `freq=1100 Hz` with default `freq_match_tol_octaves=0.5` excites the nearest resonator (which is within tolerance); same quantum with `freq=5 Hz` excites NOTHING (well outside tolerance for any bank centre in [50, 8000]).
  5. `test_synth_step_is_read_only_on_energy` — record `quanta.energy.sum()` before and after 100 `Synthesis.step` calls. Sum unchanged within 1e-12. (Synthesis does not modify energy; only reads.)
  6. `test_synth_bound_node_path_smoke` — `Synthesis.step_with_nodes(nodes, quanta, grid)` with an empty `Nodes` collection equals the result of `Synthesis.step(quanta, grid)`. (Path exists, no-op when no nodes.)

- [ ] **Step 2: Implement `agent/flux/synthesis.py`** per the algorithm above. Single SoA bank backed by `Resonator2ndOrder`.

- [ ] **Step 3: Run** `uv run pytest tests/flux/test_synthesis.py -v -k "not roundtrip"`. Expect 6/6 unit tests pass; round-trip test is added in Task 6.

- [ ] **Step 4: Commit** `flux F2 task 4: synthesis bank + free-quanta read path`.

---

## Task 5: `agent/flux/__init__.py` re-exports + audit wiring

**Files:** Modify `agent/flux/__init__.py`.

- [ ] **Step 1:** Re-export `Cochlea`, `CochleaConfig`, `Synthesis`, `SynthesisConfig`, plus the resonator helpers (`make_log_spaced_centres`, `Resonator2ndOrder`). Build `__all__`.

- [ ] **Step 2:** Add module docstring describing the F2 surface: cochlea drives injection, synthesis reads near-floor quanta, both share a bank topology, neither modifies binding/decay/plasticity.

- [ ] **Step 3:** Run `python -c "from agent.flux import Cochlea, Synthesis; print('ok')"`. Expect no ImportError.

- [ ] **Step 4: Commit** `flux F2 task 5: agent.flux re-exports`.

---

## Task 6: 1 kHz tone-burst round-trip — F2 acceptance test

**Files:** Append to `tests/flux/test_synthesis.py`.

This is the binary test pre-registered in §9 of the spec and the heart of the F2 falsifier.

Protocol:

1. Construct a substrate with default F1c thermal config (`ThermalConfig(buoyancy_g=2.0, damping_mu=0.5, ...)`) + `cube_dims=(20, 20, 40)`.
2. Construct `Cochlea(cfg)` and `Synthesis(cfg)` sharing the same config bank.
3. Synthesise a 100 ms, 1 kHz sinusoid at amplitude 1.0, sampled at 16 kHz → 1600 samples of audio.
4. Pad with 100 ms of silence after (1600 samples zeros).
5. For each of the 3200 samples:
   a. `cochlea.step(audio_sample)` — advance cochlea bank.
   b. `tick(quanta, grid, dt=1/16000, injector=cochlea.injector_for(...), thermal_cfg=tcfg)` — substrate step.
   c. `out_sample = synthesis.step(quanta, grid)` — synth bank advance + readout.
   d. Append `out_sample` to `recorded[]`.
6. Take FFT of `recorded[1600:3200]` (the 200 ms window starting at burst onset — captures ringing and tail).
7. The dominant non-DC bin's centre frequency must be within ±20% of 1000 Hz.

- [ ] **Step 1: Write the test:**

  ```python
  @pytest.mark.slow
  def test_F2_round_trip_1kHz_burst_dominant_bin_within_20pct():
      """F2 acceptance: 1 kHz audio in → 1 kHz dominant out.

      Spec §9 F2 binary contract. This is the entire F2 falsifier.
      """
      from agent.flux import Cochlea, CochleaConfig, Synthesis, SynthesisConfig
      from world.flux import Quanta, Grid, EnergyAuditor, tick
      from world.flux.thermal import ThermalConfig
      cfg_coc = CochleaConfig(n_cochlea=64, f_lo=50.0, f_hi=8000.0,
                              audio_sample_rate=16000.0, Q=8.0,
                              inject_gain=5.0)
      cfg_syn = SynthesisConfig(n_cochlea=64, f_lo=50.0, f_hi=8000.0,
                                audio_sample_rate=16000.0, Q=8.0,
                                synth_gain=1.0, synth_read_zone=2.0,
                                freq_match_tol_octaves=0.5)
      LX, LY, LZ = 20, 20, 40
      q = Quanta(max_quanta=100_000)
      g = Grid(dims=(LX, LY, LZ), voxel_size=1.0, T_smoothing=0.1)
      audit = EnergyAuditor(quanta=q, tol=1e-9)
      audit.record_initial()
      tcfg = ThermalConfig(buoyancy_g=2.0, damping_mu=0.5,
                           T_hot_floor=5.0, T_cold_ceiling=0.0)
      coc = Cochlea(cfg_coc)
      syn = Synthesis(cfg_syn)
      fs = 16000.0
      dt = 1.0 / fs
      f0 = 1000.0
      n_burst = int(0.1 * fs)
      n_tail = int(0.1 * fs)
      import numpy as np
      tt = np.arange(n_burst) / fs
      audio = np.concatenate([np.sin(2 * np.pi * f0 * tt),
                              np.zeros(n_tail)])
      recorded = np.zeros(audio.shape, dtype=np.float64)
      for k, sample in enumerate(audio):
          coc.step(sample)
          tick(q, g, dt=dt,
               injector=coc.injector_for(q, g, audit),
               thermal_cfg=tcfg)
          recorded[k] = syn.step(q, g)
      audit.check()  # T1 conservation across the round-trip
      window = recorded[n_burst - 200: n_burst + n_tail]  # 1400 .. 3200
      spectrum = np.abs(np.fft.rfft(window - window.mean()))
      freqs = np.fft.rfftfreq(window.size, d=dt)
      # skip DC
      k_peak = int(1 + np.argmax(spectrum[1:]))
      peak_freq = freqs[k_peak]
      tol = 0.20 * f0
      assert abs(peak_freq - f0) <= tol, (
          f"F2 round-trip: peak at {peak_freq:.1f} Hz, expected {f0:.1f} Hz "
          f"±{tol:.1f} Hz. spectrum peak amp = {spectrum[k_peak]:.4f}, "
          f"recorded.rms = {window.std():.4e}. Calibrate inject_gain / "
          f"synth_gain / Q / freq_match_tol_octaves; log to phase-log."
      )
  ```

  The test is marked `@pytest.mark.slow` because 3200 ticks on a 20×20×40 cube takes 30–90 s on Apple Silicon. CI baseline `pytest -m "not slow"` skips it; postflight's verdict runs the full suite incl. slow markers.

- [ ] **Step 2: Run** `uv run pytest tests/flux/test_synthesis.py::test_F2_round_trip_1kHz_burst_dominant_bin_within_20pct -v`. Likely fails first try.

- [ ] **Step 3: Up to 5 calibration sweeps** if Task 6 fails. Cheapest → most expensive:
  1. `inject_gain` — too low = no quanta, too high = T1 audit headroom blown. Sweep 1, 2, 5, 10, 20.
  2. `Q_resonator` — sharper Q = sharper output peak but slower ring-up. Sweep 4, 8, 16.
  3. `freq_match_tol_octaves` — wider = more quanta couple to the right resonator, but neighbours bleed in. Sweep 0.25, 0.5, 1.0.
  4. `synth_read_zone` — wider = more quanta sampled per output, but stale air-borne quanta dilute the signal. Sweep 1.0, 2.0, 4.0 voxels.
  5. `audio amplitude` — bump input from 1.0 to 2.0 if the cochlea is starved. Note in phase-log; the spec doesn't lock amplitude.

  Document each sweep in `docs/flux/phase-log.md` per the F1a/F1b/F1c pattern.

- [ ] **Step 4: Commit** `flux F2 task 6: 1 kHz round-trip passes` once green.

- [ ] **Step 5: BLOCKER** — if Task 6 fails after 5 sweeps, escalate. The cochlea–synthesis pipeline as specced may need a different free-quanta-to-resonator coupling (e.g. coupling via *flux through* a resonator's spatial cell rather than nearest-by-frequency), or the synthesis read zone needs to be promoted from floor-only to whole-cube. Either is a spec deviation — write to `~/.eqmod/autopilot/HUMAN_NEEDED.md` and STOP. Do not retune the ±20% threshold.

---

## Task 7: Verify T1–T4 + legacy regression

The cochlea + synthesis additions live in `agent/flux/`. The `tick` path in `world/flux/dynamics.py` is unchanged from F1c (injector signature already supports any closure). So T1–T4 should be unaffected. Verify anyway.

- [ ] **Step 1: Run** `uv run pytest tests/flux/ -v`. All F0/F1a/F1b/F1c tests (≈87 pre-F2 + 8 cochlea + 6 synthesis = ≈101) plus the slow round-trip should pass.
- [ ] **Step 2: Run legacy** `uv run pytest -m "not slow"`. Expect 382 pass.
- [ ] **Step 3:** If anything regresses, the likely cause is an accidental import side effect at module load (e.g. the `Cochlea` constructor allocating shared state). Bisect.

---

## Task 8: __init__ status update + README + F2 close

**Files:**
- Modify: `agent/flux/__init__.py` (re-exports complete after Task 5)
- Modify: `README.md`
- Modify: `docs/flux/phase-log.md`

- [ ] **Step 1: README "Two substrates" status line:**

  ```
  Status as of <date>: F0 + F1a + F1b + F1c + F2 complete
  (Phase 1 thermodynamic substrate done; cochlea + synthesis driving
  1 kHz round-trip). F3 (learning as flux reconfiguration) is next.
  ```

- [ ] **Step 2: Phase-log F2-close entry**: tasks summary, final CochleaConfig + SynthesisConfig, measured FFT peak frequency, T1 audit residual, n quanta peak, wallclock for the round-trip test.

- [ ] **Step 3: Run** `uv run pytest tests/flux/ -v` (all green) and `uv run pytest -m "not slow"` (382 + new fast tests).

- [ ] **Step 4: Commit** `flux F2 complete: cochlea + synthesis + 1 kHz round-trip`.

---

## Notes for autonomous execution

- **F2's binary contract is unusually expensive** (3200 ticks × 20×20×40 cube ≈ 50M voxel-tick-equivalents). Budget ~90 s wallclock for the round-trip test alone. If it takes longer, downsize `cube_dims` to (16, 16, 32) before sweeping the gain parameters.
- **The cochlea is fixed, by spec.** Resist any urge to "learn" the resonator centres from a calibration signal. Spec §5.6 is explicit: the bank is biological-fixed-analog and learning happens above it, not in it.
- **Energy conservation is the silent killer.** The cochlea injects new quanta; the auditor must see those injections via `record_injection`. If T1 fails after F2, the most likely cause is a missed `audit.record_injection` call inside `injector_for`. Check that first.
- **Synthesis must not be a state detector.** Spec §5.7 says synthesis is the inverse of the cochlea — quanta near the floor excite the resonator bank in reverse. It is NOT a "summarise what just happened" decoder. Test 5 in Task 4 enforces that synthesis is read-only on energy; if anyone introduces a path where synthesis "absorbs" a quantum to produce its sample, that's a state detector and a charter violation under the negative-controls rule from the autopilot charter.
- **Bound-node-driven synthesis is optional in F2.** The 1 kHz tone burst probably doesn't form bound nodes (no second-frequency, no temporal coherence beyond one harmonic). The `step_with_nodes` path is wired so that R-5 (F3 learning) can exercise it without re-touching this file. Don't gate Task 6 on the bound-node path firing.
- **Frequency tagging:** the F1c quanta already carry a `freq` scalar field (spec §5.2). F2 uses it. If R-3 finds the field is being clobbered somewhere in the substrate, that's a pre-existing bug and the fix is in scope (it's the same class of silent-pass guard the F3b bug occupied — a never-fail test).
- **No new world/flux/ code.** F2 is an agent-side wiring of an existing substrate. If R-3 finds itself editing `world/flux/dynamics.py` or `world/flux/quantum.py`, stop and reread this plan's "File structure (locked decisions)" — that's a deviation.
