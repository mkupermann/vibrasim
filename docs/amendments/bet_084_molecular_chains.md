# BET-084 — Molecular Chain Formation

Pre-registered: 2026-05-27, before any run.

## Hypothesis

Enabling molecule+molecule fusion and raising the level ceiling allows
spontaneous formation of molecular chains (level 15+) from the
substrate's own binding physics. No external force — only the existing
8% frequency rule, spatial proximity, polarity matching, and decade
isolation.

## Changes from baseline

1. `mol_fusion_enabled = True`
2. Level ceiling raised from 12 to 32
3. Generalized upgrade table: any (level_a, level_b) where both >= 4
   produces level = max(a,b) + 1 (capped at 32)
4. LEVEL_TO_VIBRATIONS extended dynamically
5. n_nodes_max raised to 4096 (more room for complex structures)
6. Dense world: box_size 30x30x30, 2000 vibrations (8x density)

## Acceptance bars (pre-registered)

| ID | Criterion | Bar |
|----|-----------|-----|
| T84a | Atoms form | >= 10 atoms (level 4) in 60s |
| T84b | Molecules form | >= 5 molecules (level >= 5) in 120s |
| T84c | Chains form | >= 1 structure at level >= 8 in 300s |
| T84d | Growth continues | max level at 300s > max level at 120s |
| T84e | No runaway | total alive nodes < n_nodes_max * 0.9 at all times |

## Time budget

Realistic: 30 min. Ceiling: 2h.

## What this does NOT do

- No neuron dynamics (neuron_dynamics_enabled = False)
- No STDP, no Brian2
- No external input — substrate seeds once, evolves autonomously
- No membrane detection (that's BET-085+)
