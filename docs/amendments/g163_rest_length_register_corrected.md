# G163 — rest-length register, corrected encoding (measured formation window)

**Status: SIGNED OFF 2026-08-11, no conditions — committed before any data generation (D2). Bars final per D3.**

## 1. The one question (D1)

Identical to G162 (geometry-coded bits retrieved from a scrambled chain under
PRIM14), with the encoding corrected after G162's census FAIL and a MEASURED
bond-formation window.

## 2. What changed vs G162 (and why)

G162 FAILED at its census gate: adjacent zero bits (4+4 = 8) put i↔i+2 inside
the bond-formation window → skip bonds + a dropped chain bond; the protocol's
"≥12 cannot bond" claim was wrong. The window has now been measured directly
(engineering probe, LOGBOOK 2026-08-11): **bonds form for d < 12, sharp cutoff
at exactly 12 (= r_2)**.

Corrected encoding (all constraints measured-safe):
- **SHORT = 6.5** (bit 0), **LONG = 10.5** (bit 1) — every consecutive spacing
  < 12 (chain bonds form); minimal non-consecutive sum = 6.5+6.5 = **13 ≥ 12**
  (skip bonds impossible for EVERY pattern).
- **Scramble state: uniform 8.5** (the midpoint = maximum ignorance).
- **Read: bit k = 1 iff spacing > 8.5.**
- OLDREST control: global rule relaxes spacings toward r_eq = 6 → decodes
  all-0 (~share of zeros ≈ chance).
- Everything else identical to G162: 7 carriers, valence 2, 8 consolidation
  ticks, carrier-0 pin, 800 retrieve ticks at k=8/damping 0.95, formation
  freeze + census (now including rest-value verification against the encoded
  pattern in ARM-P), 8 patterns × seeds {42, 7, 13}, box 120×60×60.

## 3. Pre-registered bars (unchanged from G162; fixed before any data, D3)

- **PASS:** ARM-P mean ≥ 0.90 on ≥ 2/3 seeds AND OLDREST mean ≤ 0.6 AND
  NEG mean ≤ 0.6 AND all censuses clean.
- **PARTIAL:** ARM-P 0.75 ≤ mean < 0.90 on ≥ 2/3 seeds, controls clean.
- **NULL:** ARM-P < 0.75, controls clean.
- **FAIL:** OLDREST ≥ 0.75, or any census violated, or NEG > 0.6.

## 4. Predictions (calibration, before data)

- Census clean everywhere: 90% (skip bonds are now geometrically impossible;
  residual risk is untested spacing-formation corner cases).
- ARM-P ≥ 0.90: 75% (G162's no-status observation suggests strong decode even
  under broken topology; clean topology should not be worse).
- Verdict: PASS 70%, PARTIAL 12%, NULL 8%, FAIL 10%.
- Most-likely failure mode: 800 ticks insufficient for the 1.5–2-unit
  spacing corrections at chain scale → interior misdecodes → PARTIAL.

## 5. Budget

Harness parametrization: 15 min. Runs: minutes. Verdict + LOGBOOK + FRONTIER:
30 min. **Realistic 1 h → hard cap 2 h.**

## 6. Out of scope

As G162 §6 (association, capacity, retention, interference, efficiency, flux).
