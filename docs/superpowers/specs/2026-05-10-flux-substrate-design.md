# Flux Substrate — Design Spec

**Status:** brainstorm-approved, awaiting user review before implementation plan.
**Created:** 2026-05-10
**Position:** lives alongside legacy EQMOD substrate. Path: `world/flux/` and `agent/flux/`.
**Falsifier tier:** Tier 2 pflicht, Tier 3 stretch (siehe §4).

---

## 1. Why this project exists

EQMOD's current substrate has six engineered binding rules, a pre-installed MFCC frontend, three pre-seeded engrams, and a hand-coded concept-blending rule. Its README has been rewritten (commit `d83b82c`) to reflect what that means honestly: the substrate does not learn a hierarchy — it executes a hierarchy that was installed. The G19 predictive-babble falsifier returned **FAIL** on the first real-corpus run with z-scores statistically indistinguishable from white noise.

This spec defines a parallel substrate that replaces the engineered scaffolding with **one foundational principle**:

> Energy flows through an open boundary. Structures kondensieren wo sie diesen Fluss effizienter kanalisieren als kein Struktur. Hierarchies emerge because higher organisational levels channel flux more efficiently than lower levels.

Theoretical anchors (peer-reviewed, established):
- **Schrödinger 1944** *What is Life?* — Leben as negentropy consumption
- **Prigogine 1977 (Nobel)** — dissipative structures far from equilibrium
- **Maturana & Varela 1972/1980** — autopoiesis as operational definition
- **Friston 2010** — free-energy principle as inference/thermodynamics bridge

The combination — thermodynamic flux + 3D continuous substrate + hierarchy without pre-coded levels + learning as flux-optimisation — is, to our reading, not realised as a working computational system elsewhere.

## 2. Scope statements

**What this project is.**
A new substrate in which (a) energy is carried by discrete quanta on vibrations, (b) a temperature field emerges from local free-vibration density, (c) structure formation is governed by a single temperature-gated predictive-coherence rule, (d) learning is the reconfiguration of substrate topology toward more efficient flux channelling, (e) sensory input is encoded as energy quanta injected at a hot boundary, (f) entropy is exported by quanta absorbed at a cold boundary.

**What this project is not.**
- Not a model of biological consciousness.
- Not a claim about phenomenal consciousness (qualia, "what it is like").
- Not an active-inference agent in Friston's mathematical sense — the architecture is physics-realised, not message-passing.
- Not a faithful simulation of neural dynamics.
- Not an AGI proposal.
- Not a refactor of EQMOD's existing code. EQMOD's legacy substrate (`world/`, `agent/`) remains in place for comparison. This is `world/flux/` and `agent/flux/` next to it.

## 3. The single principle

**One binding rule replaces the six legacy levels:**

A bond forms between two or more vibrations within distance `r` and time window `τ` with probability:

```
p_bind = sigmoid(α * pred_coherence + β * (T_crit - T_local))
```

where:
- `pred_coherence` is the **temporal cross-correlation** of the two vibrations' frequency-amplitude trajectories over a sliding window of `τ`. Concretely: each vibration's frequency and amplitude are sampled at every tick over the last `τ` ticks; `pred_coherence(A,B) = max_lag corr(f_A(t), f_B(t+lag))` for `lag ∈ [-τ/2, +τ/2]`. High value = one's frequency reliably predicts the other's, with possibly a time lag. Range [-1, 1].
- `T_local` is the local temperature, computed as exponentially-smoothed local free-vibration density (§5.1), units: free-quanta per voxel volume
- `T_crit` is the critical temperature above which binding is suppressed (units: same as T)
- `α`, `β` are global gain coefficients (dimensionless after T-scaling)

**No levels.** Bound nodes can themselves enter binding attempts with other nodes (free or bound), under the same rule. Hierarchies emerge because higher-level configurations channel flux more efficiently than the level below, and so persist longer.

**Energy is conserved per tick**, audited as an assertion:
```
E_total(t+1) == E_total(t) + E_injected(t) - E_exported(t)
```
within numerical tolerance `1e-9 * E_initial`. A failed audit halts the run — there is no recovery path. Conservation is non-negotiable. (Production mode flag exists to disable audit for speed; default is enabled.)

