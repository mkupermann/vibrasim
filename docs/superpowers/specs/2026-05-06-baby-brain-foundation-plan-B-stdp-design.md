# Sub-project B — STDP and directional bridge plasticity

**Date:** 2026-05-06
**Status:** draft (awaiting user approval; ready to convert to a writing-plans plan once approved)
**Parent design doc:** `docs/superpowers/specs/2026-05-06-baby-brain-foundation-design.md` §3.5
**Prerequisite:** Plan A (substrate growth amendments) complete and merged

---

## 1. What this sub-project adds

Plan A made bridges *exist*. When two atoms fire close in time, level-5+ molecules in the region between them accumulate strength via the `r_strengthen`-radius reinforcement rule, and weak structures fade via inverse-strength decay. The result: persistent molecule "bridges" between repeatedly co-firing atoms.

What Plan A did **not** do: distinguish A→B from B→A. A bridge molecule between two atoms that fire in either order looks identical to one between two atoms that always fire A-then-B. Real synapses are directional. Without directionality, the substrate can record "these two regions are correlated" but not "this region predicts the other".

Plan B adds three things on top of Plan A:

1. **A per-node orientation vector** — `k_orientation: np.ndarray`, shape `(K, 3)`. For each level-5+ molecule, this records the preferred A→B propagation direction, inferred from the order in which the surrounding atoms fired.

2. **A spike-timing-dependent plasticity rule** (STDP). After each tick, scan the firing log for ordered atom pairs within a short time window (τ_LTP ≈ 20 ms). For each causal pair A→B, *strengthen* the bridge molecules between them and *update their orientation* toward A→B. For each anticausal pair B→A, *weaken* the same bridge molecules. The strengthen/weaken magnitudes decay exponentially with the inter-spike interval — canonical STDP.

3. **A synaptic transmission rule** that turns the orientation field into actual signal flow. Vibrations passing through a strongly-reinforced bridge molecule with a stable orientation deposit charge into the post-synaptic atom in the orientation direction. This is the substrate-level analog of pre→post current flow at a synapse — and it is what makes a chain of bridges become a circuit that can predict, sequence, and (in later sub-projects) learn.

All three are gated behind `stdp_enabled: bool = False`. With the flag off, nothing changes from Plan A.

## 2. Why this scope, not less, not more

**Why not split** the orientation field and the synaptic transmission rule into two sub-projects? Because without transmission, orientation is just a number that nobody reads. We have no way to *verify* the directionality is working unless the orientation actually causes asymmetric behaviour somewhere else in the substrate. The minimum testable unit is "STDP + orientation + transmission".

**Why not include** the live-IO loop, the audio encoder, or the video encoder here? Because those run as separate I/O subsystems against the substrate's port regions, and they don't depend on STDP being implemented to work. They are Plans C, D, E.

**Why not generalise** the STDP rule to anti-Hebbian or other learning shapes? Because we have one concrete acceptance test (the glass-of-water demo from the foundation spec §6.2 M4) and STDP with bridge orientation is the simplest mechanism that can plausibly pass it. Generalisation comes when we know what the substrate actually does.

## 3. New per-node fields

Added to `World.__init__` after `k_strength`:

```python
# Plan B — per-molecule orientation vector for directional propagation.
# Zero vector = no orientation inferred yet. Updated as a strength-weighted
# running average when STDP detects a directional firing pair.
self.k_orientation = np.zeros((K, 3), dtype=np.float64)
```

Persisted in `save_snapshot` and `load_snapshot` with the same backward-compat guard pattern as `k_strength`. Old snapshots without the field load cleanly with all-zero orientation.

## 4. New configuration parameters

Added to `WorldConfig` (all default off / inert so Plan A behaviour is preserved):

```python
# Plan B — STDP and directional plasticity
stdp_enabled: bool = False              # master switch
tau_LTP: float = 0.020                  # pre-before-post window (s)
tau_LTD: float = 0.020                  # post-before-pre window (s)
delta_LTP: float = 1.0                  # LTP strength increment per qualifying pair
delta_LTD: float = 0.5                  # LTD strength decrement per qualifying pair
r_bridge: float = 5.0                   # bridge tube radius around the A→B line segment
synaptic_transmission_strength: float = 0.5  # charge deposited per crossing vibration
synaptic_transmission_threshold: float = 5.0  # min bridge strength before transmission activates
```

