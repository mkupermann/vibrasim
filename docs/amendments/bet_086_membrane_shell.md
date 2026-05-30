# BET-086 — Closed Membrane Shell via Spontaneous Curvature (Cell Precursor)

Pre-registered: 2026-05-30, before run. Builds on BET-085 FAIL.

## Hypothesis

Spontaneous curvature (push each bridged atom away from its neighbour
centroid, Helfrich-style) curls a flat valence-3 sheet into a closed
3D shell. The shell encloses volume — inside distinct from outside,
the cell precursor.

## Configuration

  400 vibs, 28^3 box, valence 3, node_freq_binding=False,
  atom_repulsion_k=1.0, curvature_k=2.0, resonance_coupling=15,
  lambda_gen=0.012, pair_decay 40s, triad_decay 400s, thermal 2.0

## Acceptance bars

| ID | Criterion | Bar | Result |
|----|-----------|-----|--------|
| T86a | Shell size | component >= 15 atoms | PASS (18) |
| T86b | Triangulated | avg bridge degree >= 2.5 | PASS (3.0) |
| T86c | 3D closure | sv_ratio > 0.5 | PASS (0.6-0.75 sustained) |
| T86d | Encloses volume | >= 10 vibrations inside, persistent | PASS (33-105, 18000s) |
| T86e | Stability | shell persists >= 5000s sim | PASS (1000s-19000s+) |

## Result: PASS

A closed 18-atom triangulated shell (degree 3.0) formed at 1000s and
persisted to 19000s+ sim time. sv_ratio held 0.6-0.75 (genuine 3D
shell, not a flat disk). 33-105 vibrations were trapped inside the
enclosed volume at any time.

This is the cell precursor: a closed membrane of bridged atoms with
a defined interior and exterior. Spontaneous curvature (BET-086)
succeeded where edge-closure attraction (BET-085) failed — the
out-of-plane force domes the sheet, the in-plane force flattened it.

## Replication (2026-05-30): 5/5 seeds

Shells form across all tested seeds — not a lucky seed-42 configuration:

  seed 42:   size 19, sv_ratio 0.78, inside 64
  seed 7:    size 25, sv_ratio 0.66, inside 60
  seed 99:   size 30, sv_ratio 0.78, inside 69
  seed 123:  size 15, sv_ratio 0.86, inside 75
  seed 2024: size 34, sv_ratio 0.75, inside 52

All 5: closed 3D shell (sv_ratio > 0.5), >= 15 atoms, >= 50 vibrations
trapped inside. The cell precursor is a robust, reproducible
attractor of the substrate physics, not an artifact.

## Chain status

```
Waves → Electrons → Pairs → Triads → Atoms → Bridges →
Rings (val 2) → Sheets (val 3) → Closed Shell (curvature) = CELL
```

## Not claimed

- Not a lipid bilayer, no selective permeability (yet)
- Not metabolism, not replication
- A topologically closed shell of bridged atoms enclosing a region,
  with vibrations trapped inside

## Next (BET-087)

The shell exists but is passive. Toward learning: (a) two shells
connected by a bridge that passes vibrations = proto-synapse, or
(b) shell selectivity — interior vibrations behave differently from
exterior. Plasticity must emerge from bridge dynamics, not be imposed.
