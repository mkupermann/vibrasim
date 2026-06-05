# Pattern: the recurring prediction-error classes (synthesis of the predict-calibrate log, JEP-92..180)

Michael's directive was "make the prediction become 100% correct eventually." The honest synthesis: predictions
converge WITHIN a settled domain, and a small set of RECURRING error classes account for almost every miss. Naming
them is the transferable output of the discipline — anticipate these proactively and the miss doesn't recur. (Tally
~70/96; the one forbidden outcome — repeating a *diagnosed* mistake — was avoided except for two bug-families now
structurally guarded.)

## The error classes (each with the lesson that prevents recurrence)

1. **Surface-form bugs are a CLASS, not incidents** (JEP-92/94/95/100/119). Articles (a/an is PHONETIC not
   orthographic), plurals (incl. irregular -ves/-ses/-us/-is over-stripping), verb agreement, underscore/space.
   LESSON: fix a surface-form bug in EVERY parser/regex + grep to confirm; one-path fix is not a fix. The a/an
   alternation recurred 6× before a structural guard (mandatory `(?:(?:an|a|the)\s+)?` form) stopped it.

2. **In-sample reconstruction ≠ held-out generalization** (JEP-176). An embedding can reconstruct a structure it was
   trained on even when small; the scale caveat (needs ≥N) applies to HELD-OUT generalization. State which you mean.

3. **A metric must DISCRIMINATE the failure mode it claims to measure** (JEP-87, JEP-180). A probe where the
   "right answer" is the same across the conditions you're contrasting measures nothing (vocabulary confound;
   "is it an animal?" when both concepts are animals). Pick a discriminating probe.

4. **D-dimensional isotropic noise has magnitude σ·√D, not σ** (JEP-158, a CARDINAL repeated bug). Always scale
   injected noise by 1/√D to control its size relative to unit vectors, or it swamps the signal.

5. **Match the TEST REGIME to the predicted MECHANISM** (JEP-157). A noise-dependent effect cannot show in a
   noise-free experiment; a redundancy cure cannot show without errors to cure. Build the condition the effect needs.

6. **Predict QUALITY, not RATE** (JEP-108, JEP-155). A high match/parse RATE on hard input is a precision trap; raw
   counts look like progress while precision is near-zero. Measure precision on the real distribution.

7. **On CLEAN/controlled data, predict BUGS, not ambiguity-spreads** (JEP-159). Clean data has no ambiguity, so a
   predicted "graded difficulty" won't appear; the residual error is almost always a latent bug. Hunt the bug.

8. **A data-structure TYPE change breaks EVERY reader** (JEP-104). Grep all tests + runners + call-sites before
   predicting green after a representation change.

9. **Check a test is WELL-POSED for the STRUCTURE** before predicting an accuracy (JEP-177). Held-out generalization
   is ill-posed on a tree (no redundancy); some questions can't be answered by the structure you built.

10. **Don't carry intuition ACROSS representations** (JEP-158). Symbolic compounding intuition (independent edges →
    exponential decay) is wrong for continuous reps (independent errors average, √k). Measure per representation.

11. **Defeasible/general rules must SURVIVE exceptions** (JEP-105), and **redundancy is a RECALL tool, not a
    precision tool** (JEP-139). Know what a mechanism buys before predicting it fixes the other thing.

12. **PROCESS: never commit without gating on a green test run** (JEP-98). The one process error that committed a
    failing test; now every commit is `pytest ... && GREEN && { commit; push }`.

## The meta-lesson
Calibration converges where the domain is understood; it CANNOT be 100% on genuinely novel experiments — that is
where the information is, and a miss there is a DISCOVERY (each row above came from a miss that became a checkable
rule). The discipline's value is not perfection-on-novelty but CALIBRATED UNCERTAINTY plus the guarantee that no
diagnosed lesson recurs. Established practice (forecasting calibration, post-mortems); named; the synthesis is the
reusable artifact.
