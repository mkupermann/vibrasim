# New direction — computation in the substrate's DYNAMICS, not static codes

Chosen 2026-05-31 after the honest novelty reckoning (Michael: "Das ist doch nicht
neu"). BET-124→135 used only ESTABLISHED static methods (VSA, reservoir/ELM, RLS) —
fixed/shallow representation + a linear readout — and they provably hit a wall on
algorithmic (modular) composition (BET-135: 0.000 even with learnable codes; the
limit is the additive binding OPERATOR).

The substrate's ACTUAL distinguishing feature was never used as the computer: its
recurrent DYNAMICS in time (energy relaxation, iteration, BTSP eligibility traces).
Every static one-shot map (a,b)->result failed. But algorithmic functions are
naturally computed by ITERATION of a reusable step.

## The bet
Use the substrate as a DYNAMICAL computer: learn a single update operator by a LOCAL
one-step rule (no backprop-through-time), then ITERATE it. Test whether this
generalizes an algorithmic function to unseen inputs where static composition gives
~0.

Honest provenance (no overclaim): the model class is finite-state-machine / recurrent
computation; local recurrent learning has precedents (e-prop Bellec 2020, equilibrium
propagation Scellier 2017, RTRL). The contribution sought here is EMPIRICAL and
substrate-specific: does the substrate's recurrence break a wall its own static stack
cannot, using only local one-step learning + iteration? Sharply falsifiable; may NULL.

First probe: BET-136 (modular addition by iterated successor).