## 5. Algorithms

### 5.1 STDP scan (`apply_stdp(world)`)

Runs once per tick, after `neuron_dynamics(world, dt)` produces this tick's `world.firing_events`. The scan considers all firing events with `t > world.t - tau_LTP` (i.e. within one window of the present tick).

```
For each ordered pair (i, j) in recent firings, with t_j - t_i in (0, tau_LTP]:
    delta_t = t_j - t_i
    A_pos = world.k_pos[atom_i]
    B_pos = world.k_pos[atom_j]
    bridge_indices = molecules_in_tube(world, A_pos, B_pos, r_bridge)
    weight_LTP = delta_LTP * exp(-delta_t / tau_LTP)
    weight_LTD = delta_LTD * exp(-delta_t / tau_LTD)
    For each m in bridge_indices:
        # The pair (i, j) is causal A→B: this is a pre-before-post pair from
        # m's perspective if its current orientation is closer to A→B than B→A,
        # and an anti-causal pair otherwise. Without an existing orientation
        # (zero vector), we treat all causal pairs as LTP and skip LTD.
        u = unit(B_pos - A_pos, periodic_min_image)
        if k_orientation[m] is zero or dot(k_orientation[m], u) >= 0:
            apply_LTP(world, m, weight_LTP, u)
        else:
            apply_LTD(world, m, weight_LTD)
```

`apply_LTP(world, m, w, u)` does two things:
1. `k_strength[m] += w` (capped at some ceiling, e.g. 1000.0, to prevent runaway)
2. Update `k_orientation[m]` as a strength-weighted running average:
   ```
   strength_old = k_strength[m] - w
   k_orientation[m] = (k_orientation[m] * strength_old + u * w) / k_strength[m]
   k_orientation[m] /= max(np.linalg.norm(k_orientation[m]), 1e-9)  # renormalise
   ```
   The renormalisation keeps `|k_orientation| ≤ 1` so it can be used as a unit vector elsewhere.

`apply_LTD(world, m, w)` only weakens:
1. `k_strength[m] = max(k_strength[m] - w, 1.0)` (floored at 1, so a heavily-decayed bridge can still recover later)
2. Orientation is **not** updated by LTD — losing strength shouldn't change which way a bridge points; it should just make the bridge less confident. If LTD reduces strength to 1.0, the orientation is left as-is.

### 5.2 Bridge tube identification (`molecules_in_tube`)

Given two atom positions A, B and radius `r_bridge`, returns the indices of alive level-5+ molecules whose perpendicular distance to the segment A→B is ≤ r_bridge AND whose projection along the segment is within [0, |B-A|].

Standard segment-distance math, with periodic minimum-image applied to (M - A):

```python
def molecules_in_tube(world, A, B, r_bridge):
    box = np.asarray(world.config.box_size)
    K = world.k_count
    mol_mask = world.k_alive[:K] & (world.k_level[:K] >= 5)
    if not mol_mask.any():
        return np.empty(0, dtype=np.int64)
    indices = np.where(mol_mask)[0]
    M_pos = world.k_pos[indices]

    # Periodic min-image on (M - A)
    rM = M_pos - A
    rM -= box * np.round(rM / box)
    v = B - A
    v -= box * np.round(v / box)
    v_len_sq = float((v * v).sum())
    if v_len_sq < 1e-12:
        return np.empty(0, dtype=np.int64)

    # Projection scalar t = dot(rM, v) / dot(v, v); clamp to [0, 1]
    t = (rM * v).sum(axis=1) / v_len_sq
    in_segment_mask = (t >= 0.0) & (t <= 1.0)
    # Perpendicular component
    proj = t[:, None] * v
    perp = rM - proj
    perp_dist_sq = (perp * perp).sum(axis=1)
    in_tube_mask = perp_dist_sq <= r_bridge ** 2
    return indices[in_segment_mask & in_tube_mask]
```

