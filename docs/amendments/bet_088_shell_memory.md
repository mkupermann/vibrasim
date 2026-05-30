# BET-088 — Stable Bridge-Strength Pattern on a Membrane Shell (Proto-Memory)

Pre-registered: 2026-05-30. Builds on BET-086 (stable cell) + BET-087
(conserved flux plasticity).

## Hypothesis

A membrane shell (BET-086) with conserved flux plasticity (BET-087)
on its bridges develops a stable, non-uniform bridge-strength pattern.
Bridges that consistently sit in higher-flux positions strengthen;
others weaken. The pattern stabilises (low change once settled) — the
shell holds a persistent internal state shaped by its flux history.
That persistent state is the substrate of memory.

## Mechanism

Form a shell (valence 3, curvature). Enable flux_plasticity_rate.
No external stimulus — the test is whether the shell's own structure
produces a stable, differentiated strength pattern from intrinsic
flux asymmetry.

## Acceptance bars

| ID | Criterion | Bar |
|----|-----------|-----|
| T88a | Differentiation | strength coefficient-of-variation (std/mean) across shell bridges >= 0.3 (not uniform) |
| T88b | Stability | strength vector autocorrelation between t and t+2000s >= 0.7 (pattern persists, not random churn) |
| T88c | Not saturated | no more than 20% of bridges at max strength (pattern is graded, not all-or-nothing) |
| T88d | Substrate-only | constraint_checker.py passes |

## Time budget

Realistic: 8 min wall. Ceiling: 20 min.

## RESULT (2026-05-30): NULL — and it names the missing mechanism

Stable shell (44 bridges, constant) but:
- T88a FAIL: cv = 0.03 (bridges uniform ~1.0, not differentiated)
- T88b FAIL: autocorr 0.1-0.4 (random churn, no stable pattern)
- T88c PASS trivially (nothing saturates)

Two reasons, both instructive:
1. **Symmetric flux**. Vibrations fill the box uniformly; the shell is
   symmetric; every bridge sees ~the same density. No asymmetry → the
   conserved rule pulls all strengths to the mean. No pattern to form.
2. **No hysteresis**. The conserved-redistribution rule constantly
   relaxes toward the instantaneous flux-proportional target. Strength
   TRACKS flux; it does not LATCH. When flux is symmetric/noisy, the
   target is uniform and strengths stay uniform.

**This stacks with BET-087 to name the missing mechanism for memory:**
plasticity that merely tracks flux is not memory. Memory requires
BISTABILITY — a bridge with two stable states (weak, strong). Flux
above a threshold flips weak→strong; the bridge STAYS strong until
strong depression flips it back. That hysteresis is how a synapse holds
LTP. Without it, strength is a mirror of present flux, not a record of
past flux.

**Next (BET-089): bistable bridges.** Strength has two attractors.
Then expose the shell to an ASYMMETRIC, recurring stimulus and test
whether the strengthened bridges latch and persist after the stimulus
stops — and whether a different stimulus produces a different latched
pattern (content-addressable memory).

## Not claimed

- Not memory recall (no read-out mechanism yet)
- Not content-addressable (different-input→different-pattern is BET-089)
- A persistent, differentiated internal state shaped by flux history
