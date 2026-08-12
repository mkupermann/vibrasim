# G169 — interference re-certification: two axes, one mechanism test

**Status: SIGNED OFF 2026-08-13 (round 9: A, C, E, F for the two-axis
re-certification, 4/5; A's margin metric + point-prediction axis and C's
anti-tuning declaration + location logging incorporated verbatim; D explicit
bars-JA — his mechanism-first position is embedded as the MECHANISM
sub-verdict) — committed before any data (D2). Bars final per D3.**
**Verdict 2026-08-13: COUPLED-BUT-SEPARABLE (structural BROKEN / informational
INTACT — R1 1.000, R2 ≥ 0.917 on all seeds), MECHANISM-OPEN (point prediction
falsified at 0.375: 13 LI bonds reveal a transient interior-vulnerability
window during sequential write; R2-exclusivity of losses unexplained). All
gates green. Harness aggregation gap disclosed and resolved by deterministic
re-execution. LOGBOOK 2026-08-13.

## 1. The one question (D1)

> On the pre-registered TWO-AXIS scale (structural: does the bond graph
> couple? informational: does the content survive?), where do two adjacent
> rest-length registers land — and does the pre-registered POINT PREDICTION
> of the loss mechanism hold: a far-end↔far-end cross-bond causes exactly
> one bit error on the upper register (R2), while carrier-0↔carrier-0
> cross-bonds cause none (both retrieve-pinned)?

## 2. Honesty declaration (researcher C's anti-tuning condition)

G168 ran this protocol and landed outside its one-axis scale; the chair
KNOWS its aggregates (NEAR 0.986, write_x 41, SENS fired, controls clean)
and a 12-run diagnostic probe suggested the loss mechanism. This scale is
therefore derived from MECHANISM, not from those numbers: the flip margin
(2.0 units) follows from the encoding (|6.5−8.5| = |10.5−8.5| = 2.0); the
0.90 bars are the register line's standard; and the pre-registered point
prediction, per-bit margins, and cross-bond locations were NEVER measured
in any prior run — they cannot be tuned to a known result. The probe has no
evidential status and its 12 runs are disjoint from the registered seeds'
pattern draws.

## 3. Protocol

Identical to G168 (same arms NEAR/FAR/SENS/OLDREST/NEG, same seeds,
patterns, order permutation, kick regime, censuses, boundary gate), plus
three registered metrics:
- **Cross-bond location class** per bond: (0,0) both carrier-0 ends,
  (L,L) both far ends, (0,L)/(L,0) mixed. (Interior carriers are
  valence-saturated; only end pairs can bond.)
- **Per-bit flip margin** at decode: |spacing − 8.5| per bit; minimum per
  register per run.
- **Point-prediction score:** per run, predict the error set from the
  census — (L,L) bond present ⇒ exactly one bit error, located on R2;
  no (L,L) bond ⇒ zero errors — and score the prediction (hit = exact
  match of error count AND register).

## 4. Pre-registered two-axis scale (fixed before any data; D3)

**Structural axis:** BROKEN if cross-bonds (write + idle) occur in > 10% of
NEAR runs; INTACT otherwise. (SENS must fire structurally — its own gate.)
**Informational axis:** BROKEN if any register decodes < 0.90 at NEAR on
≥ 2/3 seeds; INTACT otherwise.

Verdict = the cell, each pre-named:
- (INTACT, INTACT): **SEPARABLE-CLEAN** — registers coexist untouched.
- (BROKEN, INTACT): **COUPLED-BUT-SEPARABLE** — bond graphs couple, content
  survives; margins + point-prediction quantify HOW.
- (INTACT, BROKEN): **ANOMALY** — information lost without structural
  coupling: engineering stop, investigate before any claim.
- (BROKEN, BROKEN): **INTERFERENCE** — the register lines' coexistence
  limit, census-classified.

**Mechanism sub-verdict (independent of the cell):**
- **MECHANISM-CONFIRMED:** point-prediction hit rate ≥ 0.90 over all NEAR +
  SENS runs.
- **MECHANISM-OPEN:** < 0.90 — the loss channel is not (only) the (L,L)
  bond; the R2 asymmetry question returns to the table.

Gates carried over unchanged: SENS structural firing (else INCONCLUSIVE),
NEG sensitivity (< 0.90 and ≤ 0.6), OLDREST ≤ 0.6, boundary ≤ 10%,
FAR write census valid (else FAIL), ORDER-EFFECT label at |effect| > 0.2.

## 5. Predictions (calibration, before data)

- Cell (BROKEN, INTACT) "COUPLED-BUT-SEPARABLE": 70%; (BROKEN, BROKEN) 15%;
  (INTACT, INTACT) 5%; ANOMALY 2%; gates/INCONCLUSIVE/FAIL 8%.
- MECHANISM-CONFIRMED: 60% — the R2-only asymmetry is the least understood
  element; a hit rate below 0.90 with (L,L) bonds sometimes hitting R1
  would be the informative miss.
- Min flip margin at NEAR (unaffected bits): > 1.0 units: 70%.

## 6. Budget

Harness metric extension: 30 min. Compute ≈ G168 (~40 min). Verdict +
LOGBOOK + FRONTIER (D10): 30 min. **Realistic 1.5 h → hard cap 3 h.**

## 7. Out of scope

Association, kinematics dossier, Δy sweeps, > 2 registers, kick variation.
