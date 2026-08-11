# G164 — retention: does the rest-length register survive time under agitation?

**Status: SIGNED OFF 2026-08-11 by round-table majority (4/6 incl. two external
members; the sceptic's first NEIN was resolved by hardening, not by relaxing:
rebonding threshold and the closed verdict gap were added BEFORE data) —
committed before any data generation (D2). Bars final per D3.**

## 1. The one question (D1)

> Does a G163-written rest-length register (6 bits, encoding 6.5/10.5) still
> decode at ≥ 0.90 after an IDLE interval of free, thermally agitated dynamics
> (no pins, node_thermal_speed = 2.0 — the chain_cascade calibration value)
> inserted between write and the G163 scramble/retrieve — across 2 000, 10 000
> and 50 000 idle ticks?

Without retention, "register" is an overclaim: G163 measured write → immediate
scramble → immediate read. G164 adds exactly one factor (idle-under-agitation)
to the validated G163 protocol; geometry, encoding, dynamics, controls and the
readout are unchanged (retrieve runs at thermal 0.0, identical to G163, so
decode differences attribute to the idle phase alone).

## 2. Protocol (all else = G163)

Per pattern: write (8 consolidation ticks, census gate as G163) → **IDLE**
(all pins released, node_thermal_speed = 2.0, N ∈ {2 000, 10 000, 50 000}
ticks) → scramble to uniform 8.5 → retrieve 800 ticks (thermal 0, carrier-0
pin, formation freeze) → decode (> 8.5).

Recorded during idle (round-table conditions, measured variables, NOT gates):
- **Bond census sampled every 1 000 ticks** (researcher A): LOST bonds are the
  decay mechanism; NEW register-internal bonds are a REBONDING CONFOUND — at
  spacing 10.5 every carrier pair sits below the formation cutoff 12, and a
  bond formed during idle freezes its CURRENT geometry, so decode success can
  ride on idle-written bonds instead of the original rests. Pre-registered
  threshold (fixed now, no adjustment): net NEW register-internal bonds during
  idle must be 0 for the clean PRIM14 retention claim; any arm/seed with > 0
  is classified separately as "PASS/PARTIAL WITH REBONDING CONFOUND" and never
  as a clean verdict. New-bond and lost-bond counts are reported per interval.
- **Drift measure** (researcher B): max carrier displacement from written
  position at idle end, per run.

Arms (8 patterns × seeds {42, 7, 13} each):
- **ARM-P@2k / P@10k / P@50k:** the question.
- **ARM-T0@50k:** idle at thermal 0.0 — numerical-drift baseline.
- **ARM-OLDREST@50k:** global r_eq, thermal 2.0 — attribution control.
- **ARM-NEG@50k:** bonds deleted before idle, thermal 2.0 — readout control.

## 3. Pre-registered bars (fixed before any data; D3)

Accuracy is defined on TOTAL bits per arm/seed (8 patterns × 6 bits = 48;
granularity 1/48 — researcher B: a 0.90 bar on a single 6-bit register would
be unreachable between 0.833 and 1.0).

- **PASS:** ARM-P decode ≥ 0.90 at ALL three intervals on ≥ 2/3 seeds AND
  OLDREST ≤ 0.6 AND NEG ≤ 0.6 AND T0@50k ≥ 0.90 AND write-censuses clean
  AND net new idle bonds = 0 (else the with-confound label applies).
- **PARTIAL:** P@2k ≥ 0.90 on ≥ 2/3 seeds but a longer interval < 0.90 —
  the decay curve (decode vs interval + census events) is the finding.
  Same rebonding-confound labelling.
- **NULL:** P@2k < 0.90 (researcher B: the former 0.75–0.90 gap is hereby
  CLOSED into NULL — any @2k accuracy below the PASS bar is NULL, no
  post-hoc zone assignment), controls clean.
- **FAIL:** OLDREST@50k ≥ 0.75 (attribution broken), or NEG > 0.6, or any
  write-census invalid, or **T0@50k < 0.90** (numerical drift alone destroys
  the register — design premise broken, engineering stop).

## 4. Predictions (calibration, before data)

- T0 baseline holds: 90%.
- P@2k ≥ 0.90: 70%. P@50k ≥ 0.90: 35% — Brownian agitation over 50k ticks
  plausibly folds the free chain until end-to-end distance < 12 → fold bond →
  topology corruption (researcher A's spontaneous-write warning).
- Verdict: PASS 30%, PARTIAL 35%, NULL 15%, FAIL 20% (dominated by the
  T0-baseline risk and fold-bond artifacts in controls).
- Most-likely failure mode: PARTIAL via fold-bond events at 10k/50k, visible
  in the sampled census.

## 5. Budget (hybrid, §5)

Harness extension (idle phase + census sampling + drift): 30 min. Compute:
~5M ticks ≈ 1–1.5 h wall. Verdict + LOGBOOK + FRONTIER (D10): 30 min.
**Realistic 2.5 h → hard cap 5 h.**

## 6. Out of scope

Capacity, interference, association, adaptive rests, thermal-level sweeps
beyond the two registered values, flux port, efficiency.
