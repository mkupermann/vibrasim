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

## Result
_(pending run)_
