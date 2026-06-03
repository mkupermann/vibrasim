# G135 — Is the substrate a PHYSICAL OPTIMIZER for geometry? (relax cluster -> even spacing)

## Motivation
G133/G134: the substrate is a poor FEATURE provider. But its strongest possible role is a PHYSICAL
OPTIMIZER — atoms repel, so a clustered group should relax (energy-minimize) toward EVEN SPACING, the
analog-computer niche (force-directed layout / packing). G135 tests whether the dynamics actually solve
this spatial layout: inject KA atoms clustered at one point, run, and measure whether they spread and
reach low normalized gap-variance (even spacing).

## Pre-registration (locked BEFORE run)
Clear atoms; inject KA=6 tight clusters at x=15 (clustered start); record initial sorted atom xs and
normalized gap-variance; run T=200 ticks; re-measure. Both seeds.

**Bars (locked):**
- G135 PASS: spread grows by > 3 units AND final normalized gap-variance < 0.5 on both seeds (the physics
  relaxes the cluster toward an even-spacing min-energy layout — a genuine spatial computation).
- NULL otherwise.

## Result (existing settled atoms clustered at x=15, then relaxed)
| seed | atoms n0→n1 | gap-var → | spread → |
|------|-------------|-----------|----------|
| 42   | 6 → 3       | 0.0 → 0.05 | 2.0 → **0.5** (collapsed; 3 atoms died) |
| 7    | 6 → 6       | 0.0 → 0.04 | 2.0 → 2.8 (+0.8, < +3 bar) |

**VERDICT: NULL** — the dynamics do NOT relax the cluster to an even-spacing optimum. Seed 42 the atoms
COLLAPSED tighter (and some died); seed 7 barely spread (+0.8). (The low gap-variance is misleading — it
reflects atoms still tightly clustered, not an even spread.)

## Finding — the substrate is not a usable physical optimizer either
Even on the analog-computer's home turf (energy-minimizing layout via repulsion), the substrate fails:
atoms cluster/collapse rather than relaxing to even spacing. Binding/cohesion dominates over repulsion,
so the dynamics don't perform the spatial optimization. (The first attempt was a setup failure — fresh
injections didn't form level-4 atoms; this corrected run clusters EXISTING atoms.)

## Complete honest answer: the substrate has NO computational advantage in this sim (G133–G135)
- Feature provider, algebra (G133): NOISE (negative R2).
- Feature provider, geometry (G134): weak + inconsistent; trivial ELM wins.
- Physical optimizer, layout (G135): NULL; atoms collapse, no relaxation.
Across every niche tested — the substrate does not beat trivial baselines, and "faster" is impossible in a
serial Python sim. Its one genuine computational role is MEMORY/IO (matter-position). The analog-compute
advantage is a HARDWARE claim, not demonstrable in simulation. This is the evidence-based ceiling.
