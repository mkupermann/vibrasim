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

## RESULT

_(to be filled after all variants complete — per-variant + pattern)_
