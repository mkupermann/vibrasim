# Flux Substrate F3 — Learning-as-Flux-Reconfiguration

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal.** Falsify the claim that the flux substrate exhibits learning under sustained patterned input. F3 does NOT introduce a new weight-update rule. The learning rule is already in the substrate — it is spec §5.5's flux-monotone bridge plasticity, which has been live in code since F1b. F3 commits the rule to a falsification: after a long exposure to a repeated audio pattern via the cochlea, the substrate's surviving bridge topology must be **frequency-localised around the training pattern's spectrum**; on a matched-wallclock substrate driven by spectrally-flat white noise through the SAME cochlea, the same topology metric must fail. If both pass, the metric is a state detector, not a learning signal — verdict NULL.

F3 closes when:

- a repeated 1 kHz tone-burst pattern through the cochlea produces surviving bridges whose endpoint-node frequency distribution is concentrated near `log(1000)` above the pre-registered threshold (`tests/flux/test_learning.py`)
- a matched-wallclock substrate driven by white noise through the SAME cochlea bank does NOT reach the same threshold (`tests/flux/test_learning_negative_control.py`)
- T1 conservation, T2 Bénard, T3 crystallization, T4 decay all still pass

**Why this is the right F3.** Spec §3 says "Structures kondensieren wo sie diesen Fluss effizienter kanalisieren als kein Struktur" — bridges that channel actual flux persist; bridges that don't, decay. Spec §5.5 operationalises that as one monotone-in-flux rule:

```
w(t+1) = w(t) + γ · flux_through(t) − λ · max(0, flux_min − flux_through(t))
```

This is **not** STDP (no pre-/post-synaptic spike timing), **not** Hebbian (no pre-post co-activation pairing — flux through a bridge is a single per-edge quantity, not a coincidence detector on its endpoints), **not** BTSP (no eligibility trace gated by a global plateau signal). It is path-monotone integration of flux along an edge, with a deficit-decay term. Under sustained patterned input the bridges along the pattern's flux path accumulate weight and survive the pruner; bridges off that path stay below `flux_min` and die. That is the learning mechanism, derived directly from the single flux principle. F3's job is to take that mechanism out of the unit-test regime (single-tick, hand-built bridges in `tests/flux/test_plasticity.py`) and into the regime where many ticks of patterned audio produce a measurable topology signature — and to falsify it against a matched-wallclock spectrally-flat control on the same cochlea.

**Architecture sketch — what changes vs F2 and what doesn't.**

- **No new physics module.** No new file under `world/flux/`. The plasticity, decay, binding, and bridge layers stay exactly as F1b/F1c left them. F3 is a *test phase*, not a substrate-extension phase.
- **One new agent-layer driver.** `agent/flux/learning_run.py` orchestrates a learning run: it spins up a `Cochlea`, drives it from a synthetic waveform generator (1 kHz tone bursts for training, gaussian-white for control), steps the substrate for `n_ticks_train` ticks under the F1b plasticity+decay loop, then returns the substrate state for metric computation.
- **One new metric module.** `agent/flux/learning_metric.py` computes the **frequency-localisation index `f_loc`** — the fraction of alive bridges whose two endpoint nodes both have `node.frequency` within ±`band_log_hz` of the training-pattern centre `log(f_train_hz)`. Definition is purely substrate-side; it never reads the input waveform.
- **Two new test files.** `tests/flux/test_learning.py` runs the trained-substrate experiment and asserts `f_loc >= f_loc_thresh_train`. `tests/flux/test_learning_negative_control.py` runs the matched-wallclock white-noise experiment and asserts `f_loc < f_loc_thresh_control`. Both tests share the SAME helper (`agent/flux/learning_run.py`) — only the input-waveform generator differs.
- **Matched control means matched everything except the input waveform.** Same `BindingConfig`, same `PlasticityConfig`, same `DecayConfig`, same `ThermalConfig`, same `CochleaConfig`, same grid, same `n_ticks_train`, same RNG seed. The cochlea is the same fixed bank in both cases. The only thing that differs is the time series of audio samples fed into the cochlea: a deterministic tone-burst pattern in training, a gaussian-white sequence in control (seeded so the noise is reproducible).

**Tech stack:** Python 3.13, numpy, pytest. No new dependencies. Reuses the F2 `Cochlea`/`CochleaConfig`/`step_resonators`/`cochlea_inject` API exactly. Synthesis is NOT in the F3 loop — F3 is input-side only; we measure the substrate's topology, not its output waveform.

**Spec reference:** `docs/superpowers/specs/2026-05-10-flux-substrate-design.md` — §3 (the single principle), §5.4 (structures persist while flux passes through them), §5.5 (the monotone-flux plasticity rule), §5.6 (fixed cochlea), §9 F3 row of the roadmap ("Tier 1: log-likelihood improvement of trained vs untrained on 60-min audio"). F3 in this plan is a STRUCTURE-LEVEL falsification — it is the precursor to the full Tier-1 audio LLR test, which lives in the training-phase items R-6/R-7/R-8 and is not in F3 scope.

**Estimated wallclock:** 6–10 weeks solo per spec §9 F3 row; compressed under autonomous-build because the substrate primitives are already in place.

