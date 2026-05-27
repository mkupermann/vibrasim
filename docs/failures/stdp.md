# STDP (Spike-Timing-Dependent Plasticity) — What We Simplified

## The shell
Plan B (substrate STDP) and Phase A-C (Brian2 STDP): classic pair-based
STDP rule. Pre-before-post = potentiation, post-before-pre = depression.
Exponential traces with tau=20ms. Fixed learning rates.

## What a non-thin version requires
- **Triplet STDP** (Pfister & Gerstner 2006): real STDP depends on
  spike triplets, not pairs. Pair-based STDP cannot explain rate-
  dependence of plasticity. Our BET-081 FAIL (0 distinct clusters
  despite silhouette 0.90) might be a direct consequence of missing
  triplet interactions.
- **Dendritic computation**: STDP in biology depends on where on the
  dendrite the synapse sits. Proximal vs distal synapses have different
  plasticity rules. We treat all synapses identically.
- **Neuromodulation**: dopamine, acetylcholine, serotonin gate STDP
  in vivo. Without neuromodulation, STDP alone cannot solve credit
  assignment (confirmed: 3 sequential NULLs on R-STDP, BET-067/071/072).
- **Structural plasticity**: real synapses grow and retract. Our
  connectivity is fixed at initialization (connect(p=...)). New
  synapses never form, existing ones never disappear. Only weights
  change.

## What breaks if wrong
BET-081 series showed: STDP produces assemblies (silhouette 0.90) but
not multi-class selectivity (0 distinct clusters). This is exactly the
regime where pair-based STDP is known to fail — it finds one dominant
pattern and suppresses alternatives. Triplet STDP or neuromodulation
might fix this, but both violate the "substrate primitives only" rule
unless they emerge from the binding physics.

## When to revisit
If the substrate ever develops neuron-like structures from the binding
cascade (cells with membranes that fire), STDP should emerge from the
physics of those structures, not be imposed as a Brian2 equation.
The Brian2 work was a proof-of-concept, not the final architecture.