### 5.3 Synaptic transmission (`synaptic_transmission(world, dt)`)

Runs inside `neuron_dynamics`, after the existing integration pass. For each level-5+ molecule with strength above threshold AND non-zero orientation:

```
For each m where k_strength[m] >= threshold and |k_orientation[m]| > 0.5:
    M_pos = world.k_pos[m]
    o = world.k_orientation[m]
    # The "post-synaptic side" lies in the direction of o from M
    post_search_centre = M_pos + r_bridge * o
    # Find alive vibrations within r_bridge of M
    free_vibration_indices = find_vibrations_near(world, M_pos, r_bridge)
    # Find alive level-4 atoms within r_bridge of post_search_centre
    post_atom_indices = find_atoms_near(world, post_search_centre, r_bridge)
    if not post_atom_indices:
        continue
    # Each crossing vibration deposits charge into all post-synaptic atoms,
    # weighted by alignment of vibration velocity with orientation
    for v_idx in free_vibration_indices:
        v_vel = world.s_vel[v_idx]
        v_speed = np.linalg.norm(v_vel)
        if v_speed < 1e-9:
            continue
        alignment = float(np.dot(v_vel / v_speed, o))
        if alignment <= 0:
            continue  # vibration moving against orientation; no transmission
        for a_idx in post_atom_indices:
            world.k_charge[a_idx] += alignment * w_synaptic * dt
```

Performance note: this is potentially O(M × V × A) per tick where M is the number of strong bridges, V is vibrations near each, A is atoms near the post side. A spatial-hash query (`world.spatial_hash` if present, else a brute-force radius query) keeps each per-bridge step proportional to the local population, not the global one.

`w_synaptic = cfg.synaptic_transmission_strength`. Threshold = `cfg.synaptic_transmission_threshold`.

### 5.4 Wiring into `tick`

After Plan A:

```python
def tick(world, dt):
    box = ...
    move_vibrations(...)
    apply_scale_repulsion(world, dt)
    move_nodes(world, dt)
    bind_vibrations_to_electrons(world)
    bind_nodes_upward(world)
    decay_unstable_nodes(world, dt)
    decay_high_level_nodes(world, dt)        # Plan A R2
    ambient_regeneration(world, dt)           # Plan A R1
    neuron_dynamics(world, dt)                # PHASE4 + Plan A strengthening + Plan B transmission
    apply_stdp(world)                         # Plan B STDP scan (NEW)
    world.t += dt
```

`synaptic_transmission` is invoked from inside `neuron_dynamics` because it modifies atom charges, which are part of the same integrate-and-fire state and should be applied before the threshold check that decides who fires this tick. Specifically, the order inside `neuron_dynamics` becomes:

```
1. Decay all atom charges (existing)
2. Integrate input vibrations into atom charges (existing)
3. Synaptic transmission: strong bridges deposit charge into post-synaptic atoms (NEW)
4. Threshold + fire (existing)
5. Refractory bookkeeping (existing)
6. R2 strengthening pass (Plan A)
```

Putting transmission at step 3 means a single bridge can influence whether the post-synaptic atom fires this tick — the standard synaptic-integration semantics.

## 6. Acceptance tests

### 6.1 Necessary (unit + integration)

