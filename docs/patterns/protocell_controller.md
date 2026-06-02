# Pattern — Proto-cell as a first-order linear analog controller / low-pass filter

The proto-cell (emergent membrane G30 + selective channel G32) is a fully characterized FIRST-ORDER
LINEAR homeostatic controller — a substrate-level analog low-pass filter built only from physics
primitives + one engineered §4.8 channel. No LLM.

**The complete system-ID (all PASS, seeds 42 & 7):**
- **Qualitative regulation (G44):** restores interior set-point after a foreign-bolus perturbation.
- **Step response (G58):** interior clearance is first-order — time-constant τ≈75 ticks INDEPENDENT
  of perturbation magnitude (peak scales linearly with bolus; τ constant). Clearance rate ∝ load.
- **DC gain (G59):** under sustained influx, the steady-state interior offset is BOUNDED and scales
  LINEARLY with influx rate (ss = influx·τ). Disturbance rejection with a proportional offset.
- **Frequency response (G60):** the interior LOW-PASS filters a modulated disturbance — tracks slow
  (below ~1/τ), attenuates fast ~6.5× — confirming first-order dynamics.

**Mechanism.** The selective channel passively effluxes interior foreign species (outbound
unreflected, re-entry blocked, G44); efflux rate ∝ amount present → a leaky integrator = first-order
low-pass. The "controller" is passive selective transport, not active computation.

**Why it works where memory failed.** This uses the channel for selective EFFLUX/CONTAINMENT —
the substrate's genuine strength — not a selective WRITE (the mapped deadlock). It is a clean analog
DYNAMICAL element, not a memory.

**Where it applies.** Substrate-level analog signal conditioning: bounded regulation, disturbance
rejection, temporal low-pass filtering / leaky integration of a chemical signal. See
docs/amendments/g44, g58, g59, g60.

**Tunable cutoff (G61).** The time-constant scales with membrane radius: τ ∝ R (R up 1.5× → τ up
1.55×, both seeds), consistent with τ = interior_size / efflux_speed. So the low-pass cutoff (~1/τ)
is set by the emergent membrane size — a tunable analog filter with a clean design law.
