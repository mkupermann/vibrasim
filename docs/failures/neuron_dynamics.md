# Neuron Dynamics (PHASE4) — What We Simplified

## The shell
Integrate-and-fire on level-4 atoms: count nearby vibrations, accumulate
charge with exponential decay (tau=0.5s), fire when charge >= theta.
Firing emits n_emit vibrations. Refractory period t_ref=50ms.

## What a non-thin version requires
- **Ion channels**: real neurons have voltage-gated Na+/K+/Ca2+ channels
  with distinct activation/inactivation kinetics. Our "charge" is a
  single scalar with linear integration. No action potential shape, no
  after-hyperpolarization, no bursting modes.
- **Hodgkin-Huxley dynamics**: the simplest biophysically realistic
  model has 4 differential equations per neuron. We have 1 (charge
  decay). Even LIF (which Brian2 uses) is a simplification of HH.
  Our PHASE4 is a simplification of LIF.
- **Spatial structure**: real neurons have soma, axon, dendrites. Our
  atom is a point in 3D. There is no concept of "where on the neuron"
  a signal arrives.
- **Chemical synapses**: neurotransmitter release is stochastic,
  involves vesicle pools, receptor dynamics. Our "firing emits
  vibrations" is a broadcast, not a targeted chemical signal.

## What breaks if wrong
The simplified neuron dynamics might fire too easily or too rarely
compared to biophysical neurons, producing unrealistic activity
patterns. The emission mechanism (vibrations in all directions) has
no synaptic specificity — it's more like a shockwave than a signal.
This could prevent the formation of specific circuits even if the
substrate has the structural complexity for them.

## When to revisit
When we need circuits (specific neuron-to-neuron signal routing). The
current broadcast model works for "does anything fire at all" but
fails for "does neuron A selectively excite neuron B". That's the
cell → synapse step in the chain.