| ID | Test | Pass criterion |
|---|---|---|
| BS1 | Pair detection | Manually inject a firing log with `(t=0, atom_A)` and `(t=0.010, atom_B)`, no other firings. After `apply_stdp`, the bridge molecules between A and B have `k_strength` increased by `delta_LTP * exp(-0.010 / 0.020) ≈ 0.61` (within ±0.01). Out-of-tube molecules are unchanged. |
| BS2 | Outside time window | Same setup but with `t_B - t_A = 0.050` (i.e. ≥ τ_LTP=0.020 s scaled appropriately, here outside the window). Bridge molecules unchanged. |
| BS3 | Outside spatial tube | Place a level-5 molecule far from the A→B segment (perpendicular distance > r_bridge). After STDP, that molecule's strength is unchanged. |
| BS4 | Asymmetric LTP / LTD | Run 100 paired-pulse trials in *both* orders alternately (A→B at t=0, then B→A at t=0.5s, repeat). After 100 pairs, LTP and LTD apply equally — bridge strength should net out near baseline (within ±20% of baseline). |
| BS5 | Orientation update | Run 50 paired pulses A→B at fixed positions (A=(50,50,50), B=(70,50,50)). After 50 pairs, every bridge molecule's `k_orientation` is within 5° of the unit vector (1, 0, 0), and its norm is in [0.95, 1.05]. |
| BS6 | Synaptic transmission charges post-synaptic atom | Build a single bridge molecule at (60,50,50) with `k_strength=20`, `k_orientation=(1,0,0)`. Place a level-4 atom at (65,50,50). Place a vibration at (60,50,50) with velocity (15, 0, 0). After one tick, the post-synaptic atom's `k_charge` increased by approximately `1.0 (alignment) * 0.5 (w_synaptic) * dt`, within ±5%. |
| BS7 | Misaligned vibration is ignored | Same setup but vibration velocity is (-15, 0, 0) (opposite direction). Post atom charge unchanged. |
| BS8 | Snapshot round-trip for `k_orientation` | Set `k_orientation[3] = (0.7, 0.3, 0.0)`, save, load. Loaded value matches within float64 precision. |

### 6.2 Headline integration test

| ID | Test | Pass criterion |
|---|---|---|
| **P1** | **Causal pair training (foundation spec §6.1)** | 100 paired-pulse trials, A fires at `t = k * 0.5`, B fires at `t = k * 0.5 + 0.010` for k=0..99. After all trials: bridge molecules in A→B tube have strength ≥ 5; bridge molecules in B→A tube (same physical molecules — measured with reversed segment order) have strength bias such that `k_orientation · (B - A) > 0.8`. Confirms STDP correctly distinguishes A→B from B→A. |

### 6.3 Stretch

| ID | Test | Pass criterion |
|---|---|---|
| P2 | STDP timing curve | Vary inter-spike interval Δt across [-50, +50] ms. For each Δt, run 20 paired pulses and measure mean ΔStrength of bridge molecules. The resulting curve must: peak at Δt = 5–10 ms with ΔStrength ≈ δ_LTP * exp(-(7.5e-3)/τ_LTP) ≈ 0.69, fall to near-zero at Δt = ±50 ms, and reach a negative minimum at Δt = -5 to -10 ms with ΔStrength ≈ -δ_LTD * exp(-(7.5e-3)/τ_LTD) ≈ -0.34. |
| P3 | Plasticity-driven prediction | Train: 50 paired-pulse trials A→B with 10 ms lag. Test phase: stimulate A only (no direct stimulation of B). Measure: B's firing rate during test phase is ≥ 2× B's baseline firing rate before training. This is the "circuit learning" demo — a trained chain of bridges propagates signal forward. |

## 7. New module / test layout

```
world/
  config.py              # extended with stdp_enabled, tau_LTP, tau_LTD, delta_LTP, delta_LTD, r_bridge, synaptic_transmission_*
  state.py               # adds k_orientation field
  snapshot.py            # extended with k_orientation persistence
  physics.py             # adds apply_stdp, synaptic_transmission, molecules_in_tube; wires into tick + neuron_dynamics

tests/
  test_amendment_stdp_pair_detection.py         # BS1-BS3
  test_amendment_stdp_asymmetric_plasticity.py  # BS4
  test_amendment_stdp_orientation_update.py     # BS5
  test_amendment_synaptic_transmission.py       # BS6, BS7
  test_amendment_stdp_snapshot.py               # BS8
  test_stdp_e2e.py                              # P1 (and optionally P2, P3 marked slow)
```

## 8. Out of scope (still)

- **Audio I/O, video I/O, reward channel, agent loop** — Plans C, D, E.
- **Brain checkpoint extension to firing-event tail** — Plan F. Plan B only adds `k_orientation` to the snapshot; the firing event log persistence comes later.
- **Bridge pruning** — beyond simple LTD, no removal of bridge molecules from the substrate. Decay (Plan A R2) handles dying bridges naturally.
- **Multi-bridge chain reinforcement** — STDP is strictly pairwise. A chain A→B→C is reinforced by A→B pairs and B→C pairs separately; we don't reinforce a chain as a unit.
- **STDP across modalities** — once audio + video ports exist, the same STDP rule applies to bridges spanning the boundary, but no new mechanism is needed; this is a free property.

