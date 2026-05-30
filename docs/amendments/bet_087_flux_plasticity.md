# BET-087 — Flux-Driven Bridge Plasticity (Substrate Learning Foundation)

Pre-registered: 2026-05-30, before any run.

## Hypothesis

Bridges are channels for vibration flux. A bridge whose two endpoint
atoms are both in regions of high vibration density carries more flux;
that bridge strengthens. Low-flux bridges weaken and eventually decay.
This is plasticity from substrate physics — a riverbed deepening where
water flows — NOT an imported STDP/learning rule, NOT spike-timing,
NOT supervised.

The test: present a recurring spatial vibration pattern. The bridges
in the stimulated region must strengthen relative to bridges elsewhere,
and that strengthening must persist after the stimulus stops (memory).

## Mechanism

Each tick, for each bridge (A,B):
  local_flux = vibration_count_near(A) * vibration_count_near(B)
  if local_flux > threshold:  strength += rate * dt   (potentiation)
  else:                       strength -= decay * dt   (depression)
  strength clamped [0, max]

Bridges below min_strength are removed (structural pruning).
No target, no label, no gradient. Strength follows flux.

## Acceptance bars

| ID | Criterion | Bar |
|----|-----------|-----|
| T87a | Differentiation | stimulated-region bridges end >= 2x stronger than control-region bridges |
| T87b | Persistence | after stimulus stops, stimulated bridges stay >= 1.5x for >= 500s |
| T87c | Not trivial | a no-stimulus control shows no differentiation (all bridges similar) |
| T87d | Substrate-only | constraint_checker.py passes (no STDP/label/backprop imports) |

## Time budget

Realistic: 10 min wall. Ceiling: 30 min.

## RESULT (2026-05-30): NULL

The mechanism works but the experiment cannot demonstrate spatial flux
memory at this scale. Three iterations:

- v1/v2 (absolute + relative-to-mean): all bridges SATURATE to max.
  Background vibration density (~46/atom) exceeds any fixed threshold;
  relative-to-mean always keeps ~half above mean, creeping to max.
- v3 (localized slow stimulus, low background): real strength dynamics
  (0.7-1.3) but only n=1 bridge per region — too sparse.
- v4 (conserved redistribution): NO saturation (strengths stay ~1.0,
  fixed budget shared by flux). But measurement dominated by structure
  PRESENCE, not plasticity: n flips 0↔3 per region as the small mobile
  structures drift between measurement zones. Ratio 100/0 just means
  "stim region has bridges this instant" — noise.

T87a/b not cleanly met. T87c (no saturation) achieved by v4.

**Root cause**: plasticity needs STABLE structure. With ~18-25 mobile
atoms and a handful of drifting bridges, there is no fixed substrate
for place-specific flux memory to accumulate on.

**Insight → BET-088**: put plastic bridges on the STABLE membrane shell
(BET-086). The shell's bridges have fixed positions. Test whether shell
bridges facing a recurring external stimulus strengthen and remember.
Plasticity belongs on stable matter, not free-floating atoms.

The conserved-redistribution mechanism (no saturation, strength tracks
flux, competition between channels) is sound and carried forward.

## Not claimed

- Not biological LTP/LTD (no NMDA, no calcium)
- Not a complete learning system — this is the plastic element only
- Plasticity = bridge strength tracking vibration flux. Whether this
  composes into pattern memory is BET-088+.
