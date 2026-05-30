# BET-085 — Membrane Closure into a Shell (Cell Precursor)

Pre-registered: 2026-05-30, before any run.

## Hypothesis

A growing 2D membrane sheet (valence 3, atom repulsion + bridge
tension) will curve and close into a 3D shell when enough atoms
accumulate. Edge atoms (degree < 3, free valence) bridge to other
edge atoms on contact, curling the sheet. A closed shell encloses
volume — the cell precursor with a defined inside and outside.

## Configuration

  300 vibs, 30^3 box, valence 3, node_freq_binding=False,
  atom_repulsion_k=1.0, resonance_coupling=15, lambda_gen=0.015,
  longer decay (pair 30s, triad 300s), thermal_speed 3.0

## Acceptance bars (pre-registered)

| ID | Criterion | Bar |
|----|-----------|-----|
| T85a | Sheet grows | largest connected component >= 20 atoms |
| T85b | 2D structure | avg bridge degree of largest component >= 2.5 |
| T85c | Closure | sv_ratio (sv2/sv0) of largest component > 0.5 (3D shell, not flat) |
| T85d | Encloses volume | >= 1 vibration trapped inside the shell for >= 10s |
| T85e | Negative control | valence 2 does NOT produce sv_ratio > 0.5 (stays 1D) |

## Time budget

Realistic: 10 min wall. Ceiling: 30 min.

## RESULT (2026-05-30): T85c FAIL

Edge-closure attraction (edge_closure_k) made closure WORSE: sv_ratio
dropped from 0.43 to 0.00 (perfectly flat). The in-plane edge force
flattens the sheet rather than curling it. Largest component stayed
at 7-11 atoms — too small to close (need ~12+ for a shell).

Finding: isotropic forces (repulsion + edge attraction) produce flat
minimal surfaces, not closed shells. Closure requires ANISOTROPIC
curvature — a preferred bond angle that forces out-of-plane bending,
the way pentagons among hexagons curve a fullerene.

T85a partial (11 atoms, bar was 20). T85b PASS (degree 2.6 >= 2.5).
T85c FAIL. T85d/e not reached.

Next hypothesis (BET-086): intrinsic curvature via preferred bridge
angle < 180°. Accumulated bending closes the sheet into a shell.

## Not claimed

- Not a biological membrane (no lipid bilayer, no selective permeability)
- Not a living cell (no metabolism, no replication)
- A closed topological shell of bridged atoms enclosing a region