## 9. Decision log

- **Why exponential weighting on Δt** — canonical biological STDP. Hebbian learning is fundamentally about temporal coincidence, and exponential decay captures the "correlation window" with one parameter. Linear or step-function alternatives have similar effect for the small-Δt regime we care about and are not worth the extra knob.
- **Why orientation update is strength-weighted (not learning-rate-α)** — strength weighting means heavily-reinforced bridges resist orientation flipping, which is biologically plausible (mature synapses are stable). Fixed α would let a single new pair tilt a long-trained bridge, which is too plastic.
- **Why orientation is NOT updated by LTD** — losing strength shouldn't change "which way" a bridge points; it should just make the bridge less confident. The orientation should fade toward zero only via decay (Plan A R2 already does this — if strength → 1, orientation × strength_old / strength_new dilutes).
- **Why synaptic transmission is gated by both strength AND orientation magnitude** — we don't want unstable, partially-formed bridges (low strength, scattered orientation) to leak charge into the wrong atoms. Both gates have to clear before the bridge is trusted to transmit.
- **Why per-vibration alignment dot product (not all-or-nothing)** — graded transmission lets fast-moving vibrations align poorly and contribute less, without an arbitrary threshold. Matches the dot-product semantics of the spec text.
- **Why `delta_LTD < delta_LTP`** — biological STDP has roughly LTP / LTD ratio of 2. Default `delta_LTP=1.0, delta_LTD=0.5` matches this. Tunable.
- **Why no learning-rate decay over time** — STDP is a per-pair rule; the system's overall learning rate is governed by how often pairs occur (which is governed by firing rate, which is governed by upstream dynamics). Adding a separate global decay would be a third tunable that doesn't add explanatory power.

## 10. Risks and what to watch for

- **Computational cost of `apply_stdp` per tick.** With N firings per tick, the pair scan is O(N²) per tick on its face; with N≤20 typical, this is fine, but aggressive runs with N≥100 firings/tick will see noticeable slow-down. If P1 is slow, switch the inner pair loop to use a sliding window indexed on `firing_events` (only consider pairs where `t_j - t_i ≤ τ_LTP`).
- **Orientation field instability** when a bridge molecule has multiple "post" atoms in different directions. The strength-weighted running average will converge to the dominant direction over time, but during early training the orientation may flicker. P1 (100 trials) should give it enough samples; if not, increase the trial count.
- **Synaptic transmission feedback loops.** A→B→C where each transmission deposits charge could in principle cause runaway oscillation. Mitigation: refractory window (already in PHASE4-R3) prevents same-atom re-firing within `t_refractory`; transmission charge is scaled by `dt`, so it's a rate not an impulse.
- **Snapshot size growth.** `k_orientation` adds 24 bytes per node. With `n_nodes_max=1024`, that's 24 KB per snapshot — negligible.

---

## Approval gate

Before this becomes a writing-plans plan, the user should confirm:

1. **The synaptic transmission mechanism** (§5.3) is acceptable — vibrations crossing strong, well-oriented bridges deposit charge into post-synaptic atoms in the orientation direction. This is the substrate's analog of pre→post current flow.

2. **The orientation update rule** (§5.1) — strength-weighted running average, renormalised to unit length. An alternative is a fixed learning rate α. Strength-weighted is more stable but updates more slowly.

3. **Acceptance test P1** in §6.2 — 100 paired-pulse trials with 10 ms lag, asserting both strength asymmetry AND orientation alignment. Is the acceptance threshold `k_orientation · (B-A) > 0.8` reasonable, or should it be tighter / looser?

4. **The stretch tests P2, P3** — should they be in scope for Plan B, or moved to Plan G (end-to-end demo)?

If approved, this design becomes the basis for `docs/superpowers/plans/2026-05-06-baby-brain-foundation-plan-B-stdp.md`, with bite-sized TDD tasks following the same pattern as Plan A.
