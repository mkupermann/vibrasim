# Kuramoto Resonance — What We Simplified

## The shell
Linear frequency pull: df/dt = (coupling/level) * (f_j - f_i) / max(f_i, f_j).
Applied every 10 ticks to all node pairs within r_2.

## What a non-thin version requires
- **Proper Kuramoto model**: the real model uses phase oscillators
  with dphi/dt = omega + K/N * sum(sin(phi_j - phi_i)). We skip phase
  entirely and operate on frequencies. Phase-locking is a richer
  phenomenon than frequency-matching — two oscillators can frequency-
  match without phase-locking, and vice versa.
- **Coupling topology**: real Kuramoto has a coupling matrix K_ij that
  depends on the medium. We use uniform coupling for all pairs within
  radius. No attenuation with distance.
- **Finite-time synchronization**: real synchronization has transient
  dynamics, chimera states, partial sync. Our linear pull always
  converges monotonically. No oscillation, no metastability.
- **Back-reaction**: when a node's frequency shifts, its binding
  eligibility changes mid-tick. We update frequencies but don't
  re-check binding — that happens next tick. Temporal resolution
  matters for fast dynamics.

## What breaks if wrong
The frequency synchronization could be producing artificially easy
binding. If real Kuramoto dynamics have metastable states where
frequencies approach but don't converge, our cascade would overestimate
binding rates. The atom formation at 10s could be a simulation artifact
that disappears with proper phase dynamics.

## When to revisit
When we need quantitative predictions (how many atoms per second, at
what density). Currently: qualitative result (atoms form with resonance,
don't form without) is sufficient. Quantitative accuracy requires
proper Kuramoto.
