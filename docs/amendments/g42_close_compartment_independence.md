# G42 — Close compartments: does the seal give independence where geometry cannot?

Pre-registered: 2026-06-02 (BEFORE the run). G41 showed the two-way seal works
mechanically but a 15-unit separation already isolates 5.7× by distance, so the result was
ambiguous. G42 puts the compartments CLOSE (centres 6 apart, radius 2.5 — surfaces ~1 unit
apart) where emissions readily cross, and uses a proper INDEPENDENCE metric: a compartment
is independent if its firing is unchanged by the OTHER compartment's stimulus, relative to a
no-stimulus baseline. Seal vs no-wall isolates the seal's true contribution.

## Method
BET-099 substrate, compartments A (x=12) and B (x=18), radius 2.5. Six arms = {stim-A,
stim-B, stim-none} × {seal, no-wall}. Tally firing per core (|x−cx|<2.5) during STIM.

## Bars (locked pre-run)
| ID | Criterion | Bar |
|----|-----------|-----|
| G42a | Own stimulus activates a compartment | seal: A_fire(stim-A) ≥ 5× A_fire(stim-none) AND B_fire(stim-B) ≥ 5× B_fire(stim-none) |
| G42b | Seal gives independence | seal: B_fire(stim-A) ≤ 1.5× B_fire(stim-none) AND A_fire(stim-B) ≤ 1.5× A_fire(stim-none) |
| G42c | Seal is necessary (no-wall cross-talks) | no-wall: B_fire(stim-A) ≥ 2× B_fire(stim-none) OR A_fire(stim-B) ≥ 2× A_fire(stim-none) |

PASS = G42a–c → at close range the sealed compartments are modularly INDEPENDENT (each
driven only by its own input) while no-wall compartments cross-talk: the engineered seal
provides isolation that geometry does not. A clean positive CONCEPT §4.8 modular-port
building block. NULL: if G42b fails the seal does not block close-range cross-talk (route is
not free-vibration transit — likely bridge percolation between near compartments); if G42c
passes-as-no-crosstalk even without walls, close compartments are already independent (seal
unnecessary). Honest either way; this CLOSES the modular-port thread. No post-hoc tuning.

## RESULT (2026-06-02): NULL — the vibration-seal does NOT isolate close compartments

| arm | stim-A → (A, B) | stim-B → (A, B) | stim-none → (A, B) |
|-----|------------------|------------------|---------------------|
| seal | (113, 12) | (9, 132) | (0, 0) |
| no-wall | (111, 11) | (9, 139) | (0, 0) |

G42a ✓ (own stim activates, 113/132 vs 0), G42b ✗ (seal stim-A → B=12, not ≤ 0), G42c ✓
(no-wall cross-talks). **Verdict: NULL — and decisive.**

1. **No intrinsic baseline:** stim-none → 0 firing in both arms. (Corrects the G41 guess
   that residual firing was intrinsic; at this scale it is purely stimulus-driven.)
2. **The seal makes ZERO difference at close range:** seal B=12 vs no-wall B=11; seal A=9
   vs no-wall A=9. The vibration-reflecting seal does not block close-range cross-talk.
3. **Therefore close-range cross-talk is NOT free-vibration transit.** At 6-unit centres
   (surfaces ~1 apart) the coupling is the neuron CHARGE-integration field (`r_integrate=5`
   reaches straight across the gap) and/or BRIDGE percolation — neither of which the seal
   touches. The vibration-seal isolates only at long range (G41), where distance already
   isolates and the seal is redundant. It is the wrong tool for close-range modularity.

## Unified finding (memory thread + modularity thread converge)
Both major threads this session hit the SAME wall: the substrate is **multiply-connected** —
free-vibration field, neuron charge-integration field (r_integrate), AND the bridge graph
each carry signal. Gating ONE channel (the vibration seal) cannot isolate a region because
the OTHER channels still couple it. (Memory: emissions both wrote and contaminated via the
vibration channel; modularity: close compartments couple via charge/bridges the seal ignores.)

**Next (G43) — the real deadlock-breaker test:** a TRUE engineered port that gates ALL
cross-boundary channels at once — vibration seal + no cross-boundary bridge formation + no
cross-boundary charge integration. If full multi-channel gating isolates close compartments
(seal-arm cross-talk → 0 while no-wall cross-talks), the §4.8 port is real and the deadlock's
mechanism (multi-channel connectivity) is confirmed by breaking it. This CLOSES the thread
either way.
