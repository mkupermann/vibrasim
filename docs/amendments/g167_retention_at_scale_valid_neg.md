# G167 — retention at scale, re-run with a measurable NEG control

**Status: SIGNED OFF 2026-08-12 (A and C authored the two design conditions in
their round-7 votes — static NEG, sensitivity gate — incorporated verbatim;
D explicit JA; majority incl. external member) — committed before any data
(D2). Bars final per D3.**

## 1. The one question (D1)

Identical to G166 (24-bit register × kick agitation), whose verdict was
INCONCLUSIVE solely through a control-arm artifact: the bondless NEG under
kicks has no damping (damping lives in bridge tension), drifted linearly out
of the box, and was never validly measured. G167 repairs ONLY the control
design and re-certifies the whole run.

## 2. Protocol (delta to G166 — everything else identical)

- **NEG redesign (researcher A):** static NEG after the G163 pattern —
  bonds are deleted at scramble time and the NEG runs NO kick agitation
  (its role is the readout-needs-bonds check; T0 covers bonds-without-
  agitation). No artificial damping assumption enters the chance baseline.
- **NEG sensitivity criterion (researcher C, fixed now):** the NEG must fall
  MEASURABLY below the PASS threshold — pre-registered: NEG accuracy < 0.90
  AND ≤ 0.6 on the standard chance bar. A NEG ≥ 0.90 proves the metric does
  not discriminate → verdict **INCONCLUSIVE**, never PASS. (This converts
  C's G164 "trivial-PASS" worry into a hard gate: a certified PASS now
  requires an arm in which the score demonstrably falls.)
- All other arms, gates, metrics, seeds, patterns bit-identical to G166
  (P@K24 + P@K6 contrast at {2k, 10k, 50k}, T0@50k, OLDREST@50k, per-tick
  min-NN + time-fraction-below-window, rebonding threshold, boundary
  anti-bias gate, perturbation floor, within-run controls). The P-arm kick
  seeds are unchanged — their G166 trajectories reproduce deterministically;
  certification requires all arms from ONE registered run.

## 3. Pre-registered bars (fixed before any data; D3)

As G166 §3, with the NEG clauses replaced by:
- PASS-clean additionally requires **NEG < 0.90 and ≤ 0.6** (sensitivity +
  chance), measured with boundary rate ≤ 10% in the NEG arm.
- **INCONCLUSIVE:** NEG ≥ 0.90 (metric non-discriminating) or NEG boundary
  rate > 10% (control unmeasurable — again) or P-arm boundary > 10% at an
  interval.

## 4. Predictions (calibration, before data)

- Static NEG lands at ~0.5 (share of zeros) with boundary 0: 90%.
- P-arms reproduce their G166 values (deterministic seeds): 95%.
- Verdict: **PASS clean 80%**, INCONCLUSIVE 8%, PARTIAL/NULL 5%, FAIL 7%.
- Most-likely failure mode: none dominant — this is a certification re-run;
  the honest risk is a surprise non-reproduction of the P-arms, which would
  itself be a serious finding (nondeterminism in the stack).

## 5. Budget

Harness: NEG branch change only, 10 min. Compute ≈ G166 (~1.5–2 h).
Verdict + LOGBOOK + FRONTIER: 30 min. **Realistic 2.5 h → hard cap 5 h.**

## 6. Out of scope

Interference (C's Nachrang: mechanistically sharpened, next question after
certification), association, kinematics dossier, kick-magnitude sweeps.
