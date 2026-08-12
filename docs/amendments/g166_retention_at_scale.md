# G166 — retention at scale: 24 bits × 50 000 ticks of agitation

**Status: SIGNED OFF 2026-08-12 by round-table majority (A, C, E = 3:1;
B abstention per protocol; D's NEIN — "PASS-Prediction 40% unterschreitet
Mindestkonfidenz" — is recorded and rejected on principle: requiring high
prior PASS-confidence selects for confirmatory experiments and contradicts
the falsification discipline, where an uncertain outcome marks a GOOD
experiment. A's per-tick strain sampling and C's K6 contrast arm + within-run
T0 are incorporated) — committed before any data (D2). Bars final per D3.**

## 1. The one question (D1)

> Does the 24-bit register survive the G164 agitation protocol — the cross
> product G164 × G165 that each experiment kept unstressed? At K=24 the chain
> already operates with non-neighbour distances at the formation window
> (G165: min-NN 11.68 < 12 during quiet retrieve); under 50 000 ticks of kick
> agitation one excursion suffices to push non-neighbours into the window,
> whereupon PRIM14 freezes the folded geometry PERMANENTLY. This is the first
> run where rebonding = 0 is not free — the only known intrinsic failure
> mechanism of the register becomes live (researcher A).

## 2. Protocol (merge of two validated protocols, nothing new)

G164 protocol (write → idle under kick agitation → scramble → retrieve →
decode; kicks magnitude 1.0 every 50 ticks, census every 1 000 ticks with
new/lost bond counts, drift + RMS metrics, perturbation floor
RMS ≥ max(3×RMS_T0, 0.1), rebonding threshold: net new idle bonds = 0 for a
clean verdict else the with-confound label) at **K = 24** (G165 geometry:
box 300, encoding 6.5/10.5, scramble 8.5) plus the G165 gates (boundary
anti-bias gate INCONCLUSIVE@>10%, strain metrics min-NN + gyration).
Idle intervals {2 000, 10 000, 50 000}. Arms: **P@K24** at all three
intervals, **P@K6 contrast arm at all three intervals** (researcher C:
within-run attribution — if K6 holds while K24 breaks, the finding is a
LOAD-dependent capacity-under-time limit; if both break alike, it is
retention; pre-registered mapping, no post-hoc choice), T0@50k, OLDREST@50k,
NEG@50k (all at K24; T0 comes from THIS run — no cross-run import).
8 patterns × seeds {42, 7, 13}.

**Strain sampling (researcher A, fixed now):** min non-neighbour distance is
tracked as a PER-TICK running minimum (census-interval sampling would see
~1% of the kick dynamics; excursions below the formation window last ~10
ticks), plus the TIME FRACTION of idle ticks with min-NN < 12. A "min-NN
stayed above the window" statement is only admissible from the per-tick
series. Bond counts remain census-based (bonds persist; distances do not).

Accuracy on total bits per arm/seed (8 × 24 = 192 bits; granularity 1/192).

## 3. Pre-registered bars (fixed before any data; D3)

- **PASS (clean):** P ≥ 0.90 at all three intervals on ≥ 2/3 seeds AND net
  new idle bonds = 0 AND OLDREST ≤ 0.6 AND NEG ≤ 0.6 AND T0@50k ≥ 0.90 AND
  write censuses valid AND boundary rate ≤ 10% everywhere.
- **PASS WITH REBONDING CONFOUND:** decode bars met but new idle bonds > 0 —
  reported as its own category (the mechanism wrote during idle; the decode
  success may ride on frozen fold geometry).
- **PARTIAL:** P@2k ≥ 0.90 but a longer interval < 0.90 — decay curve +
  census events (fold-bond counts) are the finding; A's mechanism becomes
  measurable.
- **NULL:** P@2k < 0.90, controls clean.
- **INCONCLUSIVE@interval:** boundary rate > 10% at that interval.
- **FAIL:** OLDREST ≥ 0.75, or NEG > 0.6, or write census invalid, or
  T0@50k < 0.90 (drift baseline broken — engineering stop).

## 4. Predictions (calibration, before data)

- P@2k ≥ 0.90: 75%. P@50k clean (rebonding 0): **40%** — A's fold-freeze
  mechanism has 50 000 ticks × ~8 units drift amplitude to find the window
  at K=24; G164's K=6 chain had 20+ units of window margin, this one has
  < 0.7.
- Fold-bond events observed (census new bonds > 0 anywhere): 45%.
- Verdict: PASS clean 35%, PASS-with-confound 10%, PARTIAL 30%, NULL 5%,
  INCONCLUSIVE 5%, FAIL 15%.
- Most-likely failure mode: PARTIAL at 50k via fold bonds — which would be
  the register's first measured intrinsic decay channel.

## 5. Budget

Harness merge (G164 idle loop into G165 K-geometry): 20 min. Compute:
~100 runs, most at 50k ticks with 25 carriers ≈ 45–70 min. Verdict + LOGBOOK
+ FRONTIER (D10): 30 min. **Realistic 2 h → hard cap 4 h.**

## 6. Out of scope

Interference (next question, C's precondition argument noted), association,
kick-magnitude sweeps, adaptive rests, flux port.
