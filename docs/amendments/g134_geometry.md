# G134 — Does the physical substrate EARN its place on GEOMETRY? (proximity detection)

## Motivation
G133: the physics is decorative/noise for algebra. Its native strength is SPATIAL structure. G134 tests
the geometric niche directly: a proximity-detection task (is any pair of K points within distance d?) — a
NONLINEAR SPATIAL threshold that raw+linear cannot fit. If the substrate's binding/proximity physics gives
features that beat raw+linear (and match the ELM), the physics computes the spatial relation natively and
EARNS its place for geometry.

## Pre-registration (locked BEFORE run)
N=120 samples; KP=5 point positions in [6,24]; target = 1 if min pairwise distance < d=1.6. Features:
raw sorted positions + linear; abstract ELM tanh(R·sorted); PHYSICAL (inject points, 25 ticks, vib+atom
16-bin histograms). Held-out 70/30 balanced accuracy. Both seeds.

**Bars (locked):**
- G134 PASS: PHYSICAL balanced-acc >= raw+linear + 0.10 on both seeds (physics earns its place on geometry).
- NULL: physical does not beat raw+linear → substrate doesn't help even here.

## Result
_(pending run)_
