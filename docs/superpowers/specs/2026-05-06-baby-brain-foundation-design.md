# Baby brain — foundation design

**Date:** 2026-05-06
**Status:** approved (brainstorm complete, awaiting implementation plan)
**Scope:** the foundation sub-project of the *baby brain* programme: a self-organising, learning, multi-modal agent that grows structure in response to its own experience.

---

## 1. Programme goal and where this fits

The substrate has so far produced vibrations → electrons → atoms → molecules (Phases 1–2 of the original conceptual programme), and as of 2026-05-06 it can fire individual atoms via integrate-and-fire dynamics (PHASE4-R1/R2/R3). The next horizon is no longer "the next phase" — it is a complete, multi-modal agent that perceives, learns, and acts. The foundation described here is the *first* sub-project of that horizon. After it, three further sub-projects layer on real-time performance, video output, and multi-agent interaction; they are **out of scope** for this spec.

The agent we are building has the following character. It listens via a microphone. It watches via a webcam. It receives a reward signal from a button on the dashboard. It speaks back via a speaker. It grows physical structure inside itself — molecules and bridges — in response to what it experiences. Structures that are reinforced repeatedly persist. Structures that are not, decay. Co-occurring sensory events form bridges between the regions that fire together, so that, after enough exposure, presenting one input pattern recalls the others. Showing it a glass of water and saying "water" enough times will, by the substrate's own physics, leave a trace that pairs the two — and presenting the glass alone afterwards will activate the audio-port pattern for "water".

Nothing about this requires a learning algorithm bolted on top of the substrate. Every claim above reduces to the substrate's local laws.

Plan A is conventionally named *substrate-growth foundation*, not *baby brain foundation*. The "baby brain" label is reserved for the post-Plan-D scope where the glass-of-water demo (M4) actually runs and the agent exhibits brain-like behaviour. Pre-Plan-D plans (A, A.5, B, C, D) are infrastructure.

## 2. Architecture overview

The substrate is a 3D periodic-boundary box. Inside it, four spatial regions are designated as I/O ports. The substrate physics is unaware of these regions; the I/O code knows where to inject and where to read.

| Region | Role |
|---|---|
| Audio input port | Microphone → STFT → vibration injections at frequency-mapped positions |
| Video input port | Webcam → patch features → vibration injections at retinotopic positions |
| Reward port | Dashboard buttons → vibration burst at the reward port location |
| Audio output port | Firing activity → IFFT → speaker waveform |
| The middle | Free substrate. Where bridges form. Where memory lives. |

The audio input and audio output ports use the same frequency-to-position mapping in opposite directions, so the substrate "speaks" the same language it "hears". The audio and video input ports are placed on adjacent faces of the box so that bridges spanning the boundary form naturally when audio and video events co-occur.

A closed loop runs continuously: microphone → input port → substrate dynamics → output port → speaker → ambient sound → microphone again. The substrate experiences both its own utterances and the user's, and the bridge mechanism naturally makes recurring patterns dominate.

## 3. Substrate amendments

Five additions to the existing physics. All are guarded by `neuron_dynamics_enabled` (already in the config) so legacy configurations behave as before.

### 3.1 R1 — Recycling regeneration

The current `lambda_gen` rule allocates new vibration slots until the buffer fills, after which regeneration silently no-ops. Replace with a *displace* rule: when the ambient density falls below the configured target, pick an existing alive vibration that is far from any active region (more than 2× r_2 from any node) and respawn it where regeneration is needed. Total vibration count stays constant, the buffer never bloats, the world stays the same size, and vibrations recycle the way oxygen does in lungs.

### 3.2 R2 — Strength-aware decay for level-5+ structures

Add a per-node scalar field `k_strength`, initialised to 1.0 at birth. Each tick, every level-5+ molecule within radius `r_strengthen` of any firing atom gets `strength += dt`. The decay probability per tick is `lambda_dec_mol * dt / max(strength, 1.0)`. Weak (strength=1) molecules decay with a time constant of approximately one minute of simulated time; strength=100 molecules decay one hundred times more slowly. When a molecule decays, its constituent atoms revive into the alive pool.

