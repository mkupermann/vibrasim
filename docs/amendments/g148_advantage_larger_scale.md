# G148 — Does the emerging annealing gap CROSS threshold at larger scale? (settles G147)

Pre-registered: 2026-06-05 (BEFORE the run). G147 found a real, monotonically-growing gap between annealing
(OSC/SA) and a strong CORRECT multi-restart greedy on frustrated MAX-CUT (mean gap 0.000→0.002→0.004→0.013
for n=30→150; annealing wins 0/6→2/6→5/6→6/6), but it stayed under the pre-registered 0.02 bar at n=150
(verdict: EMERGING). G148 scales up to settle whether the gap crosses threshold (advantage restored against
a correct baseline) or plateaus (the trend was a ceiling artifact).

## Method
Identical to G147 (spin-glass MAX-CUT, signed Gaussian; OSC best-of-5; proper SA 4×1000 sweeps incremental
field; GRD sign-correct greedy 60 restarts; REF = best + long SA). Scaled: `n ∈ {200, 280, 360}`, 5 instances
per n (`rng_seed=2` stream). **Classification ordering bug from G147 fixed** (monotone branch evaluated
correctly). Budgets reported in output.

## Bars (locked pre-run — carried verbatim from the G147 pre-registration of G148)
- **ADVANTAGE** (G145 claim RESTORED on hard instances vs a correct baseline): mean gap ≥ 0.02 at the largest
  n AND annealing beats GRD on ≥ 4/5 instances there.
- **NO_ADVANTAGE** (retract): the gap plateaus/shrinks below 0.01 at the largest n (the n=150 trend was a
  ceiling artifact).
- **EMERGING-still** (inconclusive): the gap keeps growing but stays in (0.01, 0.02) at the largest n →
  pre-register a still-larger rerun.

## Verdicts
- **PASS / ADVANTAGE** → annealing genuinely out-solves a strong correct greedy once frustrated instances are
  large enough. The programme's lone positive claim is restored — honestly, against the proper baseline, on
  genuinely hard instances. The real, buildable niche: annealing for hard combinatorial optimization.
- **NULL / NO_ADVANTAGE** → the gap was a ceiling artifact; correct greedy matches annealing even at n=360.
  Final honest retraction.
- **EMERGING-still** → the separation is real and growing but slow; report and pre-register larger n.

No post-hoc tuning; greedy stays at 60 restarts (strong, biasing against a spurious advantage).

## RESULT (2026-06-05): the advantage is CLASSICAL SA's — the oscillator (physical) machine has NONE

Pre-registered bar (`anneal = max(OSC,SA)` vs greedy): gap +0.020 / +0.020 / +0.023 at n=200/280/360,
anneal wins 4/5, 5/5, 5/5 → **technically ADVANTAGE.** But a bar on `max(OSC,SA)` conflates the physical
oscillator machine with the classical SA algorithm. Separating them (the whole point of "vibrations
computing") REVERSES the reading:

| n | SA vs greedy (wins, mean gap) | **OSC vs greedy (wins, mean gap)** | SA vs OSC |
|---|-------------------------------|------------------------------------|-----------|
| 200 | 4/5, **+0.020** | **2/5, −0.000** | 5/5 |
| 280 | 5/5, **+0.020** | **1/5, −0.008** | 5/5 |
| 360 | 5/5, **+0.023** | **3/5, +0.001** | 5/5 |

- **Classical simulated annealing** beats strong correct multi-restart greedy **14/15 instances** across all
  scales (~2% better cuts). This is the textbook result: annealing escapes the local minima that trap local
  search on hard frustrated landscapes. Real, established — and a property of the *algorithm*.
- **The oscillator-Ising machine (the project's actual physical subject) has NO advantage.** It TIES correct
  greedy (6/15 wins, mean gap ≈ 0.000) and is beaten by SA on **15/15** instances at every scale. It is a
  legitimate annealer but a *weak* one — no better than correct local search, strictly worse than SA.

**Honest verdict — REVERSES G145's headline upon rigorous scrutiny.** The pre-registered `max(OSC,SA)` bar
passes, but the honest, separated finding is the opposite of what the programme hoped: the genuine advantage
at scale belongs to **classical SA, an algorithm that needs no substrate at all**, while the physical
oscillator/"vibrations" realization confers **zero edge** over a correctly-implemented greedy. So:

- **What is real:** annealing-as-an-algorithm (SA) > local search on hard combinatorial optimization. (Known.)
- **What is NOT supported:** that the *physical/vibrations/oscillator* machine has any computational edge —
  it matches trivial correct greedy and loses to classical SA.

This is the clean close of the arc **G145 → G146 → G147 → G148**: G145's "the one place vibrations-computing
has a real edge" does **not** survive a correct baseline + the OSC/SA separation. The substrate's last
candidate advantage is, honestly, an advantage of a standard classical algorithm — not of the substrate.
Consistent with the programme-wide pattern: the physics is decorative; standard methods carry every win.

No further scale-up is warranted for the oscillator (its gap vs greedy is flat ≈ 0 across n=200–360, not
growing). The honest conclusion stands without more compute.
</content>
