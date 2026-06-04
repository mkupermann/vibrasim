# Prediction–Calibration Log (predict-calibrate skill)

Running record of pre-experiment predictions vs outcomes. A MISS is diagnosed into a checkable LESSON; repeating a
logged mistake is the one forbidden outcome. Goal: predictions converge to calibrated (reliably correct).

Running tally: hits 2 / predictions 4 (JEP-92 x3, JEP-93 x1; calibration improving — hits now come from APPLYING logged lessons).

| id | prediction (🔮 before) | outcome | hit? | lesson (don't repeat) |
|----|------------------------|---------|------|------------------------|
| JEP-92 #1 | 100%, and IF it misses it'll be a plural/article parse-drop in the TOLD facts | 89.5%; parse of told facts was fine (10/10); misses were (a) relational threshold 0.5 false-positived a 2/3-role-overlap fact, (b) ask-regex alternation matched "a" inside "an" | MISS | Predicted the wrong LOCATION. (1) VSA 3-role superposition: a query sharing 2/3 roles scores ~0.67 — require ALL roles (threshold 0.9), not 0.5. (2) Regex article alternation must be longest-first (an\|a\|the) with required whitespace, or "a" matches inside "an". |
| JEP-92 #2 | the two fixes give 100% (19/19) | 94.7%; new miss: "does the dog chase" (interrogative) didn't match stored "chases" (declarative) | MISS | Verb AGREEMENT/inflection differs between declarative storage and interrogative query. Normalize the relation token (strip 3rd-person -s) in _bind so both forms match. META: "controlled language" still has surface-form classes (articles, noun number, verb inflection) — ENUMERATE them all before predicting 100%, don't assume controlled=trivial. |
| JEP-92 #3 | 100% (19/19) after normalizing verbs AND having audited all three surface-form classes | 100% (19/19) | HIT | Applying miss #2's meta-lesson (audit every surface-form class) produced a correct prediction. Calibration working: enumerate, don't assume. |
| JEP-93 | 🔮 100% on single-connective+negation Boolean battery; most-likely miss = NOT-parsing (bare IS-A regex would grab 'not' as object) | 12/12 = 100% | HIT | Applied JEP-92's surface-form lesson: handled negation BEFORE atomic parse and enumerated connective/negation/article forms. Prediction held because the lesson was applied, not re-learned. |
