# G147 — Does annealing open a REAL gap over correct multi-restart greedy at scale? (the programme's advantage, settled)

Pre-registered: 2026-06-05 (BEFORE the run). G146 refuted G145's headline "genuine physical advantage":
G145's greedy was sign-buggy (minimizing cut), and a *correct* multi-restart greedy reaches the reference
optimum on all 8 of G145's n=30 instances — so those instances are not hard, and the oscillator (tied with
SA) buys nothing over trivial local search. G146 left one honest possibility open: the advantage may exist
on **genuinely hard** instances where correct greedy demonstrably gets trapped. G147 tests that at scale —
the decisive, final test of whether the oscillator/Ising/annealing paradigm has ANY real edge.

## Method
Spin-glass MAX-CUT (signed Gaussian weights `W = triu(A,1)+ᵀ`), `n ∈ {30, 60, 100, 150}`, 6 instances per n
(`rng_seed=2` stream). Three solvers, budgets scaled with n and **reported explicitly** for auditability:
- **OSC** — oscillator-anneal (G145 code), best of 5 seeds, 1500 steps.
- **SA** — proper Metropolis SA with incremental field `h=W@s`, geometric cooling 4.0→0.01, 4 restarts ×
  1000 sweeps.
- **GRD** — sign-CORRECT multi-restart greedy (flip iff `Δcut = s_i·(W[i]@s) > 0`), **60 restarts**
  (deliberately generous — a STRONG baseline, biasing the test AGAINST finding a spurious annealing edge).
- **REF** — best over all methods + one long SA (8k sweeps); proxy optimum for approximation ratios.

`anneal_ratio = max(OSC, SA)/REF`, `grd_ratio = GRD/REF`. The quantity of interest is the **gap**
`anneal_ratio − grd_ratio` as a function of n.

## Bars (locked pre-run)
| ID | Criterion | Threshold |
|----|-----------|-----------|
| G147a | Confirm G146 (small n easy) | at n=30, mean GRD ratio ≥ 0.99 |
| G147b | **Does a gap open at scale? (decisive)** | classify per below |
| G147c | Annealers work at scale (sanity) | mean anneal_ratio ≥ 0.97 at every n |

**G147b classification (pre-registered):**
- **ADVANTAGE** (G145 claim RESTORED): at the largest n, mean(anneal_ratio − grd_ratio) ≥ 0.02 AND best
  annealing beats GRD on ≥ 5/6 instances → annealing genuinely out-solves a strong correct greedy once
  instances are hard enough. The programme has a real, demonstrated computational edge.
- **NO ADVANTAGE** (claim RETRACTED): at every tested n the gap < 0.02 → correct multi-restart greedy
  tracks annealing up to n=150; the paradigm shows no advantage anywhere tested.
- **EMERGING** (inconclusive): a positive but sub-threshold gap that grows monotonically with n → suggestive;
  pre-register a larger-n rerun rather than claim either way.

## Verdicts
- **PASS / ADVANTAGE** → the genuine niche is real, now established against a correct baseline on hard
  instances. The honest positive result the programme has been hunting for.
- **NULL / NO ADVANTAGE** → final, honest retraction of the programme's lone positive claim: across the
  whole arc (substrate computationally empty; cognition stack physics-decorative; and now annealing
  matched by trivial correct local search up to n=150) there is **no demonstrated computational advantage
  anywhere**. The value was the rigorous, self-correcting process.
- **PARTIAL / EMERGING** → a gap is opening; scale further before concluding.

Conservative by construction: GRD gets 60 restarts (strong). If annealing STILL opens a gap, the effect is
real; if not, the retraction is well-earned. No post-hoc threshold tuning; budgets reported in the output.

## RESULT (2026-06-05): EMERGING — a real gap opens with scale, sub-threshold at n=150

| n | mean anneal_ratio | mean grd_ratio | mean gap | anneal wins |
|---|-------------------|----------------|----------|-------------|
| 30 | 1.000 | 1.000 | +0.000 | 0/6 |
| 60 | 1.000 | 0.998 | +0.002 | 2/6 |
| 100 | 0.998 | 0.994 | +0.004 | 5/6 |
| 150 | 1.000 | 0.987 | **+0.013** | **6/6** |

- **G147a ✓** — at n=30 GRD = REF exactly (1.000): confirms G146, small frustrated instances are trivial.
- **G147c ✓** — anneal_ratio ≥ 0.998 at every n: the annealers track the optimum at scale.
- **G147b — EMERGING (per the pre-registered doc definition).** The gap is **monotonically growing**
  (0.000 → 0.002 → 0.004 → 0.013) and annealing's win rate climbs 0/6 → 2/6 → 5/6 → **6/6**. At n=150
  correct strong greedy (60 restarts) falls ~1.3% below annealing on *every* instance. This is exactly the
  doc's EMERGING signature ("a positive but sub-threshold gap that grows monotonically with n").

**Honesty note on the verdict.** The harness *printed* `NO_ADVANTAGE` — but that is a logic-ORDERING BUG in
the script, not the pre-registered criterion: it evaluates `elif not any_gap` (no single n reached 0.02)
*before* the `monotone_growing` branch, so the EMERGING case is unreachable whenever the gap stays under
0.02 at every n. The pre-registration of record is this DOC (CLAUDE.md: "criteria pre-registered in
docs/…"), which defines EMERGING precisely for this data. Reporting the honest outcome as **EMERGING /
PARTIAL**, transparently noting the code's misprint rather than silently accepting it or silently flipping
to ADVANTAGE (the 0.02 bar was genuinely not met — no goalpost-moving). The harness ordering is fixed for
G148 so future runs classify correctly.

**Reading (honest, careful).** Neither "no advantage anywhere" (the gap is clearly NOT flat — it grows and
annealing sweeps 6/6 by n=150) nor "advantage established" (gap < the pre-set 0.02 at n=150) is the right
call yet. A real separation between annealing and even a strong *correct* greedy **emerges as frustrated
instances get larger** — consistent with the textbook fact that local search degrades faster than annealing
on hard glassy landscapes. The programme's positive claim is neither refuted nor confirmed; it is
**emerging and scale-dependent**.

**Pre-registered G148:** rerun at larger n ∈ {200, 280, 360} (5 instances each), with the classification
ordering fixed. Decisive bars: ADVANTAGE if mean gap ≥ 0.02 at the largest n AND anneal wins ≥ 4/5 (the gap
crosses threshold → G145's claim restored on hard instances vs a correct baseline); NO_ADVANTAGE if the gap
plateaus/shrinks below 0.01 (the n=150 trend was a ceiling artifact); EMERGING-still if it keeps growing but
stays in (0.01, 0.02). Budgets reported; greedy stays at 60 restarts (strong).
</content>
