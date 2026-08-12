# G172 — association bandwidth on writability-clean geometry

**Status: SIGNED OFF 2026-08-13 (round 12: A, C, D, E for clean-geometry
bandwidth; A's engineered-disclosure and C's validation-first + permanent
dual-gate conditions incorporated; D JA after the corners-majorize rebuttal
of his selection-bias concern) — committed before any data (D2). Bars final
per D3.**

## 1. The one question (D1)

> With cross-contact WRITABILITY made pattern-independent by construction
> (centered chains, Δy = 8, k ∈ {4, 6, 12}), does association through the
> cross-structure follow the exactly derived bandwidth curve
> **0.667 / 0.750 / 1.000** — the axis G171 tried to measure and could not?

Honesty (researcher A's condition, D5): the contact geometry is ENGINEERED
structure — admissible like ports, not an emergent finding. Her G171-era
self-correction is on record: under end-anchoring, stored content and
connectivity were COUPLED (pattern-dependent end offsets decided whether a
bond could form at all); G172 exists to decouple them. G171's
pattern-dependent-writability observation is hereby protocolled as a
STANDALONE finding of the register line, not a mere disturbance.

## 2. Two-stage protocol (researcher C's validation-first condition)

**Stage 1 — writability validation (engineering gate, runs FIRST):**
centered chains (each chain's center fixed; ends deviate ≤ bits_per·2 from
center), Δy = 8 → worst-case end-to-end distance √(64 + (bits_per·2)²) =
{10.0, 8.9, 8.25} for bits_per {3, 2, 1} — all < 12 for EVERY pattern.
Validation: the 4 corner pattern-pairs per arm (all-0/all-1 combinations,
the extreme spans) × 3 seeds × all arms → cross censuses must be 100%
exact. Any miss = engineering stop; Stage 2 does not run.

**Stage 2 — the measurement (only after Stage 1 passes):** as G171 with
arms k=4 (m=2, 3-bit chains), k=6 (m=3, 2-bit), k=12 (m=6, 1-bit);
scramble is CENTERED uniform. Permanent dual gate (researcher C, now
standing for the whole register line):
- **Sensitivity:** k=12 must reach ≥ 0.90 (an arm that demonstrably falls
  elsewhere exists via NEG) — else INCONCLUSIVE.
- **Specificity (Freigabebedingung):** SCRAM-X with SPAN-MATCHED decoys
  (decoy drawn with identical per-chain bit-weight → identical spans; only
  the bit ARRANGEMENT differs; chains with uniform weight re-draw) must sit
  ≤ 0.6 AND < 0.75 BEFORE any treatment value counts — else INCONCLUSIVE
  (the G171 span leak, closed by construction and verified).
- **NEG** (cross deleted): ≤ 0.6.

8 pattern-pairs × seeds {42, 7, 13} per arm; all censuses, boundary gate.

## 3. Pre-registered bars (fixed before any data; D3)

- **BANDWIDTH-LAW CONFIRMED:** monotone k=4 < k=6 < k=12, k=12 ≥ 0.90,
  controls per dual gate, all censuses valid.
  Sub-verdict **QUANT-MATCH** (±0.10 per arm vs 0.667/0.750/1.000;
  reported, does not gate).
- **ASSOCIATION-FLAT:** k=12 ≥ 0.90 without monotone scaling below
  (defined: k=4 or k=6 within 1/48 of chance 0.5).
- **CLASS-NULL:** all arms at chance incl. k=12, controls clean —
  researcher C's abort clause MAY fire (programme decision), only then.
- **INCONCLUSIVE:** dual-gate violation (k=12 < 0.90, or SCRAM-X > 0.6),
  or Stage-1 gate missed, or boundary/census breaks.
- **FAIL:** NEG or SCRAM-X ≥ 0.75 (artifact), or Stage-2 census invalid
  after a passed Stage 1 (writability model wrong — engineering stop).

## 4. Predictions (calibration, before data)

- Stage 1 passes: 85% (the geometry bound is closed-form; residual risk is
  implementation).
- Derived curve (exact enumeration, code in the amendment's tool):
  k=4 → 0.667, k=6 → 0.750, k=12 → 1.000.
- Verdict: BANDWIDTH-LAW CONFIRMED 55% (QUANT-MATCH CONFIRMED 40%),
  ASSOCIATION-FLAT 5%, INCONCLUSIVE 25%, FAIL 10%, CLASS-NULL 5%.
- Most-likely failure mode: INCONCLUSIVE via span-matched SCRAM-X still
  above 0.6 — if arrangement-independent geometry statistics beyond span
  leak through, the specificity gate catches exactly that.

## 5. Budget

Harness delta (centering, span-matched decoys, staging): 40 min. Stage 1:
minutes. Stage 2: ~30 min. Verdict + LOGBOOK + FRONTIER (D10): 30 min.
**Realistic 2 h → hard cap 4 h.**

## 6. Out of scope

k=2 (geometrically unwritable per the standalone finding), retention of
associations, bidirectional recall, kinematics dossier.