This is the long-term-memory rule. Repeated activity keeps a structure alive indefinitely. One-off coincidences fade.

### 3.3 PHASE3-R1 — Molecule + molecule binding

Append `(5,5)→6, (5,6)→7, (6,6)→7, (6,7)→8, (7,7)→8` to the upgrade-target table. Same frequency-ratio rule as atom-to-molecule binding. Without this, structures only grow wide (more level-5 molecules); with it, they grow tall (towards level 8), which is necessary for any non-trivial cortical-column-like architecture.

### 3.4 Tuned PHASE4 emissions — frequency-band fan

Currently when an atom fires, it emits N vibrations at a single `emit_freq`. Same-frequency vibrations cannot bind to each other under the existing frequency-ratio rule, so firing emissions cannot climb the binding hierarchy. Replace with an emission *fan*: each firing emits N vibrations whose frequencies are drawn from a band that includes `emit_freq`, `emit_freq × freq_ratio`, and `emit_freq / freq_ratio`. Within the band, binding-ratio pairs naturally exist. Result: where firings happen, vibrations of the right ratios cluster, the binding cascade runs, molecules form. Activity-driven growth emerges from existing physics; we do not add a new "spawn molecule on firing" rule.

If yield turns out too low in practice, a fallback rule (with probability p, firing seeds a level-5 molecule near the firing atom) is acceptable; we will start without it.

### 3.5 STDP — directional bridge plasticity

> **Framing disclaimer.** This rule uses STDP notation (τ_LTP, τ_LTD, δ_LTP, δ_LTD) by analogy with the spike-timing-dependent-potentiation literature. The substrate has no membrane voltage, no calcium transient, and no neurotransmitter delay — so the parameters here are free design choices, not fits to biological data. The shape of the timing curve (P2 acceptance test) is a substrate property, not a validation of biological STDP.

Add a per-tick post-processing step. After each tick, scan `world.firing_events` for ordered pairs `(t₁, A) → (t₂, B)` with `0 < t₂ − t₁ ≤ τ_LTP` (default τ_LTP = 20 ms). For each such pair:

1. Identify the bridge tube — molecules within radius `r_bridge` of the line segment from atom A to atom B.
2. For each bridge molecule:
   - Pre-before-post (causal): `strength += δ_LTP · exp(−(t₂−t₁) / τ_LTP)`
   - Post-before-pre (the same scan picks these up in reverse): `strength −= δ_LTD · exp(−(t₂−t₁) / τ_LTD)`
3. Update the molecule's `k_orientation` 3-vector with a running average of the unit vector A→B at the moments it was reinforced.

The `k_orientation` field is what makes synapses directional. When a vibration arrives at the bridge, its propagation strength is modulated by the dot product with the orientation vector. A→B propagates strongly; B→A propagates weakly. This is the asymmetry of a real synapse.

## 4. I/O subsystems

### 4.1 Audio — symmetric encoder/decoder pair, buffered

A single `audio_io` module owns mic capture, speaker playback, the STFT/IFFT pair, and the frequency-to-position mapping.

**Input pipeline.** A live capture thread captures the microphone at 16 kHz (configurable) into a 30-second circular buffer. The audio encoder consumes from the head of the buffer at the substrate's own consumption rate, which is whatever the substrate's tick rate yields (today approximately 0.3× realtime). For each consumed audio block, an STFT produces a frequency spectrum; for each non-trivial bin, a vibration burst is injected at the input port at the position mapped from that frequency, with intensity proportional to amplitude and polarity matching the bin's phase.

**Output pipeline.** At each substrate tick, the audio decoder reads firing activity inside the output port, builds a per-frequency-bin amplitude vector by summing firings at each port-mapped position, runs an inverse STFT, and writes the resulting audio samples into a second 30-second circular buffer. A live playback thread plays from the buffer at native speaker rate.

**Honest behaviour given substrate < realtime.** When the substrate is slower than realtime, the input buffer fills; we drop the oldest samples on overflow. Output samples are produced slowly, so the substrate's voice plays back deeper and slower than what it heard — an honest artifact, not a bug. Real-time performance is its own future sub-project.

