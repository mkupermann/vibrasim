# Phase 4 Neuron Firing Experiments — Findings

**Date:** 2026-05-06
**Substrate:** vibrasim EQMOD (commit HEAD, branch main — unmodified)
**Config:** `renders/calibration_session3b_molecules.toml`
  Box 60³, 800 initial vibrations cap, lambda_gen=0, lambda_dec=0, dt=1/60 s
**Cluster:** 8 atoms (level 4) + 6 molecules (level 5), radius=6, axis=(1,0,0), centre=(30,30,30)
  Inlet: (33.6, 30, 30) — 0.6r along +x from centre
  Outlet: (26.4, 30, 30) — 0.6r along −x from centre
  r_io = 1.8 units (0.3 × radius)
**Firing criterion:** output snapshot count ≥ 5 × mean baseline output count

---

## 1. Experiment A — Passive Observation

**Setup:** 30 simulated s, snapshot every 1 s, 0 initial vibrations, no stimulation.

- Snapshots: 30
- Baseline output rate (mean counts/snapshot): 0.000
- Firing threshold (5× baseline): 1.000
- Input total: 0,  Output total: 0
- Firing events: 0
- Integration lag: N/A
- Refractory period: N/A
- Wall time: 3.2 s

### Per-second input/output counts

| t (s) | inlet count | outlet count |
|-------|-------------|--------------|
|    1.0 | 0 | 0 |
|    2.0 | 0 | 0 |
|    3.0 | 0 | 0 |
|    4.0 | 0 | 0 |
|    5.0 | 0 | 0 |
|    6.0 | 0 | 0 |
|    7.0 | 0 | 0 |
|    8.0 | 0 | 0 |
|    9.0 | 0 | 0 |
|   10.0 | 0 | 0 |
|   11.0 | 0 | 0 |
|   12.0 | 0 | 0 |
|   13.0 | 0 | 0 |
|   14.0 | 0 | 0 |
|   15.0 | 0 | 0 |
|   16.0 | 0 | 0 |
|   17.0 | 0 | 0 |
|   18.0 | 0 | 0 |
|   19.0 | 0 | 0 |
|   20.0 | 0 | 0 |
|   21.0 | 0 | 0 |
|   22.0 | 0 | 0 |
|   23.0 | 0 | 0 |
|   24.0 | 0 | 0 |
|   25.0 | 0 | 0 |
|   26.0 | 0 | 0 |
|   27.0 | 0 | 0 |
|   28.0 | 0 | 0 |
|   29.0 | 0 | 0 |
|   30.0 | 0 | 0 |

**Interpretation:** All counts are 0. The substrate is deterministic with 0 initial
vibrations and no ambient generation. The constructed cluster is inert without a
free-vibration bath. Experiment A establishes the zero baseline cleanly.

---

## 2. Experiment B — Active Stimulation

**Setup:** 10 vibrations per burst, injected within r_io=1.8 of inlet, directed
inward. Snapshot every 0.5 s. (B_high ran for 15 simulated s due to time budget;
others ran 30 s.)

| Run | Stim rate | Input rate/s | Output rate/s | Baseline/snap | Firing events | Integ. lag | Refractory |
|-----|-----------|-------------|---------------|---------------|---------------|------------|------------|
| B_low | 1/s | 20.8/s | 1.03/s | 0.52 | 2 | 500 | 13000 |
| B_medium | 5/s | 40.2/s | 18.00/s | 9.00 | 0 | — | — |
| B_high | 20/s | 125.7/s | 30.93/s | 15.47 | 0 | — | — |

### B_low detail (1 burst/s, 30 s)
- Snapshots: 60
- Baseline output rate (mean counts/snapshot): 0.517
- Firing threshold (5× baseline): 2.583
- Input total: 624,  Output total: 31
- Firing events: 2
  [0] t_start=6.50s  t_peak=6.50s  peak_count=3  duration=0.500s
  [1] t_start=19.50s  t_peak=19.50s  peak_count=3  duration=0.500s
- Integration lag (mean): 500.0 ms
- Refractory period (mean): 13000.0 ms
- Wall time: 13.1 s

### B_medium detail (5 bursts/s, 30 s)
- Snapshots: 60
- Baseline output rate (mean counts/snapshot): 9.000
- Firing threshold (5× baseline): 45.000
- Input total: 1205,  Output total: 540
- Firing events: 0
- Integration lag: N/A
- Refractory period: N/A
- Wall time: 174.8 s

### B_high detail (20 bursts/s, 15 s)
- Snapshots: 30
- Baseline output rate (mean counts/snapshot): 15.467
- Firing threshold (5× baseline): 77.333
- Input total: 1886,  Output total: 464
- Firing events: 0
- Integration lag: N/A
- Refractory period: N/A
- Wall time: 259.9 s

---

## 3. Verdict

**Passive (Experiment A):** 0 firing events over 30 simulated s. Total input-region counts = 0, output-region counts = 0. The inlet and outlet sub-spheres are entirely silent: with n_initial_vibrations=0 and lambda_gen=0 the constructed cluster has nothing to interact with. The cluster is static — nodes sit at their constructed positions, no vibrations arrive. This confirms the cluster itself does not spontaneously generate activity.

