# BET-105 — Bridge-Graph Write (parallel sweep)

Pre-registered: 2026-05-31 (BEFORE any run). The architectural resolution from
BET-104: the omnidirectional broadcast write is the bottleneck (floods high,
percolates low), while the compartment wall helps containment. Replace the
broadcast write with a NON-broadcast write that travels along the bridge graph.

## Mechanism

`apply_bridge_charge_propagation` (world/bridges.py): a firing atom deposits
charge directly into its bridged neighbours = `bridge_charge_prop_rate ×
bridge_strength`. No emitted vibrations (n_emit≈0). Co-activation travels only
along connectivity, so it cannot flood; the compartment wall (cutting
cross-boundary bridges) contains it WITHOUT starving within-compartment
propagation. Strength feeds back (strong bridge ⇒ stronger propagation ⇒ recall
self-sustains).

Required regime detail: propagation delivers charge to neighbour B the tick
AFTER A fires, so the correlation window must span ≥2 ticks. `tau_LTP = 1.0 s`
(≈2 × dt) so propagation-driven sequential firing registers as co-active. The
initial firing is seeded by the stim vibrations; the cascade then runs along
bridges within the stim compartment; control (starved + walled) stays silent.

## Variants (parallel, pre-committed) — n_emit=0, tau_LTP=1.0

| Label | bridge gain | wall | role |
|-------|------------:|------|------|
| 105a | 4  | ON  | minimal (≈theta_fire bootstrap) |
| 105b | 6  | ON  | moderate |
| 105c | 8  | ON  | strong |
| 105d | 6  | OFF | control — cross-region bridges should LEAK |
| 105e | 6  | ON, n_emit=1 | moderate + tiny broadcast assist |

Box 30, correlation plasticity + persistence + neuron_dynamics as BET-099, but
the WRITE is bridge propagation, not emission. Shortened phases for concurrency.

## Acceptance bars (locked pre-run — fraction-selective metric, verbatim)

| ID | Criterion | Bar |
|----|-----------|-----|
| Ta | Selective firing (gate) | stim firings >= 3× control during STIM |
| Tb | Selective potentiation | fraction of STIM checkpoints selective >= 0.5 |
| Tc | Persistent recall | fraction of POST checkpoints (>= stim_end+2000 s) selective >= 0.5 |
| Td | Containment | uniform-arm POST fraction-selective < 0.25 |

A variant PASSES if Ta–Tc AND Td. PASS (any wall-ON variant, with 105d leaking)
= clean selective persistent memory via a modular bridge-graph write — the
milestone the whole programme pointed to, and validation that decoupling the
write from broadcast is the resolution. All outcomes reported honestly.

## RESULT (2026-05-31): all 5 NULL — the bridge-write self-ignites whole compartments

| Variant | gain | wall | fire ratio | stim-frac | post-frac | verdict |
|---------|-----:|------|-----------:|----------:|----------:|---------|
| 105a | 4 | ON  | 1.8 | 0.00 | 0.00 | NULL |
| 105b | 6 | ON  | 1.8 | 0.00 | 0.00 | NULL |
| 105c | 8 | ON  | 1.8 | 0.00 | 0.00 | NULL |
| 105d | 6 | OFF | 1.7 | 0.00 | 0.00 | NULL |
| 105e | 6 | ON, n_emit1 | 1.3 | 0.00 | 0.00 | NULL |

### Diagnosis — self-ignition, not selectivity

Fire ratio ~1.8 (vs 3–6 selective baseline): control fires nearly as much as
stim, in EVERY variant including wall-ON. Cause: with `gain ≥ theta_fire` (4),
one firing atom deposits `gain × strength ≥ 4` into a bridged neighbour, which
fires, which propagates onward — the bridge-write is SELF-SUSTAINING. A single
spark ignites the whole compartment; the firing then loops indefinitely along
the bridge graph. Control only needs one spark — and it has one: leftover atom
CHARGE from warmup is not cleared at the stim-transition blank (blank_bridges
resets bridge strength, not k_charge). So control self-ignites and stays lit; the
wall cannot help because control ignites INTERNALLY, not by cross-boundary leak.

This is a real property of the bridge-write: it is a bistable per-compartment
switch (any spark → whole compartment ON), not a graded stimulus-selective write.

### Two fixes for BET-106

1. **Zero atom charge at the blank** so control starts truly silent (no spark).
2. Then re-test the gain sweep: with control un-sparked, STIM ignites only the
   stim compartment and self-sustains there (good = recall), while control stays
   dark. If that yields selectivity, the bridge-write + charge-blank + wall is the
   answer. If control still lights (e.g. cross-wall propagation or noise sparks),
   gain must sit below self-ignition (gain × low-well < theta_fire) while still
   reinforcing stim — a narrower design.

### Pattern note

This is a THIRD face of the recurring coupling: the write signal strong enough to
propagate is strong enough to self-sustain everywhere. Pattern 02's lesson
(reshape, don't just scale) applies — the next lever is the charge-blank (remove
spurious sparks) and possibly sub-ignition gain with stimulus reinforcement.
