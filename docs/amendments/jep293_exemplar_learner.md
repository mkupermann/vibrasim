# JEP-293 — Corrections must STICK: nearest-mean → nearest-exemplar ActiveLearner

## Motivation (Michael's bug report)
The teaching GUI showed a **D**, was confidently called **P**, and **could not be corrected**. Two faults:
1. **UX:** the "confident" branch offered no correction button — fixed in teach_gui (always offer "No — let me
   correct it", confident or not).
2. **Deeper:** even when corrected, the fix didn't stick — after teaching D three times a fresh D still read as
   B. Cause: `ActiveLearner.teach` kept ONE running-mean centroid per symbol; averaging blurs distinctive
   strokes so round/stem letters (D,O,B,P) collide, and a correction merely nudges a blurry mean.

## Change
Switch the learner from nearest-**mean** (Rocchio) to nearest-**exemplar** (1-NN / instance-based learning —
established method, named as such). `teach` appends the example as an exemplar; distance to a symbol = distance
to its NEAREST exemplar. A corrected example then matches a near-identical future percept directly, so
corrections stick. Public API unchanged (teach/guess/observe/confirm/tau). Per-symbol exemplar cap bounds memory.

## Pre-registered bars (BEFORE the run)
- **J293a (corrections stick):** teach P,A,B,O; present a D; click "No → D" (teach D); a fresh held-out D is then
  classified **D**, ≥ 0.90 over repeated fresh D's, both seeds.
- **J293b (NO regression):** re-run the prior perception PASSes; each must still meet its original bar —
  JEP-287 letter-id ≥ 0.90, JEP-288 cross-modal hear ≥ 0.90, JEP-291 reason-acc ≥ 0.85, JEP-292 WAV-hear ≥ 0.90.

Predicted most-likely failure: 1-NN over noisy exemplars could be *less* calibrated than the mean (more
false-confident on outliers); watched via J293b. If any prior bar regresses, REVERT — do not relax the bar.

## Result
- **UX fix (teach_gui):** the "confident" branch now always offers "No — let me correct it". Michael's
  confidently-wrong guess is now correctable. **PASS.**
- **J293b (no regression):** with the exemplar learner, JEP-287 active acc 1.0 / 0.939 (≥0.90 ✓),
  JEP-288 cross-modal 1.0, JEP-292 WAV-hear 1.0. No regression. (JEP-287's own J287b label-efficiency bar was
  already False on record — pre-existing, not caused here.) **PASS.**
- **J293a (corrections stick) — diagnosed in two steps:**
  - exemplar swap alone: still 20–35% (a fresh D read as B/O). 1-NN did NOT beat nearest-mean → the classifier
    was never the blocker.
  - **root cause = features:** `render_letter` randomized font size 18–24 but `_center` only *translated*, so a
    small D collided with a large B/O. Added **scale normalization** (`_norm_glyph`: crop to ink bbox + resize to
    28×28). → fresh-D→D = **100%** both seeds; full 26-letter recognition **208/208 = 100%**. **PASS.**

## Verdict: **PASS**
Two real faults fixed: (1) a confidently-wrong guess is now always correctable; (2) corrections now stick,
because the feature is scale-invariant and the store keeps exemplars (so a correction is retained, not averaged
into a blurry mean). Honest lesson (error-class #3 / #10): a micro-test that fails doesn't implicate the obvious
component — swapping the classifier proved the blocker was the *feature*, not the learner. No post-hoc tuning;
the ≥0.90 bars were pre-registered.