**Stimulated (Experiment B):** 2 firing events total across three rates (low=2, medium=0, high=0).

At 1 burst/s: input total=624, output total=31. 2 firing event(s). Output counts are low; the 2 apparent events are coincidental density spikes at the outlet, not reproducible threshold crossings (single-snapshot events, peak_count=3 barely exceeds the threshold of 2.58 set by a very low baseline).

At 5 bursts/s: input total=1205, output total=540. Output/input ratio = 0.45. 0 firing events. The high baseline (9.0 counts/snapshot) raises the firing threshold to 45, which is never reached — the output is steady diffusion, not bursting. Roughly half the injected vibrations pass through to the outlet region.

At 20 bursts/s (15 s): input total=1886, output total=464. Output/input ratio = 0.25. 0 firing events. By 15 s, k_count = 1798 (nearly all injected vibrations have formed electrons/atoms). The output rate is significant (15.5 counts/snapshot) but flat — no burst exceeds 5× baseline.

**Overall pattern:** Output rate scales roughly linearly with stimulation rate (31/30s → 540/30s → 464/15s), consistent with **pass-through / diffusion**, not integration. The output region sees a continuous trickle proportional to input density; there is no accumulation phase, no threshold crossing, no burst, and no refractory silence.

**Conclusion:** The substrate does **not** produce neuron-like firing. Injected vibrations diffuse through the cluster and bind into nodes under the standard electron-formation rules; the outlet sphere detects these passing events as a steady low-level rate. There is no internal accumulator, no threshold, and no refractory period. The two apparent 'events' at 1 burst/s are noise (single-snapshot, peak_count=3, threshold=2.58 — artefact of a near-zero baseline). The Phase 4 acceptance criterion (integration + threshold + refractory) is **not met** by the current substrate.

---

## 4. What the substrate would need for genuine neuron-like firing

The gap between what exists and what Phase 4 requires is structural, not
numerical. The following extensions are the minimum necessary:

### 4.1 Accumulator field
Add `k_charge: float[K]` and `k_refractory_until: float[K]` to `world/state.py`
(two new arrays, ~4 lines). Each tick, after `bind_vibrations_to_electrons()`,
scan vibrations inside r_io of the inlet centre. For each vibration that docks to
an inlet-region atom (`world.k_comp_indices` entries for newly formed electrons
inside the inlet sphere), increment `k_charge[atom]` by 1. Apply exponential
decay: `k_charge[i] *= exp(-dt / tau_m)` where `tau_m` is the membrane time
constant (e.g., 10 ms simulated).

### 4.2 Threshold rule
In `tick()`, after the charge update: if `k_charge[i] >= theta` for any
cluster atom `i` that is not in refractory:
- Emit `N_out` (e.g., 5–10) free vibrations at the outlet centre with isotropic
  thermal velocities (same pattern as `_inject_vibrations` above).
- Reset `k_charge[:] = 0` for all cluster atoms.
- Set `k_refractory_until[i] = world.t + T_r` for all cluster atoms.

### 4.3 Refractory rule
During the charge-accumulation step, skip any atom `i` with
`world.t < world.k_refractory_until[i]`. This produces the hard refractory
period the acceptance criterion requires.

### 4.4 Directional geometry (optional but necessary for clean separation)
The inlet/outlet sub-spheres are measurement artefacts — the physics does not
distinguish them. For input vibrations to preferentially dock to inlet atoms
rather than to any cluster atom, the inlet atoms' frequencies should be tuned to
match the injection frequency range. Set `base_freq_atom` for the four atoms
on the +x half of the cluster to, e.g., 1000 Hz, so the `freq_tolerance` window
(3%) selects them over the outlet atoms.

### 4.5 Practical estimate
All four extensions together require approximately 40–60 additional lines in
`world/physics.py` and `world/state.py`, and one new argument
(`cluster_infos: list[dict]`) passed through `tick()`. No existing physics rules
need to be modified — the change is purely additive. A single test run at
5 bursts/s with `theta=5, tau_m=0.01, T_r=0.01` should produce clearly
separated firing events visible in `measure_neuron_activity` output.

---

## 5. Wall time

| Phase | Wall time |
|-------|-----------|
| Experiment A (30 s sim) | 3.2 s |
| Experiment B_low (30 s sim, 1 burst/s) | 13.1 s |
| Experiment B_medium (30 s sim, 5 bursts/s) | 174.8 s |
| Experiment B_high (15 s sim, 20 bursts/s) | 259.9 s |
| **Total** | **451 s (7.5 min)** |

Performance note: wall time scales super-linearly with stimulation rate because
each injected vibration that binds increases `k_count`, and `bind_nodes_upward()`
is O(k_count × neighbours). At 5 bursts/s, 1500 injected vibrations over 30 s
grew k_count to >1400, pushing wall time to 174 s for 30 simulated s. At 20
bursts/s the growth is even faster. A spatial-index optimisation in
`bind_nodes_upward()` (e.g., cell-list with smaller cell radius) would recover
near-linear scaling.
