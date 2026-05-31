# G27 — Balanced binding regime: the full chain climbs robustly (8% bottleneck removed)

Pre-registered: 2026-05-31 (BEFORE the run). Continuation of G26 (the narrow 8% window
is the structural bottleneck). Michael's directive: vary the % rules / limits until the
substrate works. Hypothesis: a moderately wide vibration-binding window (±2%) + atoms
binding by PROXIMITY (node_freq_binding off — the 8% rule is no longer required) + a bit
more intermediate lifetime lets the chain climb to abundant atoms AND molecules.

## Config (the "balanced" regime)
freq_ratio 0.08, freq_tolerance 0.02 (±2% vibration-binding window), node_freq_binding
= False (atoms bind atoms by proximity), pair_decay_time 12 s, triad_decay_time 80 s,
n_nodes_max 2500. Real physics engine, 160 ticks, seeds 42 & 7.

## Bars (locked pre-run)
| ID | Criterion | Bar |
|----|-----------|-----|
| G27a | Abundant atoms | ≥ 3× baseline atoms, both seeds |
| G27b | Molecule species | ≥ 5 distinct molecule levels, both seeds (CONCEPT Phase-2 proxy) |
| G27c | Abundant molecules | ≥ 20 molecules, both seeds |

## RESULT (2026-05-31): PASS

| regime | seed | peak atoms | peak molecules | species |
|--------|------|-----------|----------------|---------|
| baseline 8% | 42 | 22 | 31 | 7 |
| baseline 8% | 7 | 11 | 27 | 7 |
| **balanced** | 42 | **195** | **649** | 7 |
| **balanced** | 7 | **203** | **636** | 7 |

G27a ✓ (195/203 vs baseline mean 16.5 → ~12×), G27b ✓ (7 species), G27c ✓ → **PASS**.
The balanced regime produces ~12× the atoms and ~22× the molecules of the 8% baseline,
robustly across seeds. The structural starvation that bottlenecked every higher level
is removed by varying the binding rule + limits — exactly the directive.

## Honest scope
This is STRUCTURAL yield (the foundation: atoms + molecules), not yet the higher
functions. Removing the starvation is necessary, not sufficient. "species = 7" counts
distinct molecule LEVELS (5–11), a proxy for species. Next (G28): re-test the
DOWNSTREAM levels with this rich substrate — does membrane formation (BET-086) and the
memory/bridge chain, which were element-count-starved, now compose where they could not
before? That is the real test of whether "it works" propagates up the chain.