### 4.2 Video — Gabor-style patch features, buffered

A `video_io` module owns webcam capture, the patch-feature encoder, and the retinotopic position mapping.

**Encoding.** Each captured frame is divided into a regular grid of patches (default 16×16). Per patch, a small bank of oriented filters (eight orientations, simple Gabor or Sobel) extracts edge orientation, edge intensity, and mean colour — approximately ten features per patch. Each feature becomes a vibration burst at a substrate position mapped from `(patch_x, patch_y, feature_id)`. The frequency of the burst encodes feature intensity. Polarity encodes sign — light-on-dark vs dark-on-light.

The video port's spatial layout mirrors the visual field. Left of frame → left of port. Vertical edges in the upper-right of the frame → vibration cluster in the upper-right of the port. This is a retinotopic map, the same way primary visual cortex (V1) is laid out.

**Buffering.** Live capture at 30 fps into a frame buffer; encoder consumes at substrate rate, dropping oldest frames on overflow. Same architectural pattern as audio.

### 4.3 Reward channel

Two buttons on the dashboard, labelled `+` and `−`. Each press injects a vibration burst at the reward port. The bridge-molecule mechanism does the rest: bridges form between whatever was firing at the moment of reward and the reward port, so reward gets associated with the structure that produced the rewarded behaviour. This is classical conditioning emerging from the same physics.

A configurable `reward_burst_size` and `reward_burst_freq` control the perceived intensity. No separate reward-propagation rule is required.

### 4.4 Brain checkpoint / resume

The substrate accumulates state over hours of simulated time. To preserve that across sessions, the existing snapshot format is extended with the new fields (`k_strength`, `k_orientation`, the firing-event tail, the live-input-buffer head pointer). The save path is `runs/<run_id>/checkpoint.npz`; the load path produces a substrate with bit-identical state. RNG state is preserved so a reload-and-run-1s yields the same trajectory as a no-save 1s.

## 5. Closed-loop integration

A single `agent_loop` module orchestrates the four I/O subsystems and the substrate. It runs four threads:

1. **Audio capture thread** — feeds the input audio buffer from the live mic.
2. **Video capture thread** — feeds the input video buffer from the live webcam.
3. **Substrate thread** — consumes from input buffers, ticks the substrate, applies STDP, writes to the output audio buffer. This is the rate-limiting thread.
4. **Audio playback thread** — drains the output audio buffer to the speaker.

The reward port and dashboard buttons run on the dashboard's request-response cycle (Streamlit), not on the agent loop. The dashboard also surfaces live metrics: substrate tick rate, buffer fill levels, firing rate per port, mean strength per region, total bridge count, growth/decay rate.

Locks are simple: each circular buffer has a producer-consumer lock; the substrate thread takes the input-buffer locks at consumption and the output-buffer lock at write.

## 6. Acceptance test plan

The foundation is *done* when every test below passes on the standard configuration and on at least three distinct rng seeds.

### 6.1 Necessary — substrate physics works in isolation

| ID | Test | Pass criterion |
|---|---|---|
| F1 | Sustained run | 60-min sim with periodic burst at one location: total molecule population stays in [0.5×, 2.0×] of mean for ≥ 80% of run |
| F2 | Activity-coupled growth | Input only at A. After 5 sim min, median(level-5+ density at A / at random distant B) ≥ 3 across 10 seeds |
| F3a | Weak decay | After F2, stop input. After 5 more min, A's unreinforced-structure density drops ≥ 80% toward B's baseline |
| F3b | Strong persists (memory) | Structures with strength > 50 decay < 20% over the same 5-min silent period |
| F4 | Molecule fusion | After 30-min sustained input, level-7+ molecules exist (zero exists without PHASE3-R1) |
| P1 | Bridge directionality | 100 paired-pulse trials (A fires, B fires 10 ms later). Bridge in A→B tube strength ≥ 5; bridge in B→A tube strength ≤ 1 |
| I1 | Tonotopic correctness | Inject 440 Hz for 5 s → firings localised within ±5% of 440 Hz-mapped position |
| I2 | Speaker fidelity | Trigger firings at 440 Hz position → speaker output has spectral peak at 440 Hz ± 2% |
| I3 | Closed-loop stability | Mic↔speaker chain runs 5 min without runaway oscillation |
| I4 | Video encoding distinctness | Three different shapes (line/circle/square) produce video-port patterns with pairwise cosine similarity < 0.5 |
| I5 | Reward port works | Button press → reward-port firings within 100 ms |
| S1 | Checkpoint roundtrip | Save → load → continue 1 s, compared to no-save 1 s, identical to numerical tolerance + RNG state preserved |

