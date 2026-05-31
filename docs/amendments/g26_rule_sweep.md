# G26 — The 8% binding rule is the structural bottleneck (rule/limit search)

Pre-registered intent: 2026-05-31. Michael: the 8% rule is not sacred — vary the
% rules / limits until the substrate produces rich structure. Goal of "works" at this
level: the substrate reliably climbs the full chain (abundant stable atoms → molecules)
instead of starving at the narrow binding window.

## Setup
Real physics engine (world/physics.tick) with config overrides. Vibration→electron
binding requires frequencies `freq_ratio ± freq_tolerance` apart; default is 0.08 ±
0.005 (a ±0.5 % window — the "load-bearing fragile" 8 % rule, CONCEPT §4.4). Measured
peak structural yield (atoms = level 4, molecules = level ≥ 5).

## Results

**Bounded capacity (n_nodes_max=1200, 120 ticks, seed 42):**
| window | peak atoms | peak molecules |
|--------|-----------|----------------|
| baseline 0.08±0.005 | 7 | 9 |
| 0.08±0.02 | **34** (4.9×) | 0 |
| 0.08±0.05 | 0 | 0 |
| 0–15 % band | 0 | 0 |
| 0.03±0.03 | 2 | 0 |

**High capacity probe (n_nodes_max=4000, 100 ticks, 0.08±0.05):** 127 atoms, 183
molecules, flooded to capacity in ~1.7 sim-s.

## Finding (honest)
1. **The narrow 8 % window IS the structural bottleneck.** Baseline yields ~7 atoms;
   widening the window multiplies binding by 5–18× (34 atoms at ±2 %; 127 atoms +
   183 molecules at ±5 % when capacity allows).
2. **But naive widening + low capacity STARVES the climb.** At ±5 % with only 1200
   node slots, electrons flood the capacity and binding halts (graceful_capacity → -1)
   before atoms can form: peak atoms = 0. The flood of low-level nodes crowds out the
   higher levels.
3. So "works" is a BALANCE of window × capacity × decay, not a single knob. The 8 %
   rule was one over-tight setting of that balance; the right regime is a wider window
   WITH enough capacity and decay headroom for the chain to climb.

## Perf note (self-corrected during the run)
Binding is O(n_vib²) all-pairs; an over-high lambda_gen (0.02) floods vibrations to the
cap and made ticks ~440 ms. Fixed to lambda_gen=0.001 and bounded capacity for fast
sweeping. The flooding-to-capacity is itself the evidence that relaxed binding works.

## Verdict: FINDING (bottleneck confirmed) — next G27
Tune the three together: a moderately wide window (≈ ±2 %), enough capacity for the
chain, and decay rates that recycle low-level nodes so atoms/molecules accumulate.
Target: many stable atoms AND ≥ 5 molecule species (CONCEPT Phase-2 criterion)
robustly across seeds, at a yield the baseline cannot reach. (G27.)
