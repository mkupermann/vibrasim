# G168 — register interference: do two registers coexist?

**Status: SIGNED OFF 2026-08-12/13 (round 8 unanimous 5/5 for interference;
C's SENS arm + order permutation and A's structural framing incorporated
verbatim; D explicit bars-JA) — committed before any data (D2). Bars final
per D3.**
**Verdict 2026-08-13: UNCLASSIFIABLE (bars gap)** — the outcome (structural
write-interference real: 41/47 write-time cross-bonds consuming end valence,
census invalid; yet decode ≥ 0.979 everywhere, FAR clean, SENS fired,
controls clean) fits no registered class: PASS demands cross-bonds = 0,
PARTIAL demands decode < 0.90. No claim; scale correction = new ID. The two
interference axes (structural vs informational) were conflated in one scale.
LOGBOOK 2026-08-13.

## 1. The one question (D1)

> Do two 6-bit rest-length registers, written side by side and held through
> the certified agitation regime, decode INDEPENDENTLY — or do their free
> chain ends (the only sites with free valence, hence the only write sites)
> cross-bond and corrupt each other?

Structural prediction (researcher A): valence saturation moved the
fold-freeze mechanism from chain interiors to the four free ends; two
adjacent registers are the only configuration in which those ends come into
range. G168 is the only remaining run where PRIM14 can write wrongly from
its own physics. Separability is also the precondition for any association
work (G154/G161 class) and for the kinematics dossier (researcher C).

## 2. Protocol

Two 7-carrier chains along x (X0 = 15, encoding 6.5/10.5, scramble 8.5,
decode > 8.5), parallel at y = 30 ± Δy/2, z = 30, box 120 × 60 × 60.
Idle 10 000 ticks under the certified kick regime (magnitude 1.0, every 50
ticks, per-tick min-CROSS-distance tracked). Scramble both chains; retrieve
800 quiet ticks with BOTH carrier-0 pinned; decode each register separately.
8 pattern-pairs (independent random patterns per register) × seeds
{42, 7, 13}.

**Write-order permutation (researcher C, fixed now):** even pattern index →
register R1 consolidated first; odd → R2 first. Reported metric:
order effect = mean acc(written-first) − mean acc(written-second); |effect|
> 0.2 attaches the label **ORDER-EFFECT** to any verdict.

Arms:
- **NEAR:** Δy = 10 (ends within the formation window 12 — cross-bonds
  physically possible). The question.
- **FAR (contrast):** Δy = 20 (cross-bonds geometrically impossible).
- **SENS (researcher C's sensitivity arm):** Δy = 6 — ends deep inside the
  window at write time; cross-bonding is deliberately provoked. The
  interference signal MUST demonstrably appear here (cross-bond count > 0
  in ≥ half the runs OR decode < 0.90), else the whole setup is
  insensitive → **INCONCLUSIVE**.
- **OLDREST@NEAR** (attribution) and **NEG@NEAR** (static, bonds deleted at
  scramble — the G167-certified control design).

Census: write census per chain (expected graph: two disjoint 6-bond chains;
cross-bonds at write are counted as WRITE-X, a measured phenomenon, not
hidden); idle census every 1 000 ticks with cross-bond and rebond counts;
per-tick min cross-chain distance.

## 3. Pre-registered bars (fixed before any data; D3)

Accuracy per register on total bits (8 × 6 per register per seed).

- **PASS (separable):** NEAR both registers ≥ 0.90 on ≥ 2/3 seeds AND
  cross-bonds at NEAR = 0 (write + idle) AND FAR ≥ 0.90 AND SENS fires
  (sensitivity satisfied) AND OLDREST ≤ 0.6 AND NEG < 0.90 and ≤ 0.6 AND
  boundary ≤ 10% everywhere.
- **PARTIAL (interference measured):** FAR ≥ 0.90 but NEAR < 0.90 on one or
  both registers, with the cross-bond/WRITE-X census as the mechanism — the
  interference boundary is the finding.
- **NULL:** NEAR and FAR both < 0.90 (degradation is not proximity-specific;
  two-register operation fails for another reason, census-classified).
- **INCONCLUSIVE:** SENS does not fire, or NEG ≥ 0.90, or boundary > 10%.
- **FAIL:** FAR write census invalid (baseline geometry broken), or OLDREST
  ≥ 0.75, or controls otherwise broken.
- ORDER-EFFECT label attaches to any verdict when |order effect| > 0.2.

## 4. Predictions (calibration, before data)

- SENS fires: 75% (write-time end distance ≈ 6 → form_bridges should
  cross-bond during consolidation; residual risk: consolidation pinning
  positions may keep ends exactly at Δy=6 > … no, 6 < 12, it should fire).
- NEAR cross-bonds at write: 35% (end pairs at ≈10 — inside the window;
  pinned consolidation geometry holds them there for 8 ticks).
- Verdict: PASS 30%, PARTIAL 40%, NULL 5%, INCONCLUSIVE 15%, FAIL 10%.
- Most-likely failure mode: PARTIAL via WRITE-X at NEAR — interference
  happens at write time, not during idle (the ends sit at 10 < 12 during
  consolidation itself).

## 5. Budget

Harness (two-chain geometry + cross metrics): 40 min. Compute: ~120 runs
@ ≤11k ticks ≈ 40 min. Verdict + LOGBOOK + FRONTIER (D10): 30 min.
**Realistic 2 h → hard cap 4 h.**

## 6. Out of scope

Association, > 2 registers, Δy sweeps beyond the three registered arms,
kinematics dossier, kick-magnitude variation.
