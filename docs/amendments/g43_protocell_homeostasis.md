# G43 — Proto-cell homeostasis: a selective membrane maintains an interior–exterior gradient

Pre-registered: 2026-06-02 (BEFORE the run). PIVOT to the structural frontier (the substrate's
robust-positive territory). G30 built a large closed emergent membrane; G32 made it selectively
permeable in the engine (atom-proximity reflector, incompatible species reflected). The
defining function of a CELL is homeostasis: the membrane maintains an interior environment
chemically DISTINCT from the exterior. This BET tests whether the G30+G32 system sustains an
interior–exterior gradient under continuous ambient pressure — and whether it collapses
without the channel (proving the membrane maintains it).

## Method
G30 rich substrate (broad band; membrane machinery) → ~110-atom closed shell forms (centre C,
radius R from the largest bridged component). Then run with continuous ambient regeneration
(lambda_gen > 0) so foreign vibrations keep arriving from everywhere. Classify each free
vibration as COMPATIBLE / INCOMPATIBLE with the membrane's characteristic frequency f_mem
(substrate binding band). Measure, over the last third of the run, the INCOMPATIBLE
concentration (count / volume) interior (r < 0.6R) vs exterior. Two arms:
- **channel ON** (membrane_channel_mode='atom'): incompatible reflected at the real shell.
- **channel OFF**: membrane present but transparent (control).
Seeds 42 & 7.

## Bars (locked pre-run)
| ID | Criterion | Bar |
|----|-----------|-----|
| G43a | Membrane forms | largest bridged component ≥ 50 atoms (both seeds) |
| G43b | Gradient established (channel ON) | interior incompatible concentration ≤ 0.5 × exterior (mean over last third) |
| G43c | Sustained (channel ON) | the gradient (ratio ≤ 0.6) holds in ≥ 80% of the last-third checkpoints |
| G43d | Channel-dependent (control fails) | channel OFF: interior/exterior incompatible ratio ≥ 0.8 (equilibrated — no gradient) |

PASS = G43a–d → the selective membrane maintains a sustained interior environment depleted of
foreign species, collapsing without the channel: a proto-cell homeostasis demonstration built
only from substrate primitives + the engineered selective channel. A genuine bottom-up
structural milestone (membrane + maintained interior environment = cell precursor with
function). NULL: if G43b fails the channel cannot hold a steady-state gradient under continuous
pressure (one-shot selectivity ≠ homeostasis); if G43d also shows a gradient, the geometry
alone traps species (not the channel). Honest either way. No post-hoc threshold tuning.

## RESULT (2026-06-02): PASS — all four bars, both seeds

| seed | component | channel ON: interior/exterior incompat ratio | sustained (frac ≤0.6) | channel OFF ratio |
|------|-----------|-----------------------------------------------|------------------------|-------------------|
| 42 | 112 atoms | **0.00** | 1.00 | 1.05 |
| 7 | 110 atoms | **0.00** | 1.00 | 0.95 |

G43a–d all ✓ → **PASS.** With the selective channel ON, the emergent ~110-atom membrane keeps
its interior **completely depleted of foreign (incompatible) species** (concentration ratio
0.00) and holds that gradient across 100% of the steady-state window, under continuous ambient
regeneration. With the channel OFF, the same membrane equilibrates (ratio ≈ 1.0 — foreign
freely inside). The gradient is unambiguously the channel's doing, not geometry.

**This is proto-cell homeostasis:** a closed, spontaneously-formed membrane maintaining an
interior environment chemically DISTINCT from the exterior, sustained against continuous
pressure — membrane (structure) + selective permeability (function) = a cell precursor that
not only encloses but REGULATES its interior. Built only from substrate primitives + the
engineered §4.8 selective channel. No LLM, no transformer.

**Honest scope.** Robust on both seeds with a decisive margin (0.00 vs ~1.0), unlike the
single-seed G37 fluke. It is a steady-state EXCLUSION gradient (interior kept clear of foreign
species), the cleanest homeostasis the channel directly supports; it does not yet show active
interior CHEMISTRY (distinct molecular species forming inside) — that is the next structural
step (G44): does a distinct interior chemistry assemble within the protected environment?
The chain: rich substrate (G27) → large closed membrane (G30) → selective permeability (G32)
→ maintained interior environment (G43). The structural frontier is delivering.