## 4. Falsifier tiers

The substrate passes Tier 2 to count as a scientific result; Tier 3 is the stretch.

| Tier | Claim | Test |
|---|---|---|
| 1 | "Prediction works on raw signal" | After F3 training, the substrate's open-loop generated signal has log-likelihood improvement vs random baseline, p < 0.01 bootstrap |
| 2 (pflicht) | "Phoneme-like categories emerge unsupervised" | Linear probe trained offline on substrate internal states classifies forced-aligned ground-truth phonemes with accuracy ≥ `X%` above random-init same-architecture baseline. `X` to be set after F2 (cannot pre-register before measuring baseline) |
| 3 (stretch) | "Curiosity demonstrably shapes growth" | Pearson correlation between local attention density and local PE in F4 phase ≥ 0.4; attention trajectory wanders measurably (variance of attention centroid over last 30% of training > variance in first 10%) |

Tier 2 not reached → project publishes the architecture + lessons as a negative result. Tier 3 not reached → published without strong attention claim. Tier 2 reached → publishable result; Tier 3 reached → headline result.

## 5. Architecture

### 5.1 Substrate

A 3D continuous cube. Default dimensions: 60×60×60 voxels (EQMOD-compatible) with absorbing boundaries on the top face and the four side faces, and injecting boundary on the bottom face. Voxel coordinates are continuous, not gridded — vibrations have float positions.

Each voxel maintains:
- `n_free_quanta[x,y,z]`: count of free vibrations whose position lies within that voxel
- `T[x,y,z]`: local temperature, exponentially smoothed:
  ```
  T(t+1) = α * n_free_quanta(t) / V_voxel + (1-α) * T(t)
  ```
  with α tunable (default α = 0.1).

### 5.2 Vibrations

Each vibration is an entity with:
- `position` (float3 in cube coordinates)
- `velocity` (float3)
- `frequency` (scalar, log-Hz)
- `polarity` (signed binary)
- `energy_quantum` (scalar, default 1.0 — quantised but float-typed so a binding event can redistribute non-integer remainders into heat export)

A vibration is **free** if not part of any structure, else **bound** (its energy is held by the structure).

### 5.3 Boundary

**Hot floor (z = 0 face):**
- In Phase 1 (validation): constant injection rate `r_hot` of vibrations with thermal-distribution frequencies and random velocities pointing up
- In Phase 2+: cochlea module (§5.6) drives injection

**Cold ceiling + sides:**
- A vibration arriving within `δ` of an absorbing face gives its energy quantum to a global `heat_exported_counter` and is removed from the simulation

### 5.4 Binding & structures

A structure is a graph: nodes (each holding the energy of one or more vibrations) and bridges (directed, weighted). When two vibrations bind, a new node is created at their spatial centroid; the bridge between them inherits initial weight proportional to their predictive coherence.

Structures can act as inputs to further binding: a bound node has an "external energy port" that lets a free vibration interact with it, and bound nodes can themselves bind with other bound nodes under the same rule.

**Binding is exothermic.** When two quanta of total energy `E_in` bind, a fraction `η ∈ [0,1)` is exported as heat to the global counter; the remaining `(1-η)·E_in` stays in the structure. `η` is tunable; lower η = "easier" binding, more energy retained; higher η = "harder" binding, more heat exported. Default η = 0.1.

**Structures persist while flux passes through them.** Each tick, free vibrations within distance `r` of a bound node interact with it. The interaction strengthens the bridge that channels the flux. Bridges with no flux over `N_decay` ticks lose weight; when bridge weight falls below `w_min`, the bridge breaks; when a node has no remaining bridges, it dissociates and its energy returns to free vibrations.

### 5.5 Plasticity

Two plasticity rules, both Hebbian-with-flux:

1. **Bridge strengthening**: `w(t+1) = w(t) + γ * flux_through(t)` where flux through a bridge is the count of quanta that traversed it this tick
2. **Bridge decay**: `w(t+1) = w(t) - λ * max(0, flux_min - flux_through(t))`

No STDP. No BTSP. Plasticity is monotonic in flux.

### 5.6 Cochlea (input)

