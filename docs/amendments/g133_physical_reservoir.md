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
_(pending run)_
