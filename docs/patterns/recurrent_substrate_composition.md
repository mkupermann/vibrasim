# Pattern — Unbounded recursive composition from substrate dynamics

**Surfaced by:** BET-136 → 140 (the "dynamics, not static codes" line). **Status:**
validated substrate capability. **Provenance (honest):** the model class is an
RNN / reservoir cell + clean-up memory; this is NOT new mathematics. The value is the
substrate-native assembly, local-only single-step training (no backprop-through-time,
no transformer), and a precise account of what each piece does.

## When to reach for it
When a task needs ALGORITHMIC / unbounded composition — generalizing to inputs or
sequence LENGTHS never seen — which static composition (VSA bundle + readout)
provably cannot do (BET-133/135: 0.000; the additive operator is separable in its
slots). Use the substrate as a DYNAMICAL computer instead.

## The four pieces (each earned through a NULL)
1. **Recurrence / iteration.** Learn ONE update step and apply it over time. A static
   one-shot map (a,b)->result fails; iterating a learned step composes (BET-136:
   modular addition, recurrent 1.000 vs static 0.000).
2. **Nonlinear cell.** The step must be nonlinear (the substrate's tanh / random
   features). A LINEAR cell cannot represent non-separable steps like XOR
   (BET-137/138 = chance; Minsky-Papert). Random nonlinear features lift it.
3. **Sharp per-step readout.** Fit the step near-exactly (ridge least-squares = the
   online-local RLS fixed point). Per-step error COMPOUNDS over length (p^L), so a
   slow/loose fit caps length-generalization (BET-139: 0.70). A sharp margin removes
   the cap.
4. **In-loop attractor cleanup.** Snap the state to the nearest clean code each step
   (the substrate's content-addressable energy attractor). This makes the state
   drift-free, so the computation stays exact for arbitrary length.

Result (BET-140): parity at length 10–20, 50, 100 all = 1.000, trained on 4 single
steps only, local rule, no BPTT. Drift-free unbounded recursive composition.

## Caveats / open
- Demonstrated on small finite-state computations (parity, modular successor). Scaling
  the state space and learning the transition from NOISY / discovered structure
  (rather than the 4 clean steps) is open.
- Local credit assignment here is one-step (the transition is given as single-step
  supervision). Genuinely deep/temporal credit assignment without BPTT remains the
  hard problem (cf. e-prop, equilibrium propagation).
- The honest contribution is engineering + mapping, not novel mathematics.
