# Phase 5 Hebbian Plasticity Findings — §6.5 failure (informative)

**Agent:** Phase-5 plasticity teammate, 2026-05-06
**Goal:** test whether constructed synapses exhibit positive Hebbian plasticity under co-activity — CONCEPT.md v2 §6.3 mechanism + §6.5 open thermodynamic question.
**Result:** §6.5 failure mode confirmed empirically — but informative about which substrate rules are missing.

---

## Experiment A — passive baseline (60 s)

| Metric | Value |
|---|---|
| Snapshots | 120 |
| Co-active intervals | 0 |
| growth_rate_active | None |
| Hebbian signal | None (not computable) |
| store + recv sum series | constant at 11 throughout |

Establishes the null baseline: no spontaneous plasticity without stimulation.

---

## Experiment B — periodic co-stimulation (90 s each)

| Stim Period | growth_rate_active | growth_rate_inactive | Hebbian Signal | Co-active intervals |
|---|---|---|---|---|
| 1 s | None | ≈ 0 | None | 0 |
| 5 s | None | ≈ 0 | None | 0 |
| 20 s | None | ≈ 0 | None | 0 |

All three are physically identical. The injected vibrations had zero effect.

## Experiment C — uncorrelated control (90 s)

Same as B but pre/post stimulated at non-overlapping times:

| Metric | Value |
|---|---|
| Hebbian Signal | None |
| Co-active intervals | 0 |

Indistinguishable from B because injection was a no-op everywhere.

---

## Why everything failed — four structural deficiencies

**D1 — Vibration buffer saturation makes injection a no-op.** With `n_vibrations_max = 512` and `lambda_gen = 0.0002` in a 200³ box, ambient regeneration fills the buffer within the first few ticks. By t=0.5s all 512 vibration slots are alive. `inject_vibrations_at()` scans for dead slots, finds none, returns. Zero injected vibrations across all experiments.

**D2 — Level-5+ nodes are permanent and immobile.** `decay_unstable_nodes()` handles only levels 2-3. `ambient_regeneration()` decays only levels 1-3. Scale repulsion only fires when freq_ratio > 1000; inter-node ratios among level-5 molecules are 1.001-1.6. All 28 constructed level-5 nodes stay in identical positions for the entire 90-second run. store + recv is a flat integer (11) throughout.

**D3 — No "release on firing" mechanism.** §6.3 requires a synapse to release presynaptic store molecules into the cleft on activity, then capture from ambient to rebuild. There is no rule converting a level-5 store node to free vibrations on activity, and no rule assembling a new level-5 node from ambient near an active region. `bind_nodes_upward` could in principle assemble a level-5 from two level-4 atoms with matching decade/freq/polarity, but constructed neurons place atoms with non-matching decades, so this binding pathway never fires.

**D4 — Activity detection is blind to short transients.** `measure_activity()` counts free vibrations + level-1/2/3 nodes in r_io = 1.8 sub-spheres. Even if injection worked, vibrations travel at 10-50 units/s, so dwell time within r_io = 1.8 is 0.04-0.18 s — shorter than the 0.5 s snapshot interval.

---

## Tool bug found and fixed (C6)

`measure_synapse_plasticity.py` lines 179-180 had a shadowed-variable bug: `slopes_active` collected the window start time `s` instead of the actual `slope`. The Hebbian signal was silently meaningless (mean of start times − mean of start times). **FIXED** in the integration commit; regression test added (`test_growth_rate_active_is_actual_slope_not_window_start`).

---

## What the substrate needs (R1-R5)

For §6.5 to be answerable in this substrate:

**R1 — Fix vibration injection.** Either enlarge `n_vibrations_max` to 8000-16000 with `lambda_gen` tuned to keep ambient density non-saturating, or implement a "displace" injection that moves a far-field alive vibration to the target zone (preserves global count, creates local gradient).

**R2 — Add decay for level-5+ nodes.** Per-tick decay probability `lambda_dec_mol * dt` for level-5+, reviving constituent atoms. This is the "inactive synapses weaken" half of §6.3.

**R3 — Add local capture / assembly rule.** When vibration density near the presynaptic outlet exceeds a threshold, assemble a new level-5 store molecule. This is the "active region refills faster than it decays" half — the thermodynamically grounded strengthening from §6.3.

**R4 — Activity detector that can see synapse-region events.** Track level-5 count *changes* in the outlet/inlet regions directly (a level-5 appearing near the outlet = a release event), or shrink `n_vibrations_max` so free vibrations can locally accumulate.

**R5 — ✅ Fix the slope-collection bug** (done — see C6 above).

---

## Wall time

| Experiment | Simulated time | Wall time |
|---|---|---|
| A (passive 60s) | 60 s | 22 s |
| B (3× 90s each) | 270 s | 102 s |
| C (90s) | 90 s | 34 s |
| **Total** | **420 s simulated** | **160 s wall** |

---

## Verdict

This is the §6.5 failure mode that CONCEPT.md was honest about — but a *cleanly informative* one. The substrate cannot currently test the §6.3 hypothesis not because the physics is wrong, but because four required mechanisms (R1-R4) are absent. The experiment establishes the minimum missing rules with precision.
