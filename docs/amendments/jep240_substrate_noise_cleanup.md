# JEP-240 — substrate multi-hop chaining under cue noise: is attractor CLEANUP the native (partial) cure for compounding?

Pre-registered 2026-06-05 (BEFORE the run). Connects the substrate-relational arc (JEP-232..239) to the programme's
deepest conceptual finding — the UNIVERSAL compounding-vs-aggregation-vs-cleanup insight (JEP-137/138/140/158):
chained inference compounds errors; attractor CLEANUP re-anchors continuous drift (JEP-158); redundant AGGREGATION
is the fuller cure (JEP-138/140). JEP-233 showed substrate chaining is 1.00 NOISELESS. This BET adds CUE NOISE and
asks whether the substrate's own attractor dynamics (decode-to-clean each hop) mitigate multi-hop compounding.

## Method (no transformer)
- JEP-232 store (is-a chain c0→…→cn). At each hop, flip a fraction `f` of the KEY cue bits before clamping (cue
  noise). Walk k hops two ways:
  - **raw**: re-clamp the settled VALUE bits directly (continuous drift accumulates).
  - **cleanup**: decode the settled value to the nearest clean concept code and re-clamp THAT (the substrate's native
    attractor re-anchoring).
- First find `f*` giving single-hop recall ≈ 0.85 (so multi-hop has errors to compound). Then k-hop recall vs depth
  (k=1..4) for raw vs cleanup at `f*`. Seeds 42 & 7, K=12 facts (within capacity).

## Bars (locked pre-run)
| ID | Criterion | Bar |
|----|-----------|-----|
| J240a | Single-hop noise calibrated | an `f*` exists with single-hop recall in [0.78, 0.92] (both seeds) |
| J240b | Compounding is REAL | raw k=4 recall < raw k=1 by ≥ 0.15 (errors compound with depth, both seeds) |
| J240c | Cleanup MITIGATES | cleanup k=4 recall > raw k=4 by ≥ 0.10 (re-anchoring removes drift, both seeds) |
| J240d | Cleanup is only PARTIAL | cleanup k=4 recall < cleanup k=1 (discrete decode errors still propagate — not a full cure, both seeds) |

PASS = J240a–d → the substrate's attractor cleanup is the native PARTIAL cure for multi-hop compounding (mitigates
drift, doesn't fix discrete errors) — the JEP-158 insight, native in the substrate; full cure still needs redundancy/
aggregation (JEP-138/140). NULL (honest): J240b fails → no compounding at this noise (raise f or it's a non-effect);
J240c fails → cleanup doesn't help here (the value drift is already negligible — match the regime to the mechanism,
the JEP-157 lesson); J240d fails → cleanup fully cures (a stronger positive than predicted). No post-hoc tuning.

## Prediction (locked BEFORE run) [predict-calibrate]
🔮 J240a PASS (a flip fraction ~0.25–0.4 of the 40-bit key should drop single-hop to ~0.85 — enough corruption to
sometimes cross an attractor basin). J240b PASS — raw chaining compounds (continuous drift + decode errors), k=4 well
below k=1. J240c PASS — cleanup re-anchors each hop to a clean attractor, removing the continuous-drift component, so
cleanup k=4 > raw k=4. J240d PASS — cleanup still propagates DISCRETE per-hop decode errors (~single-hop-error per
hop), so cleanup k=4 < cleanup k=1: a partial, not full, cure. This reproduces JEP-158 (cleanup cures drift not
discrete errors) natively in the substrate and ties it to the universal insight. RISK (match-regime, JEP-157): if
the attractors are so strong that a 0.85-single-hop cue still relaxes cleanly, the raw value has little drift and
J240c could be marginal — then cleanup ≈ raw (both just decode errors). Established (Hopfield basins, cleanup memory,
error compounding), named; no novelty — the value is connecting the substrate-relational arc to the programme's core.

## RESULT (2026-06-05): NULL/PARTIAL — cleanup does NOT reliably cure discrete compounding (it can LOCK IN errors); sharpens JEP-158

| seed | f* | single-hop | raw k1→k4 | cleanup k1→k4 | cleanup−raw @k4 |
|------|----|------------|-----------|----------------|-----------------|
| 42 | 0.20 | 0.83 | 0.83 → 0.11 | 0.83 → 0.33 | +0.22 (helps) |
| 7  | 0.20 | 0.92 | 0.92 → 0.67 | 0.92 → 0.67 | 0.00 (no effect) |

Clarifying mechanism check at FIXED, matched noise (not a bar retune — characterizing the effect):

| f | seed | single | raw k4 | cleanup k4 | cleanup−raw |
|---|------|--------|--------|------------|-------------|
| 0.30 | 42 | 0.50 | 0.00 | 0.22 | **+0.22 (helps)** |
| 0.30 | 7  | 0.58 | 0.33 | 0.22 | **−0.11 (HURTS)** |
| 0.35 | 42/7 | 0.33/0.58 | 0.00/0.11 | 0.00/0.11 | 0.00 (both collapse) |

- **J240a ✓** (noise calibrated), **J240b ✓** (compounding is real: raw 0.83→0.11), **J240d ✓** (cleanup is at most
  partial: k4<k1 always).
- **J240c ✗ (the prediction MISSED)** — cleanup does NOT reliably mitigate: it helps seed 42 (+0.22) but does NOTHING
  for seed 7 at f*, and at matched f=0.30 it actively HURTS seed 7 (−0.11). The clarifying run shows this is a REAL
  non-robustness, not just the f*-calibration artifact I first suspected.

**FINDING (a genuine NULL that SHARPENS the universal insight):** in a DISCRETE bipolar content-addressable store
under cue noise, attractor CLEANUP is NOT a reliable cure for multi-hop compounding. Its quantization can LOCK IN a
decode error — a wrong-but-CLEAN code is re-clamped and propagates CONFIDENTLY, sometimes worse than raw (whose
residual ambiguity occasionally self-corrects at the next hop). This REFINES JEP-158 (where cleanup cured CONTINUOUS-
embedding drift): cleanup helps against continuous drift but NOT against discrete decode errors, and can amplify
them. The robust, regime-independent cure for compounding remains REDUNDANCY / AGGREGATION (independent paths +
voting, JEP-138/140) — NOT per-hop cleanup. So the substrate-relational arc inherits the programme's core lesson with
a sharpened caveat: aggregation, not cleanup, is the cure that generalizes.

**CALIBRATION:** I predicted cleanup mitigates (J240c PASS). It does not reliably — I over-generalized JEP-158's
continuous-drift cleanup to the discrete-CAM regime (error-class 10: don't carry intuition across representations —
the SAME lesson JEP-158 itself taught, applied one level up). I flagged the match-regime risk but under-stated it:
cleanup can HURT, not merely be marginal. Verdict: **NULL/PARTIAL** (a/b/d PASS; the headline c failed — recorded,
not retuned). The conceptual payoff is the sharpened cure hierarchy: aggregation > cleanup for discrete compounding.