**Acceptance contract (binary):**
- `uv run pytest tests/flux/test_learning.py -v` passes — covers: (a) `learning_run` constructs a trained substrate without raising, (b) the trained substrate has at least `n_bridges_min_alive` alive bridges at end of run, (c) `f_loc(trained_substrate) >= f_loc_thresh_train` (pre-registered numeric threshold below)
- `uv run pytest tests/flux/test_learning_negative_control.py -v` passes — covers: (a) the matched-wallclock control run with white-noise input completes on the same `n_ticks_train` and same RNG, (b) the control substrate also has at least `n_bridges_min_alive_control` alive bridges (otherwise the metric is undefined, which we treat as a fail-shut FAIL not a pass), (c) `f_loc(control_substrate) < f_loc_thresh_control`, AND (d) `f_loc(trained) − f_loc(control) >= margin_min` (the separating margin — both gates must hold, individual + relative)
- `uv run pytest tests/flux/test_conservation.py -v` still passes (T1: F3 adds no energy paths; it only invokes the existing F2 cochlea-injection auditor hook)
- `uv run pytest tests/flux/test_benard.py -v` still passes (T2: cochlea is OFF in T2; substrate-only physics unchanged)
- `uv run pytest tests/flux/test_crystallization.py -v` still passes (T3)
- `uv run pytest tests/flux/test_decay.py -v` still passes (T4)
- `uv run pytest -m "not slow"` still passes (legacy regression baseline holds)

These pytest paths — `tests/flux/test_learning.py` and `tests/flux/test_learning_negative_control.py` — are the pre-registered F3 acceptance targets. R-5 implements against this contract.

**Pre-registered numeric thresholds (locked at commit time of this plan; no post-hoc retuning allowed):**

| Symbol | Value | Meaning |
|---|---|---|
| `f_train_hz` | `1000.0` | Training tone-burst centre frequency. Falls inside the cochlea's `[50, 8000]` log-spaced band, near a resonator slot, and well below Nyquist. |
| `band_log_hz` | `0.25` | Frequency-localisation half-window in log-Hz. `±0.25` around `log(1000) ≈ 6.908` covers roughly 780–1280 Hz — about ±25 % around the training tone. Wide enough to absorb cochlea-Q smearing into neighbouring slots; narrow enough to be a real specificity test. |
| `n_ticks_train` | `10000` | Substrate ticks per run. Long enough for plasticity to integrate flux into surviving bridges; short enough that a session fits in the 24 h R-5 wallclock budget (R-5 will tune this if needed within the pre-registered upper bound `n_ticks_train_max = 30000`). |
| `f_loc_thresh_train` | `0.30` | Trained substrate must reach `f_loc >= 0.30`. Calibration justification: by mass-balance of the cochlea-bank routing, the 1 kHz tone deposits ≥ 40 % of its injected quanta into resonator slots within `band_log_hz` of `log(1000)` at the F2-locked `peak_floor=2.0`; F3's claim is that ≥ 75 % of THAT fraction transduces into bridges that survive pruning — yielding ≥ 0.30 on the joint metric. Lower than 0.30 means the substrate is not channelling the input. |
| `f_loc_thresh_control` | `0.20` | White-noise control must stay BELOW `f_loc < 0.20`. With a flat input spectrum, ≤ 20 % of quanta fall in the `±band_log_hz` window simply because that window covers ≈ 16 % of the 50–8000 Hz log-range (computed: `2 * 0.25 / log(8000/50) ≈ 0.10` on the bridge population, leaving a 2× safety margin for cochlea-slot quantisation). |
| `margin_min` | `0.10` | Trained − Control must be `>= 0.10`. Two-gate design: trained crosses an absolute floor AND beats control by a margin. This rules out the "control accidentally drifts low so trained looks high in comparison" failure mode of single-gate designs. |
| `n_bridges_min_alive` | `30` | Trained substrate must end with ≥ 30 alive bridges. Below this, `f_loc` is too noisy to interpret — verdict NULL not PASS. |
| `n_bridges_min_alive_control` | `10` | Control substrate must end with ≥ 10 alive bridges. Below this, the control failed to function as a control (silent-pass risk) — verdict NULL not PASS. The asymmetric floor (`30` vs `10`) reflects that flat-spectrum noise SHOULD produce fewer surviving bridges than peaked input — but not zero. |
| `seed_train` | `4242` | Locked RNG seed for the trained run. |
| `seed_control` | `4242` | SAME locked RNG seed for the control run — only the input waveform generator differs. (The white-noise generator has its own internal sample-level seed, fixed to `9999`.) |

These thresholds are pre-registered now and must NOT be moved post-hoc to make a failed R-5 run pass. If R-5 cannot meet them with a fair attempt, the verdict is NULL with a postmortem — exactly as `marker_protocol.md` requires.

---

## What F3 deliberately defers

| Concept | Status in F3 | Where it lands |
|---|---|---|
| Tier-1 LLR test on real 60-min audio (spec §9 F3) | NOT in F3 R-4/R-5 scope | Training-phase items R-6/R-7/R-8 (corpus + run) |
| Multi-tone / phonemic input | NOT in scope | R-6+ once corpus exists |
| Synthesis-side metric (output spectrum after training) | NOT in scope | R-6+ (Tier-1 LLR uses this) |
| Phoneme probe (Tier 2) | NOT in scope | F4 (post-vacation) |
| Attention reallocate / PE-weighted compute | NOT in scope | F4+ |
| Learning-rule reformulation | EXPLICITLY out of scope | The rule is spec §5.5 as built in F1b — F3 falsifies the existing rule, not a new one. |
| Conscious choice of input — adversarial / curriculum | NOT in scope | Future |

F3 is the structure-level falsification. The substantive emergence claim ("the substrate develops topology that reflects the input pattern's statistics") is what F3 tests. Whether the substrate THEN generates a likelihood-improving output waveform is a Tier-1 question that lives in the training phase.

---

## Open calibration choices

These are the knobs that R-5's implementation session may sweep within the pre-registered ranges. Defaults below are the starting point; any move requires a phase-log entry naming the swept variable, the old value, the new value, and which threshold (if any) it pushed against.

