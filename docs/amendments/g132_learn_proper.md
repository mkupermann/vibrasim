# G132 — Can substrate PRIMITIVES learn A->B? (charter-faithful, proper readout)

## Pre-registration (locked BEFORE run)
Re-run the R2 learnability rung correctly: enable the substrate's OWN learning machinery (STDP, BTSP,
correlation plasticity, bistable wells, charge/atom propagation — no bolted-on ML), train A->B pairing
N=80 times, then probe A alone and read the B-region BTSP ELIGIBILITY (k_eligibility, which accumulates
from firing — a real activity readout, fixing G131's dead probe). Compare to untrained and to a control
region C. Both seeds.

**Bars (locked):**
- G132 PASS (learned): trained A->B eligibility > 1.5x untrained AND > 1.5x control-region C, both seeds.
NULL otherwise → substrate primitives cannot form the association (charter-faithful evidence).

## Result
_(pending run)_
