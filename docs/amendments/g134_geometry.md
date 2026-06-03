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

## Result (balanced task: threshold = median min-distance, 50/50)
| seed | raw+linear | abstract ELM | PHYSICAL |
|------|-----------|--------------|----------|
| 42   | 0.57      | 0.71         | 0.61     |
| 7    | 0.67      | 0.75         | 0.54     |

**VERDICT: NULL** — physical does not beat raw+linear by the bar; inconsistent (helps seed 42 +0.04,
HURTS seed 7 −0.13), and the trivial ELM wins both.

(The first run was invalid — degenerate task, 112/120 positive; fixed to an adaptive median threshold.)

## Finding — even on geometry, the physics does not earn a computational place (but it's LEAST useless here)
On the proximity task the physical features are slightly POSITIVE on one seed (0.61 vs 0.57) — a real
contrast with algebra (G133, R2 = −0.49, pure noise) — so the spatial physics does encode a faint
proximity signal. But it is inconsistent (negative on the other seed) and a trivial random-feature ELM
beats it on both. So the substrate does NOT earn its place as a computational feature provider even on its
most natural niche.

## Honest bottom line across G133–G134
There is NO task tested where the physical substrate beats trivial baselines: it is NOISE for algebra,
weak-and-inconsistent for geometry, and (this is a slow Python sim) it makes nothing FASTER. The
substrate's only demonstrated genuine capability remains MEMORY/IO (matter-position). As a computational
component for AI it has no advantage in this simulation; its value is conceptual (a model of physical
spatial/analog computation), realizable as a speed advantage only in HARDWARE, not here. A "mix where the
substrate works better/faster" was looked for honestly and not found in this sim.
