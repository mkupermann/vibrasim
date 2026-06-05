# G146 — Does the oscillator-Ising machine compete with PROPER simulated annealing? (validates G145, the programme's lone positive claim)

Pre-registered: 2026-06-05 (BEFORE the run). G145 is the substrate programme's single genuine-advantage
result: oscillator-Ising **annealing** beats multi-restart greedy 8/8 on hard frustrated (spin-glass)
MAX-CUT, and is offered as "the one place vibrations-computing has a real edge." But G145 states its own
caveat: *"greedy is a WEAK baseline for frustrated problems; the proper peer is SIMULATED ANNEALING."*
Two reasons this needs validation before the claim is trusted:

1. **The proper peer is missing.** The oscillator machine essentially *is* a physical annealer; the honest
   question is whether it competes with the textbook annealer (SA), not whether it beats greedy.
2. **The greedy baseline returns NEGATIVE cuts** (−25 to −67) on a MAX-CUT instance. A correct local-search
   *maximizer* should never return a cut worse than a random assignment's expectation (≈0). G145's greedy
   flips when `gain = 2·s[i]·(W[i]@s) < 0`; this may be descending toward MIN-cut (a sign bug), which would
   make the "8/8 win" a win over a broken baseline. G146 audits this empirically (does not assume it).

## Method
Same 8 hard instances as G145 (n=30, signed Gaussian weights `W = triu(A,1)+ᵀ`, `rng_seed=2`). Solvers:
- **OSC** — oscillator-anneal, G145 code verbatim, best of 5 seeds.
- **SA** — Metropolis simulated annealing, geometric cooling T: 4.0→0.01, 5 restarts × 2000 sweeps, accept a
  flip iff `Δcut>0` or `rand < exp(Δcut/T)` with the sign-checked `Δcut = s_k·(W[k]@s)`.
- **GRD145** — G145's greedy verbatim (to reproduce the published number).
- **GRD** — sign-audited greedy (flip iff `Δcut>0`), 25 restarts (the corrected baseline).
- **REF** — best cut over all methods + one long SA (10k sweeps); proxy optimum for approximation ratios.

## Bars (locked pre-run, symmetric — either outcome is informative, no rigging)
| ID | Criterion | Threshold |
|----|-----------|-----------|
| G146a | Reproduce G145 | OSC beats GRD145 on ≥ 5/8 instances |
| G146b | Greedy audit (diagnostic) | report GRD145 vs GRD; flag "buggy" if mean(GRD145) < 0 ≤ mean(GRD) |
| G146c | **Oscillator vs proper SA (decisive)** | classify per below |
| G146d | Absolute quality | OSC and SA both reach ≥ 0.95·REF on average |

**G146c classification (pre-registered):**
- **COMPETITIVE** (claim ROBUST): OSC ≥ SA on ≥ 4/8 AND mean(OSC − SA) ≥ −0.02·|REF| → oscillator-Ising is a
  legitimate annealer competitive with textbook SA; G145's positive claim stands on solid ground.
- **SUBOPTIMAL** (claim TEMPERED): SA > OSC on ≥ 6/8 AND mean(SA − OSC) ≥ 0.02·|REF| → standard SA beats the
  oscillator machine; its "advantage" was beating a (possibly buggy) greedy, not genuine annealing
  superiority. The programme's lone positive result is a *weak* realization of a standard algorithm.
- **INCONCLUSIVE**: otherwise (mixed / within noise) — reported as such.

## Verdicts
- **PASS** = G146a holds AND G146c = COMPETITIVE AND G146d holds → G145's one genuine advantage is
  **validated against the proper peer**. The honest positive claim survives its strongest test.
- **TEMPERED/NULL** = G146c = SUBOPTIMAL → the programme's lone positive claim is significantly weakened
  (textbook SA dominates the physical machine). A major, honest correction to the final answer.
- **PARTIAL/INCONCLUSIVE** = otherwise → report the comparison as not decisive; propose a budget-matched rerun.

No post-hoc threshold tuning. If GRD145 is confirmed buggy, that is recorded as a correction to G145's
framing regardless of the OSC-vs-SA outcome (the "8/8 vs greedy" headline was then unfair).

## RESULT (2026-06-05): oscillator IS a legit annealer (= SA) — but G145's headline ADVANTAGE is REFUTED

| trial | OSC | SA | GRD145 | GRD (fixed) | REF | OSC−SA |
|-------|-----|----|--------|-------------|-----|--------|
| 0 | 48.2 | 48.9 | −52.2 | 48.9 | 48.9 | −0.7 |
| 1 | 29.0 | 29.4 | −67.0 | 29.4 | 29.4 | −0.4 |
| 2 | 50.0 | 50.2 | −39.6 | 50.2 | 50.2 | −0.2 |
| 3 | 63.3 | 63.3 | −31.7 | 63.3 | 63.3 | +0.0 |
| 4 | 56.7 | 56.8 | −43.7 | 56.8 | 56.8 | −0.1 |
| 5 | 65.7 | 65.7 | −25.0 | 65.7 | 65.7 | +0.0 |
| 6 | 66.4 | 66.4 | −25.3 | 66.4 | 66.4 | +0.0 |
| 7 | 62.1 | 62.1 | −34.6 | 62.1 | 62.1 | +0.0 |

- **G146a ✓** — OSC beats GRD145 8/8 (reproduces G145 exactly).
- **G146b — GRD145 is SIGN-BUGGY (confirmed).** Mean GRD145 = **−39.9** (negative cuts on a MAX-CUT
  problem); mean corrected GRD = **+55.3**. G145's greedy flipped on `gain<0`, descending toward MIN-cut.
  The "8/8 vs greedy" headline was a win over a baseline running the wrong direction.
- **G146c = COMPETITIVE** — OSC vs proper SA: OSC≥SA on 4/8, SA>OSC on 4/8, mean(OSC−SA) = **−0.18**
  (within eps=1.11). The oscillator-Ising machine is a *legitimate annealer*, tied with textbook SA.
- **G146d ✓** — OSC 0.996·REF, SA 1.000·REF. Both near-optimal.

**The decisive, unanticipated finding (from the greedy audit): these instances are NOT HARD.** Corrected
multi-restart greedy `GRD(fixed)` reaches **REF on all 8 trials** (it equals the reference optimum every
time). A trivial local search solves n=30 frustrated MAX-CUT optimally — so there is **no regime of
difficulty here for annealing to exploit**, and the oscillator's apparent "advantage" in G145 was entirely
an artifact of the buggy greedy. Against a *correct* local search the oscillator (and SA) merely **tie**.

**Verdict: PASS on the narrow pre-registered axis (G146a ✓, G146c=COMPETITIVE, G146d ✓ → oscillator is a
real annealer competitive with SA) — but the broader G145 claim of a GENUINE PHYSICAL ADVANTAGE is
REFUTED.** Honest net: the oscillator-Ising machine is a valid annealer, not a *superior* solver; on these
instances correct greedy already hits the optimum, so annealing buys nothing. G145's "the one place
vibrations-computing has a real edge" does not hold at this scale against a correctly-implemented baseline.

**The advantage claim is not dead, but unproven: it requires genuinely HARD instances** where correct
multi-restart greedy demonstrably gets trapped (a real gap to local search). Pre-registered **G147**: scale
up (larger n and/or higher frustration density) and find the regime — if any — where annealing (OSC/SA)
opens a real gap over corrected multi-restart greedy. If a gap opens → the genuine-advantage claim is
restored on properly-hard instances; if no gap ever opens up to large n → the claim is fully retracted.
</content>
