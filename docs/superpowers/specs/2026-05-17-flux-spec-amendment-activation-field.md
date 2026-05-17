# Spec Amendment §5.8 — Activation Field Overlay

> **Status:** proposed 2026-05-17 23:00 by Claude under user authorization "Du kannst die Spec Erweiterungen setzen".
>
> **Position:** additive to existing spec (`docs/superpowers/specs/2026-05-10-flux-substrate-design.md`). Discrete quanta remain primary; the activation field is bookkeeping that smooths the plasticity signal.

## Why this amendment

Eight vacation NULLs across two substrate-learning paths:

- **R-1c, R-1c-bis, R-1c-tris, R-1c-quad** (Bénard robustness): point-particle substrate without continuum representation cannot reliably produce fluid-dynamical convection. Acknowledged limitation; this amendment does NOT address it.

- **R-8** (cochlea baseline training): broadband speech spread thinly across 64 log-spaced resonators; per-resonator peak averages ~0.3, rarely clears the binding gate's proximity check. Single events too noisy.

- **R-5, R-11** (F3 learning + encoder-free): pre-registered acceptance involves substrate developing pattern-specific topology from repeated inputs. The monotone-flux plasticity rule (spec §5.5) integrates flux through bridges, but the flux signal is dominated by Poisson density fluctuations of discrete quanta. Single quanta-pair events are too noisy to drive stable potentiation.

Common cause across the audio paths: **plasticity signal is event-discrete, learning targets are time-continuous**. The substrate has no mechanism to integrate over a relevant temporal window. Each binding event is independent of recent history beyond what already happens via existing bridge state.

This amendment adds a slow per-voxel memory trace that decays over relevant audio timescales (≈100 ms–1 s), enabling plasticity to read from a smoothed signal instead of raw event noise.

## Definition

For each voxel `(x, y, z)`, maintain a scalar **activation field** `A[x,y,z,t] ∈ [0, ∞)`. Update per tick (after the existing density / T update):

```
A[x,y,z,t+1] = A[x,y,z,t] * (1 - alpha * dt)            # exponential decay
             + beta * sum_alive_quanta_in_voxel(energy)  # firings deposit
```

Default parameters (pre-registered here; locked for the implementing session):

| Parameter | Default | Purpose |
|---|---|---|
| `alpha` (field decay rate) | 1.0 / s | half-life ≈ 0.69 s — covers a phoneme-timescale window |
| `beta` (firing → field deposit) | 1.0 | each quantum of energy contributes 1.0 to the field at its voxel per tick |
| `A_init` | 0.0 | field starts empty; populated by activity |

The field is **bookkeeping**, not an energy reservoir. T1 (conservation) is unaffected — energy still tracked through the existing quanta-energy + binding-heat + decay-heat + export ledger. The field is a read-only smoothing of the quanta state.

## Plasticity coupling

The existing monotone-flux plasticity rule from R-4's F3 plan (`docs/superpowers/plans/2026-05-16-flux-substrate-F3.md`):

```
W_ij(t+1) = W_ij(t) + eta * flux(i,j,t) * dt        # current rule
```

is extended with a **coincidence gate** derived from the activation field at the bridge endpoints:

```
W_ij(t+1) = W_ij(t) + eta * flux(i,j,t) * coincidence(i,j,t) * dt   # extended rule

where coincidence(i,j,t) = sqrt( A[voxel_of_node_i, t] * A[voxel_of_node_j, t] )
                          / (A_norm + epsilon)

A_norm = a fixed normalization constant (cube-wide mean of A over the past
         1-second window, recomputed once per second; rolling stat, not
         a free parameter to tune)
```

`coincidence` is in [0, ~1] in practice. Bridges between voxels that are *both currently active* learn faster than bridges between voxels with only one active end. Bridges between currently-quiet voxels learn at near-zero rate.

This is a single-line change in the plasticity update inside `world/flux/plasticity.py` (or wherever the F3 rule lives). The field itself is a new module.

## What this addresses

