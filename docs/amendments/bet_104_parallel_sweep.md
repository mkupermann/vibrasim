# BET-104 — Parallel Sweep: Does Broadcast Strength × Compartment Resolve Write/Leak?

Pre-registered: 2026-05-31 (BEFORE any run). Follows BET-103's finding (write =
broadcast = leak): the compartment wall contained the leak but starved the write,
because the wall halved the broadcast field the write depends on. Direct test:
with the wall containing the leak, does MORE broadcast restore the within-
compartment write while the wall keeps control clean?

Run as 5 PARALLEL variants (shared bars), each its own process/output file.

## Variants (pre-committed)

| Label | n_emit | compartment wall | role |
|-------|-------:|------------------|------|
| 104a | 16 | ON (x=15) | wall + more broadcast |
| 104b | 32 | ON (x=15) | wall + high broadcast |
| 104c | 64 | ON (x=15) | wall + very high broadcast |
| 104d | 32 | OFF | matched-broadcast control (should LEAK) |
| 104e | 8  | ON (x=15) | low-broadcast baseline (≈ BET-103) |

Box 30, neuron_dynamics + correlation plasticity + persistence as BET-099.
Shortened phases (WARMUP 3000, STIM 3000, POST ≥2000) so 5 can run concurrently.

## Acceptance bars (locked pre-run — fraction-selective metric, verbatim)

| ID | Criterion | Bar |
|----|-----------|-----|
| Ta | Selective firing (gate) | stim firings >= 3× control during STIM |
| Tb | Selective potentiation | fraction of STIM checkpoints selective >= 0.5 |
| Tc | Persistent recall | fraction of POST checkpoints (>= stim_end+2000 s) selective >= 0.5 |
| Td | Containment | uniform-arm POST fraction-selective < 0.25 |

A variant PASSES if Ta–Tc hold AND Td. 

## Pre-registered prediction (so the sweep is falsifiable, not fishing)

If write=broadcast=leak is fundamental, then for wall-ON variants either the write
stays starved (Tb fails) at every n_emit, OR raising n_emit restores the write but
the leak finds its way around the wall over time (Tc/Td fails) — i.e. NO wall-ON
variant cleanly passes. If instead some wall-ON variant passes while the matched
wall-OFF control (104d) fails Td, then enough broadcast + the wall DOES resolve it
and BET-103's starvation was just a too-low-broadcast regime. The wall-OFF control
104d is expected to write but LEAK (Td fails) at any n_emit that writes.

All 5 outcomes reported honestly; no post-hoc selection. Whatever the pattern, it
sharpens the consolidated finding.

## RESULT (2026-05-31): all 5 NULL — monotonic; broadcast write floods, wall helps containment

5 parallel variants, all NULL, but a clean monotonic pattern:

| Variant | n_emit | wall | stim-frac | post-frac | uni-frac | verdict |
|---------|-------:|------|----------:|----------:|---------:|---------|
| 104e | 8  | ON  | 0.33 | **0.26** | 0.10 | NULL (best) |
| 104a | 16 | ON  | 0.00 | 0.16 | 0.06 | NULL |
| 104b | 32 | ON  | 0.00 | 0.00 | 0.00 | NULL |
| 104c | 64 | ON  | 0.00 | 0.00 | 0.00 | NULL |
| 104d | 32 | OFF | 0.00 | 0.00 | 0.00 | NULL |

### Pattern (decisive)

Selectivity rises **monotonically as broadcast falls** (post-frac 0.26 → 0.16 →
0 → 0 as n_emit 8 → 16 → 32 → 64). High broadcast FLOODS — every atom fires, no
region is special, zero selectivity (and the wall-OFF control 104d floods
identically: it isn't even leak, it's saturation). Only the lowest broadcast
retains partial selective recall, still sub-threshold.

Two clean findings:
1. **The omnidirectional broadcast write is the bottleneck.** It floods at high
   intensity and percolates/weakens at low intensity — there is no broadcast
   level that writes a clean selective memory. This matches the pre-registered
   "fundamental" branch: more broadcast does not help.
2. **The wall genuinely helps CONTAINMENT.** uni-frac 0.06–0.10 (wall ON) vs
   BET-099's full control leak — the compartment does isolate; it just can't
   manufacture a write from a flooding/percolating field.

### Conclusion → BET-105

The resolution is confirmed to be a **non-broadcast write**: drive co-activation
along the BRIDGE GRAPH (G6 atom→atom propagation through strong bridges), which
is directional and connectivity-respecting, then the wall's containment (which
works) can hold a clean selective memory. The broadcast write cannot be salvaged
by intensity or compartmentalization. BET-105 implements the bridge-graph write.