A bank of `N_cochlea` (default 64) damped resonators distributed log-spaced from 50 Hz to 8 kHz, located at the hot floor. Each resonator is driven by the incoming audio waveform: classical second-order resonator dynamics, no FFT, no clustering. The resonator's instantaneous amplitude controls the rate of vibration injection at its corresponding floor location, with frequency property matching the resonator's tuned frequency.

The cochlea is **fixed, not learned**. This is the minimal pre-installation we accept — analogous to biological hair cells, which evolve their tuning across generations but are static within a lifetime.

### 5.7 Synthesis (output)

The inverse of the cochlea. The substrate's bound nodes drive their nearby resonators at the floor in reverse — node firings cause amplitude excitations of resonators tuned to matching frequencies; these resonators' summed driven output is the synthesised waveform. Additive synthesis from the same resonator bank.

No learned decoder. No KMeans-to-STFT.

### 5.8 Attention

Compute budget per tick is `B_total` "interaction-attempts" distributed across voxels. Allocation:

```
b(x,y,z) = B_total * (PE(x,y,z) + ε) / Σ (PE + ε)
```

where `PE(x,y,z)` is the local prediction error and `ε` is a small floor (e.g. 1e-3) so voxels with PE≈0 still get a baseline allocation. Concretely:

- For each bound node `n` in or near voxel `(x,y,z)`, the substrate has a running prediction of its next-tick state from its incoming bridges (sum of weighted contributions of upstream nodes).
- At each tick, the actual next state is compared with that prediction: `pe_n = ||predicted_n - actual_n||²`.
- `PE(x,y,z) = Σ pe_n` over nodes in the voxel + a contribution from unbound vibrations using their last-tick velocity as a trivial prediction.

Voxels with high `PE` get more interaction ticks per real-time step (more binding attempts, more pair-searches, more flux updates). Voxels with `PE ≈ 0` get the floor only. This is the curiosity mechanism: compute follows surprise.

Attention is logged per cycle (per voxel `b` allocations + per voxel `PE`) for Tier-3 evaluation.

This is the curiosity mechanism: the substrate spends compute where it does not yet understand what is happening.

## 6. Tick data flow

One tick, in order:

1. **Audit-snapshot**: record `E_total(t)`
2. **Inject** at hot floor (Phase 1: constant; Phase 2+: cochlea-driven)
3. **Absorb** at cold faces — vibrations near boundary → `heat_exported_counter`, vibration removed
4. **Move** free vibrations: `position += velocity * dt`
5. **Interact**: pair-search within `r`; compute pred_coherence; attempt binding with `p = sigmoid(α*coh + β*(T_crit - T_local))`. Binding exports `η * E_in` as heat.
6. **Structure-flux**: for each existing structure, count flux of free vibrations passing through nearby; update bridge weights via plasticity rule
7. **Decay**: bridges with flux below threshold for N ticks lose weight; nodes with no bridges dissociate
8. **Temperature update**: `T(x,y,z) = α * density(x,y,z) + (1-α) * T_prev`
9. **Attention reallocate**: compute PE field, redistribute compute budget for next tick
10. **Audit-end**: assert `|E_total(t+1) - (E_total(t) + E_injected - E_exported)| < ε`. Halt on failure.

## 7. Phase-1 validation contract

Phase 1 closes when all four tests pass on `world/flux/` without any audio input. No exceptions.

**T1 Conservation.** After 1000 ticks under constant injection: `|E_initial - (E_in_free + E_in_bound + E_exported)| < 1e-9 * E_initial`.

**T2 Bénard.** Hot floor T_hot, cold ceiling T_cold (no audio). 10000 ticks. At steady state, FFT of the temperature field along the horizontal axis shows a peak at wavelength `λ ≈ 2 * cube_height` within ±30%. Empirically observed Rayleigh-equivalent number matches analytical prediction.

**T3 Crystallization.** Uniform-frequency vibration injection at hot floor, 5000 ticks. `count_structures(top_half) / count_structures(bottom_half) > 5.0`.

**T4 Decay-without-flux.** Form structures via T3. Disable injection. 5000 more ticks. `structure_count(end) / structure_count(peak) < 0.10`.