| Param | Default | Range | Purpose |
|---|---|---|---|
| `burst_duration_ms` | `200` | `[100, 400]` | Length of each 1 kHz tone burst in the training waveform. |
| `silence_duration_ms` | `200` | `[100, 400]` | Inter-burst silence in training. Total period = burst + silence. |
| `burst_amplitude` | `1.0` | `[0.5, 2.0]` | Peak amplitude of the training tone. Affects per-tick injection count via cochlea peak. |
| `binding_alpha` | F1b-locked | F1b-locked | Pred-coherence gain. F3 does NOT retune binding — it inherits from F1b. |
| `binding_beta` | F1b-locked | F1b-locked | Temperature-gate gain. F3 does NOT retune. |
| `T_crit` | F1b-locked | F1b-locked | Binding T-cap. F3 inherits. |
| `plasticity_gamma` | F1b-locked | F1b-locked | Flux-strengthen rate. F3 inherits. |
| `plasticity_lam` | F1b-locked | F1b-locked | Deficit-decay rate. F3 inherits. |
| `plasticity_flux_min` | F1b-locked | F1b-locked | Bridge-flux deficit threshold. F3 inherits. |
| `cochlea_inject_gain` | F2-locked (`1.0`) | F2-locked | Cochlea→injection mapping. F3 inherits F2's tuned value. |
| `cochlea_peak_floor` | F2-locked (`2.0`) | F2-locked | Cochlea peak noise-floor subtraction. F3 inherits. |
| `n_ticks_train` | `10000` | `[5000, 30000]` | Substrate ticks per run. Upper bound is the pre-registered ceiling — going above 30000 is a protocol breach. |
| `grid_dims` | F1b-locked | F1b-locked | Grid geometry. F3 uses the same grid the F1b/F1c tests use. |

**Calibration discipline.** R-5 may sweep `burst_duration_ms`, `silence_duration_ms`, `burst_amplitude`, and `n_ticks_train` up to **5 sweeps** before escalating. Order of sweeps (use this exact order):

1. `n_ticks_train`: increase first (more integration time is the cheapest gain)
2. `burst_amplitude`: increase to push more quanta into the cochlea path
3. `burst_duration_ms` / `silence_duration_ms`: tune the duty cycle (shorter silence = more flux integration; too short = nothing decays so f_loc gets washed out)
4. If still NULL after 5 sweeps: STOP, write postmortem to LOGBOOK, mark R-5 NULL.

**Do NOT sweep:** binding, plasticity, decay, thermal, cochlea — those are F1b/F1c/F2-locked. Sweeping them would retrofit the substrate to the test, which is exactly what the pre-registration discipline forbids.

---

## File structure (locked decisions)

New files:

| Path | Responsibility |
|---|---|
| `agent/flux/learning_run.py` | `LearningRunConfig` dataclass + `make_training_waveform(cfg, n_samples) -> np.ndarray` + `make_control_waveform(cfg, n_samples) -> np.ndarray` + `run_learning_session(cfg, input_kind: Literal["train","control"]) -> LearningRunResult`. The `LearningRunResult` is a dataclass carrying `quanta`, `nodes`, `bridges`, `grid`, `tick_index`, plus the metric inputs (alive-bridge endpoint frequencies). |
| `agent/flux/learning_metric.py` | `frequency_localisation_index(bridges, nodes, f_train_hz, band_log_hz) -> float` — pure function over substrate state. Returns `f_loc ∈ [0, 1]`. Definition: `f_loc = #{alive bridges b : |nodes.frequency[b.src] − log(f_train_hz)| ≤ band_log_hz AND |nodes.frequency[b.dst] − log(f_train_hz)| ≤ band_log_hz} / #{alive bridges}`. If no alive bridges, returns `0.0`. |
| `tests/flux/test_learning.py` | F3 trained-run acceptance: builds a `LearningRunConfig` from F1b+F2 locked params + the pre-registered F3 thresholds, runs `run_learning_session(cfg, "train")`, asserts `n_bridges_alive >= n_bridges_min_alive` and `f_loc >= f_loc_thresh_train`. Also asserts T1 inline (energy conservation during the run). |
| `tests/flux/test_learning_negative_control.py` | F3 negative-control acceptance: builds the SAME `LearningRunConfig`, runs `run_learning_session(cfg, "control")`, asserts `n_bridges_alive >= n_bridges_min_alive_control`, `f_loc < f_loc_thresh_control`, AND `f_loc_trained − f_loc_control >= margin_min`. The trained-substrate result is recomputed within this test (not imported from `test_learning.py`) so the test is hermetic — but uses the SAME locked seed `seed_train=4242` so the trained run is byte-identical to the one in `test_learning.py`. |

Modified files:

| Path | What changes |
|---|---|
| `agent/flux/__init__.py` | Re-export `LearningRunConfig`, `LearningRunResult`, `run_learning_session`, `frequency_localisation_index`. |
| `docs/flux/phase-log.md` | F3-start, per-sweep, F3-close entries (one paragraph each per the F1a/F1b/F1c/F2 pattern). |
| `README.md` | One-line status update on F3. |

**Files explicitly NOT touched:**
- `world/flux/*` — no substrate physics changes. F3 is test-only.
- `world/flux/plasticity.py` — the learning rule is already in this file; F3 does not modify it.
- `agent/flux/cochlea.py` — the cochlea is FIXED per spec §5.6 and F2.
- `agent/flux/synthesis.py` — F3 does not read the synthesis layer; the metric is purely topology-side.
- `docs/marker_protocol.md` and `docs/marker_protocol_G20-G23_addendum.md` — frozen by autopilot charter.

**Conservation accounting note:** the F2 cochlea injection auditor hook is reused unchanged. F3 adds no new energy paths. Audit assertions inside `run_learning_session` are inherited from `dynamics.tick`. The trained and control runs both balance their books through the same `audit.record_injection` / `audit.record_decay_heat` / `audit.record_binding_heat` channels.