### 6.2 Headline — the brain demonstrably learns

| ID | Test | Pass criterion |
|---|---|---|
| M1 | Tonotopic learning | 50× 440 Hz tones (1 s on, 5 s rest). After 50 reps, persistent structure at 440 Hz-mapped position (strength > 20). No structure forms in unexposed control seed. |
| M2 | Audio co-occurrence | 440 Hz + 880 Hz played together 50×. Bridge between the two mapped positions has strength > 10. Single-tone control (440 alone or 880 alone) produces no such bridge. |
| M3 | Spoken-word fingerprint | Same word ("water") 50×. Spectral correlation between training trial 50 and recall test > 0.6. Correlation with a different word < 0.3. |
| M4 | **Glass-of-water demo** (the headline) | Webcam at glass + audio "water" 50× over 10 sim min. Show glass alone afterwards. Audio-port firing rate within 1 s of glass appearance > 2× pre-training baseline. Output spectral correlation with "water" template > 0.5. |
| M5 | Reward shaping | Positive reward when output spectrum matches "water". After 100 trials, baseline output (no input) shifts measurably toward "water" spectrum (vs random-reward control) |

### 6.3 Stretch — robustness over time

| ID | Test | Pass criterion |
|---|---|---|
| P2 | STDP timing curve | Vary Δt across [−50 ms, +50 ms]. Strengthening peaks at Δt = 5–10 ms, → 0 at Δt = ±50 ms, goes negative for Δt < 0 |
| S2 | Long-run stability | 8 sim hours, mixed audio + video + reward. No crashes, no NaN/inf in any state, memory stable |

### 6.5 Contingent Plan A.7 gate

If F5's conservation residual exceeds 20% on the held-out seed grid (i.e., the substrate is operating outside a viable thermodynamic regime), Plan A.7 (thermodynamic-regime parameter sweep) becomes a hard prerequisite before Plan B begins.

Plan B's spec document MUST open with either:
- (a) a pointer to Plan A.7's results showing the substrate is in a viable regime, OR
- (b) a CONCEPT amendment justifying why the out-of-regime result does not block learning.

This gate is enforceable: Plan B cannot pass its own pre-Brainstorm review without one of (a) or (b).

## 7. Out of scope (future sub-projects)

These are real and will come later. They are not part of this foundation.

- **Real-time performance.** Substrate currently runs at ~0.3× realtime. Live audio and video already work via buffering; closed-loop conversation at human cadence requires substrate ≥ 1× realtime, which means JIT, parallelism, or a different binding kernel.
- **Video output.** The substrate speaks but does not draw. Adding video output (the substrate dreaming, generating images) is its own sub-project.
- **Robot embodiment.** Beyond audio output, motor channels (cursor, robot arm) are out.
- **Multi-agent.** Two baby brains talking to each other is a far horizon.
- **Pruning rules.** Beyond molecule decay, more sophisticated structural pruning (e.g. weak bridges removed entirely) is deferred.

## 8. Out of scope (explicitly not changing)

- The Phase 1–2 binding rules (frequency ratio, tolerance, radii) stay as they are. Activity-driven growth piggybacks on them, it does not replace them.
- The Phase 1–2 calibration TOMLs (`calibration_session3.toml`, `calibration_phase2_acceptance.toml`) stay as they are. The new agent runs on a different config.
- The dashboard's existing pages (Sessions, Configs, Runs, Results, Amendments, Acceptance) stay as they are. The reward buttons and live metrics are *new* pages.

## 9. New configuration parameters (summary)