T1 runs as part of every test in the suite (it's an inline assertion).

## 8. Components

| File | Status | Purpose |
|---|---|---|
| `world/flux/quantum.py` | NEW | Vibration entity with `energy_quantum` |
| `world/flux/grid.py` | NEW | Voxel grid + temperature field |
| `world/flux/boundary.py` | NEW | Hot/cold faces, injection/absorption |
| `world/flux/binding.py` | NEW | The one binding rule |
| `world/flux/structures.py` | NEW | Node + bridge graph |
| `world/flux/plasticity.py` | NEW | Flux-driven Hebbian plasticity |
| `world/flux/dynamics.py` | NEW | Main tick loop |
| `world/flux/audit.py` | NEW | Energy conservation accounting |
| `agent/flux/cochlea.py` | NEW | Resonator bank input |
| `agent/flux/synthesis.py` | NEW | Resonator bank output (inverse) |
| `agent/flux/attention.py` | NEW | PE-weighted compute allocation |
| `agent/flux/loop.py` | NEW | Top-level driver |
| `tests/flux/test_conservation.py` | NEW | T1 |
| `tests/flux/test_benard.py` | NEW | T2 |
| `tests/flux/test_crystallization.py` | NEW | T3 |
| `tests/flux/test_decay.py` | NEW | T4 |
| `docs/flux/principle.md` | NEW | Long-form explanation of the principle |
| `docs/flux/phase-log.md` | NEW | Append-only build log of phases F0-F6 |

Legacy code (`world/`, `agent/` without `flux/`) is untouched. README gets a paragraph naming both substrates.

## 9. Roadmap

| Phase | Binary contract | Estimated weeks |
|---|---|---|
| **F0** | Skeleton + T1 (conservation) passes | 1 |
| **F1** | T2 (Bénard), T3 (Crystallization), T4 (Decay) pass | 4–6 |
| **F2** | Cochlea + Synthesis: 1 kHz tone burst injected → frequency-matched ringing in output | 4–8 |
| **F3** | **Tier 1**: log-likelihood improvement of trained vs untrained on 60-min audio, p < 0.01 | 6–10 |
| **F4** | **Tier 2**: Linear probe on internal states classifies phonemes ≥ baseline + threshold (X set after measuring baseline at end of F3) | 8–16 |
| **F5** | **Tier 3**: Attention-PE correlation ≥ 0.4 + measurable wandering | 4–8 |
| **F6** | Paper draft (positive or negative result) | 4–8 |

Total: 31–58 weeks of focused work. Honest range: 6–12 months for a solo developer.

## 10. Open questions (to be resolved during F0/F1)

These are not decisions for the spec — they are calibration choices that emerge from running the code:

- Exact values of `α`, `β`, `T_crit`, `η`, `r`, `τ`, `γ`, `λ`, `flux_min`, `N_decay`, `δ`, `α_T`
- Voxel size / cube dimensions for Phase 1 (60³ may be too large for Bénard validation; might shrink to 20×60×20)
- Whether N_cochlea = 64 is enough; cochlea-bank tuning curves
- Whether to add a velocity damping coefficient (mean free path) to keep simulation stable
- Implementation language for hot inner loop (Numba like legacy code, or numpy-vectorised, or Cython, or Mojo)

These are not pre-registered; they will be calibrated empirically against the Phase 1 validation tests.

## 11. Pre-registration

The four Phase 1 tests, the three falsifier tiers, and the falsifier thresholds (where pre-settable) are pre-registered in this spec at commit time. Calibrating thresholds after a failed run, then claiming a new run passes, is excluded by protocol.

If Phase 1 tests do not pass with reasonable parameter sweeps within 12 weeks of F1 start, the binding rule itself is reconsidered (not the thresholds). This is logged honestly in `docs/flux/phase-log.md`.

## 12. License and provenance

Same license as EQMOD repo (MIT for code, CC-BY-SA for docs). This spec is the brainstorm output of conversation between the project author and a Claude Opus session on 2026-05-10. The principle itself (energy-flux-driven autopoiesis) is not novel; the combination as a working computational substrate is the bet.

## 13. Next step

User review of this spec. After approval, hand off to `superpowers:writing-plans` to produce the F0 implementation plan.
