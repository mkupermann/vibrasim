# Sub-project E — Reward channel + closed-loop orchestrator

**Date:** 2026-05-07
**Status:** approved (brainstormed and approved 2026-05-07)
**Parent design doc:** `docs/superpowers/specs/2026-05-06-baby-brain-foundation-design.md` §4.3 + §6
**Prerequisite:** Plans A, A.5, B, C, D merged to main. Plan E ties them together.

---

## 1. What this sub-project adds

Plans A through D give the substrate sustained growth, performance, directional plasticity, audio I/O, and video I/O. Plan E ties them into a closed loop and adds the missing third I/O — the reward channel. With Plan E in place, the agent can be presented with paired audio + video stimuli, receive reward when its output matches a target, and have repeat exposures leave persistent associative structure across the bridges.

The headline test is **M4** (the foundation spec's "glass-of-water demo"): show the substrate a glass + audio "water" 50× over 10 simulated minutes, then show the glass alone, and check that the audio output spectrally correlates with "water." The corollary is **M5** (reward-shaped output): give the substrate positive reward when its output matches a target spectrum and verify, after 100 reward trials, that the baseline output (no input) shifts measurably toward the target relative to a random-reward control.

Plan E is the last piece of the original baby-brain foundation. After it lands, the agent is operationally complete; the remaining plans (F brain checkpoint, G end-to-end demo) extend lifecycle and reproducibility but don't add new substrate physics or new modalities.

## 2. Scope

In scope:

- Reward channel (`+` and `−`) with asymmetric STDP physics for negative reward
- Closed-loop orchestrator with three modes (stepped CI, real-time, live demo)
- M4 acceptance test (slow, headline)
- M5 acceptance test (slow, headline)
- I5 acceptance test (fast, latency check)
- Real-WAV "water" fixture for the live demo
- Pre-registered acceptance contract in `tests/acceptance.toml`

Out of scope (future sub-projects):

- Brain checkpoint / resume → Plan F
- Dashboard wiring (manual `+`/`−` button UI) → Plan E.5 if desired later
- S2 (8-simulated-hour stability endurance test) → Plan E.5 or Plan F
- Color video, MFCC encoders, multi-modal fusion beyond paired exposure
- Real-time substrate performance (substrate stays at ~0.74× CPU-time/sim-time)

## 3. Architecture

Three modules, all under the existing `agent/` package introduced by Plan C:

1. `agent/reward.py` — `RewardChannel` class with `fire_positive(world)` and `fire_negative(world)` API.
2. `agent/loop.py` — `AgentLoop` class with stepped + real-time modes.
3. `agent/demo.py` — CLI entry point (`python -m agent.demo --m4`) that runs the live demo against real audio + webcam devices.

Plus a substrate extension to Plan B's `apply_stdp` for asymmetric reward physics, a new `k_polarity` field on atoms, and 6 new `WorldConfig` fields.

The orchestrator is single-threaded for the substrate path. The audio/video capture/playback threads from Plans C/D continue to run in parallel; the orchestrator's substrate thread (when in real-time mode) consumes from their buffers each tick. In stepped mode (used by all M4/M5/I5 tests) there are no threads — the test calls `loop.step(dt)` directly.

## 4. Module: `agent/reward.py`

### 4.1 The `RewardChannel` class

```python
class RewardChannel:
    """Programmatic reward injector.

    fire_positive injects a burst of vibrations with polarity=True at the
    reward port; fire_negative does the same with polarity=False. Atoms
    that bind from these vibrations carry the polarity into their
    k_polarity field. Plan B's apply_stdp reads that polarity at the
    reward-port boundary and flips the LTP/LTD branch for negative.
    """

    def __init__(
        self,
        port_origin: tuple[float, float, float] = (45.0, 45.0, 0.0),
        port_size: tuple[float, float, float] = (15.0, 15.0, 15.0),
        burst_size: int = 12,
        burst_freq: float = 30000.0,
        rng: np.random.Generator | None = None,
    ): ...

    def fire_positive(self, world) -> int:
        """Inject burst_size vibrations at random positions inside the
        reward port, all with polarity=True. Returns count injected."""

    def fire_negative(self, world) -> int:
        """Same as fire_positive but polarity=False."""

    def is_in_reward_port(self, position: np.ndarray) -> bool:
        """Whether the given 3D position falls inside the port volume."""
```

### 4.2 Burst geometry

Each `fire_*` call places `burst_size` vibrations at random positions inside the port box (uniform, drawn from the channel's RNG). All vibrations share the same polarity for that call. Frequency is `burst_freq` (default 30 kHz — high enough that bursts bind quickly into electrons via the standard freq_tolerance check; low enough that they're well below the substrate's audible band so they don't interfere with audio output).

The reward port is placed at `(45, 45, 0)` with size `(15, 15, 15)` so it sits in a corner distinct from audio input `(0, 0, 0)`, audio output `(45, 0, 0)`, and video input `(0, 0, 45)`. No port overlaps in XYZ.

## 5. Substrate extension: asymmetric STDP at the reward boundary

### 5.1 New per-atom field

Add `k_reward_polarity: np.ndarray[int8]` to `World.__init__`. Tristate semantics:

- `0` (default) — atom is NOT of reward-channel origin. Ambient-regen atoms, audio-input-port atoms, video-input-port atoms all stay at 0 and never trigger the asymmetric branch.
- `+1` — atom was bound from vibrations injected by `RewardChannel.fire_positive(world)`. Treated as positive reward.
- `-1` — atom was bound from vibrations injected by `RewardChannel.fire_negative(world)`. Treated as negative reward; triggers the LTP↔LTD swap.

A tristate avoids the boolean-default ambiguity (where `False` would conflate "no reward" with "negative reward"). The default `0` means "ignore this atom for asymmetric reasoning" — apply Plan B's existing alignment-based STDP unchanged.

Persisted in snapshots with the same backward-compat guard as `k_strength` and `k_orientation`.

### 5.2 Polarity propagation from vibrations to atoms

`RewardChannel.fire_positive` injects vibrations with a new per-vibration tag — either an existing field repurposed or a new `s_reward_polarity: int8` per vibration. Lean: add `s_reward_polarity: np.ndarray[int8]` to `World`, default 0, set to +1 / -1 by the reward channel's burst injector.

In `bind_nodes_upward` (Plan A's existing physics), when a triad + electron binds into an atom: collect the `s_reward_polarity` of all constituent vibrations (transitively, via the `k_comp_offset`/`k_comp_end` composition table); set `k_reward_polarity[atom]` according to the rule:

- If ALL constituents have the same non-zero `s_reward_polarity` value → atom inherits that value
- If ANY constituent has `s_reward_polarity == 0` → atom's `k_reward_polarity` is 0 (mixed origin)
- If constituents disagree (some +1, some -1) → atom's `k_reward_polarity` is 0 (conflict)

This conservatively requires reward-purity for an atom to be tagged. Mixed-origin atoms (ambient drift binding with reward bursts) stay at 0.

### 5.3 `apply_stdp` extension

The existing `apply_stdp` (Plan B) iterates ordered pairs `(t_i, atom_i) → (t_j, atom_j)` within `tau_LTP`. For each pair, it identifies bridge molecules in the A→B tube and applies LTP or LTD per molecule based on alignment.

The Plan E extension: **before** the alignment-based LTP/LTD decision, check `world.k_reward_polarity[atom_j]`. If `-1`, swap the LTP/LTD outcome.

Pseudocode addition inside the bridge-molecule loop:

```python
swap_ltp_ltd = (world.k_reward_polarity[atom_j] == -1)

# ... existing alignment computation ...
if (alignment >= 0 and not swap_ltp_ltd) or (alignment < 0 and swap_ltp_ltd):
    apply LTP
else:
    apply LTD
```

Note: position check (is the atom inside the reward port?) is implicit in the polarity check — only reward-burst-origin atoms have non-zero `k_reward_polarity`, and reward bursts only inject inside the reward port, so all `+1` and `-1` atoms are reward-port residents by construction. No separate spatial gate is needed.

### 5.4 Tests for asymmetric physics

Four geometric pair tests in `tests/test_reward_asymmetric_stdp.py`:

| Test ID | Pre-firing | Post-firing | Existing orientation | Expected outcome |
|---|---|---|---|---|
| RA1 | Non-reward atom (k_reward_polarity=0) | Reward port atom, k_reward_polarity=+1 | Aligned with A→B | LTP (unchanged from Plan B) |
| RA2 | Non-reward atom (k_reward_polarity=0) | Reward port atom, k_reward_polarity=-1 | Aligned with A→B | **LTD** (flipped) |
| RA3 | Non-reward atom (k_reward_polarity=0) | Reward port atom, k_reward_polarity=+1 | Anti-aligned | LTD (unchanged from Plan B) |
| RA4 | Non-reward atom (k_reward_polarity=0) | Reward port atom, k_reward_polarity=-1 | Anti-aligned | **LTP** (flipped) |

Plus a fifth test:

| RA5 | Atom inside reward port BUT k_reward_polarity=0 (ambient origin) | Same | Aligned | LTP (unchanged — the position alone doesn't trigger asymmetry; only the polarity tag does) |

Each test sets up a single bridge molecule between the firing pair, exercises one apply_stdp call with the matching geometry, and asserts the bridge's strength changed in the expected direction.

## 6. Module: `agent/loop.py`

### 6.1 The `AgentLoop` class

```python
class AgentLoop:
    def __init__(
        self,
        world,
        audio_io: "AudioIO | None" = None,
        video_io: "VideoIO | None" = None,
        reward: "RewardChannel | None" = None,
    ): ...

    def step(self, dt: float) -> None:
        """One substrate tick + I/O sync. Used by stepped mode and called
        from the substrate thread in real-time mode."""
        if self.audio_io is not None:
            self.audio_io.inject_into_substrate(self.world, dt)
        if self.video_io is not None:
            self.video_io.inject_into_substrate(self.world, dt)
        tick(self.world, dt)
        if self.audio_io is not None:
            self.audio_io.read_from_substrate(self.world, dt)

    def start_realtime(self) -> None:
        """Spawn substrate thread that calls step in a loop at world.config.dt
        intervals. Audio/video capture+playback threads must already be
        started via their own start() methods. The substrate thread does
        a sleep with jitter compensation to keep simulated time roughly
        aligned with wall-clock time at world.config.dt cadence."""

    def stop_realtime(self) -> None:
        """Clean shutdown of the substrate thread."""
```

### 6.2 Mode 1 — Stepped (CI tests)

Tests instantiate `AgentLoop`, optionally with mock `audio_io`/`video_io`/`reward`, and drive ticks directly:

```python
loop = AgentLoop(world, audio_io=io, video_io=vio, reward=rc)
for _ in range(n_ticks):
    loop.step(world.config.dt)
```

No threads. No real-time pacing. Deterministic. Used by every M4/M5/I5 test.

### 6.3 Mode 2 — Real-time

Tests or scripts:

```python
loop.start_realtime()
... wait wall-clock ...
loop.stop_realtime()
```

The substrate thread sleeps `dt` between ticks with overshoot compensation. AudioIO/VideoIO capture+playback threads (started independently) feed buffers in parallel; `step()` consumes from them. `tests/test_agent_realtime_smoke.py` uses this mode with synthetic-source plugins replacing real devices, so it remains CI-runnable but exercises the threading path.

### 6.4 Mode 3 — Demo (`python -m agent.demo --m4`)

CLI entry point in `agent/demo.py`. Constructs:

- `World` with M4 hyperparameters
- `AudioIO` with real device + loads `tests/fixtures/water.wav` for the training phase
- `VideoIO` with real webcam (`webcam_index=0`)
- `RewardChannel`
- `AgentLoop` running real-time

Runs forever (or until ctrl-C). Prints periodic status (substrate state, buffer fill, vibration count). Useful for live demos at conferences or for the user's own inspection but not part of automated CI.

## 7. New configuration parameters

```python
# Plan E — reward channel + orchestrator
reward_port_origin: tuple[float, float, float] = (45.0, 45.0, 0.0)
reward_port_size: tuple[float, float, float] = (15.0, 15.0, 15.0)
reward_burst_size: int = 12
reward_burst_freq: float = 30000.0

# Real-time mode pacing — milliseconds to sleep per substrate tick
agent_dt_realtime_ms: int = 17  # ≈ 60 ticks/sec target wall-rate
```

All defaults are inert when the orchestrator isn't started.

## 8. Acceptance tests

### 8.1 Necessary (unit + fast integration)

| ID | Test | Pass criterion |
|---|---|---|
| RC1 | `RewardChannel.fire_positive` injects N vibrations | World has +N alive vibrations after call, all inside reward port, all with `s_pol=True` |
| RC2 | `RewardChannel.fire_negative` symmetrically does the same with `s_pol=False` | Symmetric |
| RC3 | `RewardChannel.is_in_reward_port` correctly bounds-checks | Random points inside/outside port classified correctly |
| RA1-RA4 | Asymmetric STDP physics (4 pair geometries — see §5.3) | Each LTP/LTD outcome matches expected swap |
| AL1 | `AgentLoop.step` calls inject + tick + read in correct order | Mock audio/video IOs; assert call order via mock recorder |
| AL2 | `AgentLoop.step` with no IOs is just a tick | Sanity — no crash |
| **I5** | Reward firing latency | `RewardChannel.fire_positive(world); for _ in range(6): loop.step(dt)` → ≥ 1 firing event from a reward-port-resident atom |

### 8.2 Headline integration tests (slow)

| ID | Test | Pass criterion |
|---|---|---|
| **M4** | Glass-of-water demo, stepped | 50 paired exposures (synthetic glass image + synthesized water signature) over 10 sim-min, then glass-only test for 30 sim-sec → AudioIO output spectral cosine with target ≥ acceptance.toml `[M4].cosine_min` (default 0.5) |
| **M5** | Reward shaping, n_seeds=5 | 100 reward trials targeted vs random; targeted-run baseline output spectral cosine with target ≥ random-run + acceptance.toml `[M5].margin_min` (default 0.10), bootstrap 95% CI lower bound |
| AL3 | Real-time smoke (slow) | `start_realtime()`, run 5 wall-sec, `stop_realtime()` cleanly. Substrate thread joined; vibration count > 0 (something happened); no exceptions |

### 8.3 Pre-registered acceptance contract

`tests/acceptance.toml` extended with new `[M4]`, `[M5]` sections:

```toml
[M4]
duration_sim_min = 10.0
n_pairs = 50
test_phase_sim_sec = 30.0
cosine_min = 0.5

[M5]
n_trials = 100
n_seeds = 5
ci_confidence = 0.95
margin_min = 0.10

[provenance]
plan_E_thresholds_frozen_at_commit = "<filled at commit time>"
plan_E_calibration_seeds = [42, 43, 44]  # used during calibration
plan_E_held_out_seeds = [7, 100, 314, 999, 2024]  # frozen for M4/M5
```

Per Plan A's pattern: thresholds frozen BEFORE calibration runs. If acceptance fails on the held-out seed grid, the run is a failure logged in LOGBOOK.md, not retuned. Parameter changes require a CONCEPT amendment commit and a fresh held-out seed set.

## 9. New module / test layout

```
agent/
  __init__.py             # extend with RewardChannel, AgentLoop exports
  reward.py               # RewardChannel
  loop.py                 # AgentLoop (stepped + real-time)
  demo.py                 # python -m agent.demo --m4 entry point

tests/
  fixtures/
    water.wav             # ~50 KB real "water" recording — demo only, not load-bearing
  test_reward_channel.py            # RC1-RC3
  test_reward_asymmetric_stdp.py    # RA1-RA4
  test_agent_loop_stepped.py        # AL1-AL2 + I5
  test_agent_m4_glass_of_water.py   # M4 (slow, headline)
  test_agent_m5_reward_shaping.py   # M5 (slow, headline)
  test_agent_realtime_smoke.py      # AL3 (slow)
```

Plus extensions:

- `world/state.py`: add `s_reward_polarity: np.ndarray[int8]` per vibration and `k_reward_polarity: np.ndarray[int8]` per node (atom-applicable), persist `k_reward_polarity` via snapshot
- `world/physics.py`: extend `apply_stdp` with `k_reward_polarity[atom_j] == -1` swap; extend `bind_nodes_upward` at the atom branch to set `k_reward_polarity` per the §5.2 propagation rule (all constituents same non-zero → inherit; mixed/conflicting → 0)
- `world/snapshot.py`: persist `k_reward_polarity` with backward-compat guard
- `world/config.py`: 5 new fields (reward_port_origin, reward_port_size, reward_burst_size, reward_burst_freq, agent_dt_realtime_ms)
- `tests/acceptance.toml`: `[M4]`, `[M5]` sections

DB migration `db/migrations/0009_planE_reward_orchestrator_amendment.sql` adds the REWARD-R1 amendment row + Makefile target `db-migrate-planE-mark-implemented`.

## 10. Decision log

- **Why programmatic-only reward delivery (no dashboard wiring in v1)** — the dashboard runs in a separate Docker container from the substrate process; cross-process delivery (file-based, HTTP, Redis) doubles Plan E's surface area without buying anything for M4/M5 acceptance. Tests need direct method calls regardless. Dashboard wiring becomes Plan E.5 if/when manual button demo is required.
- **Why both `+` and `−` with asymmetric physics** — completes the foundation spec's reward surface. Negative reward is testable (RA1-RA4 unit tests; M5 might use it for output that's heavily off-target). Without it, the foundation spec is half-implemented.
- **Why a tristate `k_reward_polarity` instead of a `bool` polarity field** — a `bool` defaulting to `False` would conflate "negative reward" with "no reward signal," firing the LTP↔LTD swap on every ambient-origin atom that drifted into the reward port. A tristate (-1 / 0 / +1) makes the default value `0` mean "ignore for asymmetric reasoning" and reserves -1/+1 for atoms that genuinely arose from `RewardChannel.fire_*` bursts. Storing it on atoms (not on firings) keeps the reward-boundary check O(1) per pair endpoint regardless of firing-window length.
- **Why three test modes (stepped + real-time + demo)** — stepped is fast, deterministic, CI-runnable; real-time exercises the threading path that the demo will use; demo is for human-facing experience. Each mode has a clear role; none duplicates another. The cost is three test classes; the benefit is that we don't ship an untested threading path or an untested CLI.
- **Why synthesized "water" signature for tests + real WAV fixture for demo** — synthesized lets M4/M5 be deterministic with no audio file dependency. Real WAV is what the user actually wants to use at demo time. The two paths can coexist; tests stay fast and reproducible.
- **Why `(45, 45, 0)` for reward port placement** — distinct from audio in/out and video in (no XYZ overlap), corner-of-box for symmetry with the existing port layout, doesn't matter beyond non-overlap because bridge formation depends on which structures fire near the reward port, not on the port's geometric distance from inputs.

## 11. Risks and what to watch for

- **M4 may not pass on first run.** Empirical substrate physics. Risk: 10 sim-min may be too short for enough bridges to form between video port (glass features) and audio output port (water positions); or the synthesized "water" signature is too weak; or Plan D's encode_frame additive-orientation issue (mid-flight discovery in Plan D markdown) reduces signal-to-noise. Mitigation: budget two tuning passes during calibration (training duration, audio amplitude, bridge thresholds, reward-burst intensity), document any tuning in LOGBOOK, then either pass on the held-out seed grid or mark xfail with explicit reason. Don't iterate beyond two passes.
- **M5 control comparison is statistical.** "Targeted reward shifts output more than random reward" depends on enough seeds to distinguish signal from noise. n_seeds=5 with bootstrap CI is the minimum; if variance is high we may need n=10. Mitigation: pre-register the metric and threshold in `tests/acceptance.toml`; plan accommodates a follow-up amendment if calibration shows n=5 is too small.
- **Asymmetric STDP is new physics.** RA1-RA5 cover the four pair geometries with explicit expected outcomes plus the ambient-origin negative case (atom inside reward port but `k_reward_polarity=0` does NOT trigger swap). Risk: an asymmetry I haven't anticipated (e.g., what about firings from VIBRATIONS in the reward port, before they bind into atoms?). Mitigation: explicit invariant — only atom-level firings carry reward polarity; vibration-level interactions are unchanged.
- **Real-time mode threading.** The substrate thread + audio capture + audio playback + video capture = 4 threads. They're loosely coupled (only the buffer locks are shared), but a real-time test could expose deadlocks or starvation. Mitigation: AL3 smoke test runs a short real-time burst and asserts clean shutdown.
- **Demo mode hardware fragility.** Webcam permissions, microphone permissions, default-device discovery — all flaky on macOS. Mitigation: `--dry-run` flag that uses synthetic sources instead of real devices, and clear error messages when device acquisition fails.

## 12. Approval gate

Approved 2026-05-07 with the following design choices locked:

1. Scope: M4 + M5 + I5 acceptance.
2. Reward delivery: programmatic-only (no dashboard wiring).
3. Templates: synthesized signature (M4/M5 tests) + real WAV fixture (demo).
4. Test modes: three coexisting modes (stepped CI, real-time smoke, live demo).
5. `+`/`−` asymmetry: yes, with new substrate physics (`k_polarity` field + LTP/LTD swap at reward boundary).
6. Reward port: `(45, 45, 0)` with size `(15, 15, 15)`.

Implementation proceeds via `superpowers:writing-plans` skill on a fresh `feat/baby-brain-plan-E` branch.
