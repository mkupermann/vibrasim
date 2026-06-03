# G133 — Is the PHYSICAL substrate a real reservoir, or decorative? (the crux of "substrate + theories")

## Motivation
world/reservoir.py's "SubstrateReservoir" is a plain numpy random matrix (tanh(Rx)) — a textbook ELM with
NO physics. So the cognition stack (BET-110→143) may owe nothing to the physical substrate (BET-143's own
note). G133 tests it decisively: build features from the REAL World physics (inject x, run ticks, read the
vibration/atom/charge histograms as phi_phys) and test held-out generalization on a NONLINEAR task
(pairwise products) vs the abstract ELM and a linear baseline.

## Pre-registration (locked BEFORE run)
N=90 random inputs x in [0,1]^6; target y = sum_i x_i*x_{i+1} (needs nonlinear features). Features:
linear (x), abstract ELM (tanh(Rx), R random), PHYSICAL (inject x into the World, 20 ticks, 3x10-bin
vib/atom/charge histograms). Ridge readout, held-out 70/30 R2. Both seeds.

**Bars (locked):**
- G133 PASS: PHYSICAL-substrate R2 > linear + 0.15 on both seeds (the physics provides usable nonlinear
  features -> the substrate genuinely contributes to cognition).
- NULL: physical R2 ~ linear -> the physics is decorative; the cognition is the abstract ELM alone.

## Result
| features | seed 42 R2 | seed 7 R2 |
|----------|------------|-----------|
| linear (raw x)        | 0.90 | 0.92 |
| abstract ELM tanh(Rx) | 0.94 | 0.92 |
| PHYSICAL substrate    | **-0.49** | **-0.40** |

**VERDICT: NULL** (both seeds) — physical features are WORSE than the mean (negative R2); the cognition
power is the abstract ELM, not the physics.

## Finding — for ALGEBRA the physical substrate is NOISE, not just decorative
On a nonlinear algebraic task the physics gave R2 < 0 (worse than predicting the mean) while the abstract
ELM matrix worked. The EQMOD-2 cognition stack's capability is classical ELM/VSA/RLS; the physical
substrate contributes nothing to it — BET-143's worry, now measured. (Caveat: the product task on
uniform[0,1] is largely linear, so the ELM only marginally beat linear; but the physical NEGATIVE R2 is
the clear, robust result.) This is the pivot to the geometric niche — G134 asks whether the physics earns
its place on a SPATIAL/proximity task where raw+linear fails.