---

## Task 1: F3 start — phase-log entry + plan reference

**Files:** Modify `docs/flux/phase-log.md`.

- [ ] Append the F3-start block describing: scope (test phase, no new physics), the locked thresholds table (copy from this plan's "Pre-registered numeric thresholds" section), the deferred items, and the locked pytest acceptance paths (`tests/flux/test_learning.py`, `tests/flux/test_learning_negative_control.py`). Reference this plan file by full path.
- [ ] Commit: `flux F3 start: phase-log entry`.

---

## Task 2: Waveform generators (pure functions, no substrate)

**Files:**
- Create: `agent/flux/learning_run.py` (waveform generators + config dataclass only — the run orchestrator lands in Task 5)
- Create: `tests/flux/test_learning.py` (waveform-section tests only — substrate run section lands in Task 6)

The two waveform generators must produce numpy float64 arrays of shape `(n_samples,)` sampled at `cfg.sample_rate_hz`. Training: a periodic burst of a 1 kHz sine, on for `burst_duration_ms`, off for `silence_duration_ms`, repeating to fill `n_samples`. Control: gaussian white noise scaled so its RMS equals the training waveform's RMS over the same `n_samples` (energy-matched). Both are deterministic — training is closed-form (no randomness), control uses a locked `numpy.random.default_rng(9999)`.

- [ ] **Step 1: Tests first.**

```python
"""Tests for F3 learning waveform generators."""
from __future__ import annotations
import numpy as np
import pytest

from agent.flux.learning_run import (
    LearningRunConfig, make_training_waveform, make_control_waveform,
)


def test_training_waveform_has_peak_at_1khz():
    cfg = LearningRunConfig()
    sr = cfg.sample_rate_hz
    n = sr  # 1 second
    x = make_training_waveform(cfg, n_samples=n)
    spec = np.abs(np.fft.rfft(x))
    freqs = np.fft.rfftfreq(n, d=1.0 / sr)
    peak_hz = freqs[int(np.argmax(spec))]
    assert 800.0 < peak_hz < 1200.0, f"training waveform peak at {peak_hz} Hz, expected ~1 kHz"


def test_training_waveform_is_deterministic():
    cfg = LearningRunConfig()
    a = make_training_waveform(cfg, n_samples=4000)
    b = make_training_waveform(cfg, n_samples=4000)
    assert np.allclose(a, b), "training waveform must be deterministic"


def test_control_waveform_has_flat_spectrum():
    cfg = LearningRunConfig()
    sr = cfg.sample_rate_hz
    n = 4 * sr  # 4 seconds for FFT smoothness
    x = make_control_waveform(cfg, n_samples=n)
    spec = np.abs(np.fft.rfft(x))
    freqs = np.fft.rfftfreq(n, d=1.0 / sr)
    band = (freqs >= 200) & (freqs <= 6000)
    in_band = spec[band]
    # Coefficient of variation: std / mean of the magnitude spectrum within
    # the cochlea's response band. A flat (white) spectrum has CV well under
    # 1.5; a tonal signal has CV >> 10.
    cv = float(np.std(in_band) / np.mean(in_band))
    assert cv < 1.5, f"control waveform CV={cv:.2f}, expected flat (CV<1.5)"


def test_control_waveform_energy_matches_training():
    cfg = LearningRunConfig()
    n = 16000  # 1 second
    train = make_training_waveform(cfg, n_samples=n)
    ctrl = make_control_waveform(cfg, n_samples=n)
    rms_train = float(np.sqrt(np.mean(train**2)))
    rms_ctrl = float(np.sqrt(np.mean(ctrl**2)))
    # Energy-matched to within 5 %
    assert abs(rms_train - rms_ctrl) / rms_train < 0.05, (
        f"RMS mismatch: train={rms_train:.4f}, ctrl={rms_ctrl:.4f}"
    )


def test_control_waveform_is_deterministic():
    cfg = LearningRunConfig()
    a = make_control_waveform(cfg, n_samples=4000)
    b = make_control_waveform(cfg, n_samples=4000)
    assert np.allclose(a, b), "control waveform must be deterministic for matched seeds"
```

- [ ] **Step 2: Implement** `agent/flux/learning_run.py` with the `LearningRunConfig` dataclass (carrying ALL the pre-registered thresholds + the F1b/F2 locked configs by composition) and the two `make_*_waveform` functions. White-noise RMS-matching: compute the training RMS first, then scale the white-noise draw to match.

- [ ] **Step 3: Run** `uv run pytest tests/flux/test_learning.py -v -k waveform`. Expect 5/5 pass.

- [ ] **Step 4: Commit** `flux F3 task 2: training + control waveform generators`.

---

## Task 3: Frequency-localisation metric (pure function over substrate state)

**Files:**
- Create: `agent/flux/learning_metric.py`
- Modify: `tests/flux/test_learning.py` (add metric-section tests)

The metric is purely topology-side: it reads `bridges.alive`, `bridges.src`, `bridges.dst`, and `nodes.frequency` — no audio, no injection history, no flux counts. Definition:

```
band_centre = log(f_train_hz)
ok = lambda slot: abs(nodes.frequency[slot] - band_centre) <= band_log_hz
n_alive_bridges = bridges.alive.sum()
if n_alive_bridges == 0:
    return 0.0
in_band = sum(1 for b_slot in alive_bridge_slots
              if ok(bridges.src[b_slot]) and ok(bridges.dst[b_slot]))
return in_band / n_alive_bridges
```

A bridge counts as "in band" only if BOTH endpoint nodes have log-frequency within `±band_log_hz` of the training centre. This is stricter than counting bridges with at least one in-band endpoint, and is the natural definition for "bridges along the training-pattern flux path".

- [ ] **Step 1: Tests.**

```python
def test_floc_zero_when_no_bridges():
    from world.flux.bridges import Bridges
    from world.flux.structures import Nodes
    from agent.flux.learning_metric import frequency_localisation_index
    n = Nodes(max_nodes=4); b = Bridges(max_bridges=4)
    assert frequency_localisation_index(b, n, f_train_hz=1000.0, band_log_hz=0.25) == 0.0


def test_floc_one_when_all_bridges_in_band():
    from world.flux.bridges import Bridges
    from world.flux.structures import Nodes
    from agent.flux.learning_metric import frequency_localisation_index
    n = Nodes(max_nodes=4); b = Bridges(max_bridges=4)
    log_1k = float(np.log(1000.0))
    n.add(pos=(0, 0, 0), energy=1.0, freq=log_1k, born_tick=0)
    n.add(pos=(1, 0, 0), energy=1.0, freq=log_1k + 0.05, born_tick=0)
    b.add(src=0, dst=1, weight=1.0, born_tick=0)
    floc = frequency_localisation_index(b, n, f_train_hz=1000.0, band_log_hz=0.25)
    assert floc == pytest.approx(1.0)


def test_floc_zero_when_all_bridges_out_of_band():
    from world.flux.bridges import Bridges
    from world.flux.structures import Nodes
    from agent.flux.learning_metric import frequency_localisation_index
    n = Nodes(max_nodes=4); b = Bridges(max_bridges=4)
    log_4k = float(np.log(4000.0))
    n.add(pos=(0, 0, 0), energy=1.0, freq=log_4k, born_tick=0)
    n.add(pos=(1, 0, 0), energy=1.0, freq=log_4k, born_tick=0)
    b.add(src=0, dst=1, weight=1.0, born_tick=0)
    floc = frequency_localisation_index(b, n, f_train_hz=1000.0, band_log_hz=0.25)
    assert floc == 0.0


def test_floc_partial_when_mixed():
    """Two bridges; one in-band, one out-of-band. f_loc should be 0.5."""
    from world.flux.bridges import Bridges
    from world.flux.structures import Nodes
    from agent.flux.learning_metric import frequency_localisation_index
    n = Nodes(max_nodes=4); b = Bridges(max_bridges=4)
    log_1k = float(np.log(1000.0))
    log_4k = float(np.log(4000.0))
    n.add(pos=(0, 0, 0), energy=1.0, freq=log_1k, born_tick=0)
    n.add(pos=(1, 0, 0), energy=1.0, freq=log_1k, born_tick=0)
    n.add(pos=(0, 1, 0), energy=1.0, freq=log_4k, born_tick=0)
    n.add(pos=(1, 1, 0), energy=1.0, freq=log_4k, born_tick=0)
    b.add(src=0, dst=1, weight=1.0, born_tick=0)
    b.add(src=2, dst=3, weight=1.0, born_tick=0)
    floc = frequency_localisation_index(b, n, f_train_hz=1000.0, band_log_hz=0.25)
    assert floc == pytest.approx(0.5)


def test_floc_requires_both_endpoints_in_band():
    """A bridge with one endpoint in-band, one out, must NOT count."""
    from world.flux.bridges import Bridges
    from world.flux.structures import Nodes
    from agent.flux.learning_metric import frequency_localisation_index
    n = Nodes(max_nodes=4); b = Bridges(max_bridges=4)
    log_1k = float(np.log(1000.0))
    log_4k = float(np.log(4000.0))
    n.add(pos=(0, 0, 0), energy=1.0, freq=log_1k, born_tick=0)
    n.add(pos=(1, 0, 0), energy=1.0, freq=log_4k, born_tick=0)
    b.add(src=0, dst=1, weight=1.0, born_tick=0)
    floc = frequency_localisation_index(b, n, f_train_hz=1000.0, band_log_hz=0.25)
    assert floc == 0.0  # one in, one out → fails the AND condition
```

- [ ] **Step 2: Implement** `agent/flux/learning_metric.py` with the pure function above.

- [ ] **Step 3: Run** `uv run pytest tests/flux/test_learning.py -v -k floc`. Expect 5/5 pass.

- [ ] **Step 4: Commit** `flux F3 task 3: frequency-localisation metric`.

---

## Task 4: Cochlea-injection wiring inside `run_learning_session`

**Files:**
- Modify: `agent/flux/learning_run.py` (add `run_learning_session` skeleton — the substrate-loop body lands in Task 5)
- Modify: `tests/flux/test_learning.py` (add a smoke test that `run_learning_session` constructs without raising)

This task ONLY wires the cochlea side. The substrate-loop body lands in Task 5.

- [ ] **Step 1: Define `LearningRunResult`** as a dataclass carrying `quanta`, `nodes`, `bridges`, `grid`, `tick_index`, `audit` (final auditor), `cfg` (the input `LearningRunConfig`). Reading `result.bridges` and `result.nodes` is all the metric and the tests need.

- [ ] **Step 2: Implement `run_learning_session(cfg, input_kind)` skeleton.**

```python
def run_learning_session(
    cfg: LearningRunConfig,
    input_kind: Literal["train", "control"],
) -> LearningRunResult:
    # 1. Pick the waveform generator
    n_audio_samples_total = cfg.n_ticks_train * cfg.cochlea_cfg.n_audio_samples_per_tick
    if input_kind == "train":
        waveform = make_training_waveform(cfg, n_samples=n_audio_samples_total)
    elif input_kind == "control":
        waveform = make_control_waveform(cfg, n_samples=n_audio_samples_total)
    else:
        raise ValueError(f"unknown input_kind: {input_kind}")
    # 2. Build the substrate
    rng = np.random.default_rng(cfg.seed_train if input_kind == "train" else cfg.seed_control)
    grid = Grid(dims=cfg.grid_dims, voxel_size=cfg.voxel_size)
    quanta = Quanta(max_quanta=cfg.max_quanta)
    nodes = Nodes(max_nodes=cfg.max_nodes)
    bridges = Bridges(max_bridges=cfg.max_bridges)
    audit = Auditor()
    bank = Cochlea(cfg.cochlea_cfg)
    # 3. Tick loop lives in Task 5; for Task 4 just return the empty state.
    return LearningRunResult(
        quanta=quanta, nodes=nodes, bridges=bridges, grid=grid,
        tick_index=0, audit=audit, cfg=cfg,
    )
```

- [ ] **Step 3: Smoke test.**

```python
def test_run_learning_session_constructs_without_raising():
    from agent.flux.learning_run import LearningRunConfig, run_learning_session
    cfg = LearningRunConfig(n_ticks_train=10)  # small for the smoke
    result = run_learning_session(cfg, input_kind="train")
    assert result.quanta is not None
    assert result.nodes is not None
    assert result.bridges is not None
```

- [ ] **Step 4: Run** `uv run pytest tests/flux/test_learning.py -v`. Expect 11/11 pass (5 waveform + 5 metric + 1 smoke).

- [ ] **Step 5: Commit** `flux F3 task 4: run_learning_session skeleton`.

---

## Task 5: Substrate loop body inside `run_learning_session`

**Files:**
- Modify: `agent/flux/learning_run.py` (replace the Task-4 stub with the real tick loop)

The tick loop must reuse `world.flux.dynamics.tick` with the F1b plasticity path enabled. Each tick consumes `cfg.cochlea_cfg.n_audio_samples_per_tick` audio samples; `step_resonators` advances the bank; `cochlea_inject` deposits quanta at the floor. Then `dynamics.tick` runs binding → decay → plasticity → pruning → temperature update, exactly as the existing F1b/F1c/F2 tests use it. NO synthesis read — F3 is input-side only.

- [ ] **Step 1: Implement the loop body** between `bank = Cochlea(cfg.cochlea_cfg)` and the `return`:

```python
audit_floor = cfg.audit_floor  # default 1e-9 * E_total tolerance from F1b
for tick_idx in range(cfg.n_ticks_train):
    chunk = waveform[
        tick_idx * cfg.cochlea_cfg.n_audio_samples_per_tick
        : (tick_idx + 1) * cfg.cochlea_cfg.n_audio_samples_per_tick
    ]
    step_resonators(bank, samples=chunk)
    e_injected = cochlea_inject(quanta, grid, bank, cfg.cochlea_cfg, rng=rng)
    audit.record_injection(e_injected)
    exported, binding_heat, decay_heat = dynamics.tick(
        quanta=quanta, grid=grid, dt=cfg.dt,
        injector=None,  # injection already happened above
        nodes=nodes, binding_cfg=cfg.binding_cfg,
        decay_cfg=cfg.decay_cfg, bridges=bridges,
        plasticity_cfg=cfg.plasticity_cfg,
        thermal_cfg=cfg.thermal_cfg,
        rng=rng, tick_index=tick_idx,
    )
    audit.record_export(exported)
    audit.record_binding_heat(binding_heat)
    audit.record_decay_heat(decay_heat)
return LearningRunResult(
    quanta=quanta, nodes=nodes, bridges=bridges, grid=grid,
    tick_index=cfg.n_ticks_train, audit=audit, cfg=cfg,
)
```

- [ ] **Step 2: Quick sanity smoke** — replace the `n_ticks_train=10` smoke from Task 4 with `n_ticks_train=200` and assert `result.tick_index == 200` and `result.audit.is_balanced(tol=audit_floor)`.

- [ ] **Step 3: Run** `uv run pytest tests/flux/test_learning.py -v -k constructs`. Expect smoke passes; total still 11/11.

- [ ] **Step 4: Commit** `flux F3 task 5: run_learning_session tick loop`.

---

## Task 6: F3 trained-run acceptance test

**Files:**
- Modify: `tests/flux/test_learning.py` (add the full-length trained-run acceptance test)

This is the pre-registered substantive proof of F3 part-1.

- [ ] **Step 1: Add the acceptance test.**

```python
@pytest.mark.slow
def test_F3_trained_substrate_develops_pattern_specific_topology():
    """Pre-registered F3 acceptance: substrate exposed to a repeated 1 kHz
    tone-burst pattern develops bridge topology concentrated around log(1000).
    Locked thresholds — DO NOT retune."""
    from agent.flux.learning_run import LearningRunConfig, run_learning_session
    from agent.flux.learning_metric import frequency_localisation_index

    cfg = LearningRunConfig()  # all F3 thresholds live in the defaults
    result = run_learning_session(cfg, input_kind="train")
    n_alive = int(result.bridges.alive.sum())
    assert n_alive >= cfg.n_bridges_min_alive, (
        f"trained run produced only {n_alive} alive bridges, need "
        f">= {cfg.n_bridges_min_alive} for f_loc to be a meaningful "
        f"measurement — verdict NULL not PASS"
    )
    floc = frequency_localisation_index(
        result.bridges, result.nodes,
        f_train_hz=cfg.f_train_hz, band_log_hz=cfg.band_log_hz,
    )
    assert floc >= cfg.f_loc_thresh_train, (
        f"trained substrate f_loc = {floc:.3f}, "
        f"pre-registered threshold {cfg.f_loc_thresh_train:.3f} — "
        f"verdict NULL not PASS. Bridges alive: {n_alive}. "
        f"Do NOT retune thresholds; they are locked by R-4 plan."
    )
    # Inline T1 — audit must balance
    assert result.audit.is_balanced(tol=cfg.audit_tol), (
        f"trained run violated T1 conservation: "
        f"residual={result.audit.residual():.6e}, tol={cfg.audit_tol:.6e}"
    )
```

- [ ] **Step 2: Run** `uv run pytest tests/flux/test_learning.py -v`. Expect 12/12 pass (or this test fails — go to Step 3).

- [ ] **Step 3: If it fails**, sweep within the pre-registered ranges (see "Calibration discipline" section). Document each sweep in `docs/flux/phase-log.md`. Up to 5 sweeps.

- [ ] **Step 4: If still failing after 5 sweeps**, write a NULL postmortem to `LOGBOOK.md` per the autopilot charter and STOP. Do not tighten thresholds, do not relax thresholds, do not change the metric.

- [ ] **Step 5: Commit** `flux F3 task 6: trained-run acceptance test PASSES` (only if it passes; otherwise commit the NULL postmortem and the sweep entries instead).

---

## Task 7: F3 negative-control acceptance test

**Files:**
- Create: `tests/flux/test_learning_negative_control.py`

The hermetic negative-control test. Recomputes BOTH the trained and control results inside the test (using locked seeds) so it can assert the relative `margin_min` gate without depending on test ordering.

- [ ] **Step 1: Write the negative-control test.**

```python
"""F3 negative-control acceptance.

Pre-registered by R-4 (plan docs/superpowers/plans/2026-05-16-flux-substrate-F3.md):

The same substrate, run for the same wallclock with the same RNG, driven
by spectrally-flat gaussian white noise through the SAME cochlea, must NOT
reach the frequency-localisation threshold that the trained run reaches.
If it does, the trained-run signal is a state detector, not a learning
finding — and F3 NULLs per the charter's negative-control rule.
"""
from __future__ import annotations
import numpy as np
import pytest

from agent.flux.learning_run import LearningRunConfig, run_learning_session
from agent.flux.learning_metric import frequency_localisation_index


@pytest.mark.slow
def test_F3_control_substrate_does_not_develop_pattern_specific_topology():
    cfg = LearningRunConfig()

    # Trained run (matched-wallclock baseline)
    trained = run_learning_session(cfg, input_kind="train")
    n_alive_train = int(trained.bridges.alive.sum())
    assert n_alive_train >= cfg.n_bridges_min_alive, (
        f"trained baseline produced only {n_alive_train} alive bridges; "
        f"the test cannot evaluate the negative control if the trained "
        f"substrate itself failed to form structure — verdict NULL"
    )
    floc_train = frequency_localisation_index(
        trained.bridges, trained.nodes,
        f_train_hz=cfg.f_train_hz, band_log_hz=cfg.band_log_hz,
    )

    # Negative control (white noise, same wallclock, same seed)
    control = run_learning_session(cfg, input_kind="control")
    n_alive_control = int(control.bridges.alive.sum())
    assert n_alive_control >= cfg.n_bridges_min_alive_control, (
        f"control run produced only {n_alive_control} alive bridges — "
        f"the control failed to function as a control (silent-pass risk) — "
        f"verdict NULL not PASS"
    )
    floc_control = frequency_localisation_index(
        control.bridges, control.nodes,
        f_train_hz=cfg.f_train_hz, band_log_hz=cfg.band_log_hz,
    )

    # Pre-registered absolute upper bound on control's f_loc
    assert floc_control < cfg.f_loc_thresh_control, (
        f"control substrate f_loc = {floc_control:.3f} >= "
        f"{cfg.f_loc_thresh_control:.3f}. The substrate appears to "
        f"concentrate bridges at log(1000) even with flat-spectrum input — "
        f"the trained-run metric is a state detector, not a learning "
        f"signal. Verdict NULL per autopilot charter."
    )
    # Pre-registered relative margin
    margin = floc_train - floc_control
    assert margin >= cfg.margin_min, (
        f"trained − control margin = {margin:.3f} < "
        f"{cfg.margin_min:.3f}. Trained may have crossed its floor "
        f"only because control drifted close to it; the separation is "
        f"not significant. Verdict NULL."
    )
```

- [ ] **Step 2: Run** `uv run pytest tests/flux/test_learning_negative_control.py -v`. Expect 1/1 pass. This call REUSES the trained run from Task 6 (same seed, same cfg, byte-identical result), so the trained-side `f_loc` will match exactly.

- [ ] **Step 3: If the control reaches `f_loc >= 0.20`**, the substrate's bridge-formation dynamics are systematically biased toward the 1 kHz cochlea slot regardless of input spectrum. That is a substrate finding to report in the phase-log; the verdict is NULL per the charter's negative-control rule. Do NOT raise `f_loc_thresh_control` — that retunes the test.

- [ ] **Step 4: Commit** `flux F3 task 7: negative-control acceptance test PASSES` (only if it passes; otherwise commit the NULL postmortem instead).

---

## Task 8: Verify T1 + T2 + T3 + T4 + legacy still pass

F3 is additive at the agent layer; no `world/flux/*` files change. Existing Phase-1 tests should be unaffected — but verify.

- [ ] **Step 1: Run** `uv run pytest tests/flux/ -v -m "not slow"`. Expect all previous tests pass plus the new fast metric/waveform/smoke ones.

- [ ] **Step 2: Run the slow tier** `uv run pytest tests/flux/ -v -m slow` to include `test_F3_trained_substrate_develops_pattern_specific_topology` and `test_F3_control_substrate_does_not_develop_pattern_specific_topology` and any existing slow tests.

- [ ] **Step 3: Run legacy suite.** Expect the F1c/F2 baselines (382 + flux total) to hold.

- [ ] **Step 4: If T2 / T3 / T4 regressed**, the cause is almost certainly an inadvertent import-time side effect in `agent/flux/learning_run.py` (e.g. constructing a `Cochlea` at module load time). Bisect by removing the import.

- [ ] **Step 5: Commit (if any fixups)** `flux F3 task 8: regressions fixed`.

---

## Task 9: `__init__` re-exports + README + F3 close

**Files:**
- Modify: `agent/flux/__init__.py` (re-export `LearningRunConfig`, `LearningRunResult`, `run_learning_session`, `make_training_waveform`, `make_control_waveform`, `frequency_localisation_index`)
- Modify: `README.md`
- Modify: `docs/flux/phase-log.md`

- [ ] **Step 1: Update `agent/flux/__init__.py`** with the F3 symbols and a clean `__all__`.

- [ ] **Step 2: README "Two substrates" status line**:

```
Status as of <date>: F0 + F1a + F1b + F1c + F2 + F3 complete (Phase 1 +
cochlea + synthesis + learning falsification). Frequency-localisation
metric f_loc separates trained (1 kHz tone-burst) from white-noise control
above the pre-registered margin. F4 (Tier-2 phoneme probe) is next.
```

- [ ] **Step 3: Phase-log F3-close entry:** task summary, final measured `f_loc_train` and `f_loc_control` and `margin`, number of alive bridges in each run, total test count.

- [ ] **Step 4: Run** `uv run pytest tests/flux/ -v` (all green, including slow) and the legacy suite. Commit only if both clean.

- [ ] **Step 5: Commit** `flux F3 complete: re-exports + README status + phase-log`.

---

## Notes for autonomous execution

- **The learning rule is already in the codebase.** Spec §5.5's monotone-flux bridge plasticity rule is implemented in `world/flux/plasticity.py` (`apply_plasticity`). It is monotone in `flux_through(t)`, has a deficit-decay term, and integrates flux along an edge as a STATE variable. It is **not** STDP (no spike timing), **not** Hebbian co-activation (no pre-post pairing — a bridge's flux is one number per edge, not a coincidence on its endpoints), **not** BTSP (no eligibility trace, no global plateau signal). If a task seems to require adding a new weight-update rule, the task is mis-specified — escalate. F3 falsifies the EXISTING rule under sustained patterned input; it does not invent a new one.
- **The matched-wallclock negative control is mandatory.** Per the autopilot charter: "If your current item's acceptance includes a substrate-level test […], you must also run the matched-wallclock no-engram negative control. If the substrate without the relevant engram produces the same passing test, the item is NULL, not PASS." For F3, "the relevant engram" is the pattern in the input waveform — the control substitutes spectrally-flat noise while keeping every other variable matched. The control is enforced in code by `test_learning_negative_control.py`.
- **NULL is a valid F3 outcome.** If the substrate as-built cannot produce `f_loc_train >= 0.30` AND `f_loc_control < 0.20` AND `margin >= 0.10` within the calibration ranges of `n_ticks_train`, `burst_amplitude`, and `burst_duration_ms`, the correct outcome is NULL with a postmortem describing whether the gap is in the implementation, the hypothesis, or the metric. Do NOT retune `f_loc_thresh_train`, `f_loc_thresh_control`, `margin_min`, `band_log_hz`, or `f_train_hz` after seeing run results. Those numbers are locked the moment this plan commits.
- **Pre-registration is enforced.** The thresholds in this plan are the falsifier. The pre-commit hook in `.eqmod/autopilot/CHARTER.md` blocks edits to `preregistered_acceptance:` blocks in `QUEUE.yaml` once a session starts, but the thresholds in *this plan file* are protected by protocol (charter §1: "If a test fails, the verdict is NULL or FAIL — not 'loosen the threshold.'"). R-5 must not edit this plan's threshold table.
- **Conservation is non-negotiable.** Spec §3: "A failed audit halts the run." The F3 trained-run test (Task 6) inlines a T1 assertion. If audit fails during the 10 000-tick run, the test fails and R-5 must investigate the audit residual rather than work around it.
- **Avoid silent-pass.** Both `n_bridges_min_alive` guards (≥ 30 trained, ≥ 10 control) FAIL the test if the substrate produces too few bridges to compute a meaningful metric. This is the F3 analogue of the F3b silent-pass bug described in `CLAUDE.md` (where `n_strong_before == 0` was silently treated as PASS). A run with zero alive bridges is NOT a pass.
- **No retuning of F1b / F1c / F2 configs.** Binding, plasticity, decay, thermal, cochlea, synthesis configs are FROZEN as the upstream items closed them. F3 reads those values from a single source (`agent/flux/learning_run.py::LearningRunConfig` defaults) but does not modify them.
- **The fixed cochlea is a feature, not a limitation.** Spec §5.6: the cochlea is the minimal pre-installation we accept — analogous to biological hair cells. F3 does NOT learn the cochlea bank. If the trained substrate fails because the bank is mis-tuned for 1 kHz, that is a F2 bug; revert to R-3 territory and STOP, do not adapt the bank here.
- **One sweep, one phase-log entry.** Per the F1a/F1b/F1c/F2 protocol every sweep in Task 6 must be logged in `docs/flux/phase-log.md` with: name of swept variable, old value, new value, measured `f_loc_train`, measured `f_loc_control`, measured `margin`, decision (keep / revert).
- **F3 is the bridge from substrate physics to learning claims.** If it NULLs, the substrate's structure-level signal under audio is insufficient for the Tier-1 LLR test in R-8, and that is itself a finding worth publishing per spec §11 ("If Phase 1 tests do not pass with reasonable parameter sweeps within 12 weeks of F1 start, the binding rule itself is reconsidered (not the thresholds)"). The F3 NULL postmortem feeds directly into the post-vacation decision on whether to continue with this substrate or revise the binding rule.
