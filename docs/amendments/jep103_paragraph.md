# JEP-103 — small natural paragraph: conjunction handling + clean pronoun rejection (boundary located)

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 ~60-75% paragraph coverage; conjunction ("Robins and sparrows are birds") and pronouns ("It is an animal")
  FAIL, locating the next boundary.

## Result — per-item prediction HIT, then fixed
Initial 3/4: conjunction mis-parsed into one garbage concept ("robins and sparrow"); pronoun "It" became a
meaningless concept — exactly as predicted. FIXES: (1) split conjoined subjects "X and Y are Z" -> X->Z, Y->Z;
(2) REJECT pronoun subjects (return 'none') rather than guess — coreference is a later tier. After fix: paragraph
comprehension 4/4 ("is a sparrow a bird" -> True; "It is an animal" -> cleanly rejected, no garbage). All 14 tests
gated green. CALIBRATION: prediction HIT (tally 10/15). HONEST BOUNDARY now: pronoun COREFERENCE (the engine
rejects pronouns instead of resolving them — needs discourse context, a later tier), relative clauses, and richer
syntax. Established (conjunction splitting, pronoun stop-list), named; no novelty. This pushes the natural-input
boundary outward one more controlled step while staying 100% on what it accepts.