All guarded by `neuron_dynamics_enabled` and additional flags so legacy configs behave as before.

| Parameter | Default | Role |
|---|---|---|
| `lambda_dec_mol` | 0.001 | baseline decay rate for level-5+ molecules |
| `r_strengthen` | 5.0 | radius around firing atoms for strengthening level-5+ molecules |
| `emit_band_ratios` | `[freq_ratio, 1.0, 1/freq_ratio]` | emission-frequency multipliers |
| `tau_LTP` | 0.020 | STDP pre-before-post window (s) |
| `tau_LTD` | 0.020 | STDP post-before-pre window (s) |
| `delta_LTP` | 1.0 | LTP increment per qualifying pair |
| `delta_LTD` | 0.5 | LTD decrement per qualifying pair |
| `r_bridge` | 5.0 | bridge-tube radius around firing-pair line segment |
| `audio_sample_rate` | 16000 | mic and speaker rate (Hz) |
| `audio_buffer_seconds` | 30 | input/output audio circular-buffer capacity |
| `video_fps` | 30 | webcam capture rate |
| `video_patch_grid` | `(16, 16)` | retinotopic patch grid |
| `video_n_orientations` | 8 | Gabor orientation count |
| `reward_burst_size` | 12 | vibrations per reward press |
| `reward_burst_freq` | 30000 | nominal frequency of reward vibrations |

## 10. New module layout

```
world/
  config.py            # extended with the new fields above
  state.py             # adds k_strength, k_orientation, ports
  physics.py           # adds R1, R2, PHASE3-R1, tuned emissions, STDP
  snapshot.py          # extended with the new fields

agent/
  __init__.py
  audio_io.py          # mic + speaker + STFT/IFFT + buffer threads
  video_io.py          # webcam + Gabor encoder + frame buffer
  reward.py            # reward port + dashboard wiring
  loop.py              # the four-thread orchestrator
  encoder_audio.py     # frequency↔position mapping helpers
  encoder_video.py     # patch-feature extraction

tools/                 # existing, unchanged for this foundation
app/                   # existing dashboard + new reward + live-metrics pages
tests/
  test_amendment_R1_recycling_regen.py
  test_amendment_R2_strength_decay.py
  test_amendment_PHASE3R1_molecule_fusion.py
  test_tuned_emissions.py
  test_stdp_directionality.py
  test_audio_io_tonotopic.py
  test_audio_io_speaker_fidelity.py
  test_audio_io_closed_loop.py
  test_video_io_encoding.py
  test_reward_channel.py
  test_checkpoint_roundtrip.py
  test_glass_of_water_e2e.py     # the headline test
```

## 11. Decision log (for future archaeology)

- **Why activity-driven growth (not density-driven).** Density-driven growth produces the same structure regardless of input statistics, defeating the purpose of an agent that learns from what it hears. Activity-driven growth means the substrate's structure *is* a record of its experience.
- **Why use-dependent decay (not uniform).** Uniform decay gives the substrate amnesia. Use-dependent decay is the long-term memory mechanism.
- **Why no explicit synapse rule.** Bridge molecules emerge from the existing strength field plus locality. Adding a separate "synapse" entity would duplicate machinery the substrate already has.
- **Why STDP applied to bridge molecules (not synapse weights).** We do not have synapse weights; we have molecules. STDP modulates molecular strength, which is the physical correlate.
- **Why one output port (not whole-substrate output).** Real motor cortex is a region, not the whole brain. Localised output also lets us train the rest of the substrate as "central nervous system" without bleed.
- **Why imitation + reward (not imitation alone).** Imitation alone gives self-stable babbling. The reward channel lets the user shape what gets reinforced. Both are needed.
- **Why patch-feature video (not pixels).** Pixels do not scale and they do not have the locality structure the substrate expects. Patch features mirror V1's actual organisation.
- **Why live mic with buffering (not recorded).** "Live" is the demo we are building toward. Buffering absorbs the speed mismatch between substrate (~0.3× realtime) and the world (1× realtime). Recorded audio is also supported via the same encoder for tests; live is the primary mode.