| Failure mode | How the amendment changes it |
|---|---|
| R-8 cochlea broadband: per-resonator events too rare to fire binding | Field accumulates from many small events; coincidence-gated plasticity fires on the temporal AND across events, not on individual pair encounters |
| R-11 encoder-free: amplitude modulation invisible in instantaneous flux | Field decays over phoneme-timescale (~0.5 s); amplitude envelope IS the field. Plasticity reads envelope, not samples |
| Poisson density noise dominates flux signal | Field is the time-integrated density — noise averages out as 1/sqrt(N_quanta_in_window) instead of being event-level |

## What this does NOT address

- Bénard convection (T2): the field is per-voxel scalar, no spatial-mode dynamics. Bénard limitation stays as documented in iter-1 NULLs. Out of scope.
- T3 crystallization robustness: R-1d-T3-bis already handled. Field overlay should not affect T3 if it doesn't touch binding.
- The "encoder-free demonstrates self-organizing audio representation" claim: amendment makes it *more likely* but doesn't guarantee. The long-run R-LR-6 below is the test.

## Implementation plan (R-12)

R-12 implements the field + plasticity coupling in an autopilot 4-h slot.

**Files created:**
- `world/flux/activation_field.py` — `ActivationFieldConfig`, `update_field`, `read_coincidence`
- `tests/flux/test_activation_field.py` — unit tests per below

**Files modified:**
- `world/flux/dynamics.py` — wire field update into tick after T-update
- `world/flux/plasticity.py` (or wherever F3 rule lives) — add coincidence gate
- `world/flux/__init__.py` — re-exports
- `docs/flux/phase-log.md` — R-12 entries

**Pre-registered acceptance for R-12:**

- `tests/flux/test_activation_field.py::test_field_decays_exponentially PASSES` — feed a single deposit, run 0.69 s of ticks, assert field at half its initial value within 1% tolerance.
- `tests/flux/test_activation_field.py::test_field_responds_to_firings PASSES` — feed N quanta into a voxel, assert field magnitude tracks N * beta / alpha at steady state.
- `tests/flux/test_activation_field.py::test_coincidence_zero_when_both_endpoints_silent PASSES` — set A=0 at both endpoints, assert coincidence(i,j) == 0.
- `tests/flux/test_activation_field.py::test_coincidence_increases_with_paired_activity PASSES` — gradually raise A at both endpoints, assert coincidence increases monotonically.
- **Regression on Phase 1 robust items:** `tests/flux/test_conservation.py PASSES` (T1), `tests/flux/test_crystallization_robustness.py PASSES` (T3 9/10 from R-1d-T3-bis), `tests/flux/test_decay.py PASSES` (T4).
- **Regression on F3 implementation:** `tests/flux/test_learning.py -m "not slow" PASSES` — 11 fast tests from R-5 still green.

Time budget: 4 hours.

## Long-run validation (R-LR-6)

After R-12 lands on main, queue R-LR-6 to the long-run dispatcher: same configuration as R-LR-1 (encoder-free, 1.8M ticks, full English corpus) but on the field-equipped substrate.

**Pre-registered acceptance for R-LR-6 (locked here, no retuning):**

- `tests/flux/test_encoder_free_training_run.py::test_encoder_free_substrate_distinguishable_from_no_input_control PASSES` — same 2σ KL-divergence threshold as R-11. The amendment's job is to make this PASS where R-11 NULLed.
- `tests/flux/test_encoder_free_negative_control.py::test_no_input_control_produces_no_substrate_specific_signal PASSES` — same sanity check.
- LOGBOOK observation: tabulate KL(R-LR-6) vs KL(R-LR-1) — does the field help? If R-LR-1 is also queued as NULL, this comparison answers "did the amendment help" empirically.

## Expected costs

- R-12 implementation: ~4 h compute via autopilot (one slot).
- R-LR-6 long-run: ~13 h substrate run + ~5 min evaluation.

## Falsification rules

If R-LR-6 NULLs:
- The activation field does not provide enough learning signal at this timescale / parameter setting.
- This amendment, alone, does not enable encoder-free audio learning.
- Document in LOGBOOK. Possible next steps: (a) extend field to multi-timescale (fast + slow), (b) abandon plasticity-based learning entirely in favor of a different learning principle.

If R-LR-6 PASSES:
- Substrate develops audio-statistics-distinguishable structure when given activation field overlay.
- First demonstration of physics-substrate audio learning with continuous-time memory plus discrete-event binding.
- Activation field becomes a permanent fixture in the spec (§5.8 promoted from amendment to canonical).
