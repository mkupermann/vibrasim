# JEP-290 — visual READING: see a word -> recognize letters -> compose -> UNDERSTAND (per Michael: "words after letters")

Pre-registered 2026-06-05 (BEFORE the run). The developmental bridge from grounded LETTERS (JEP-287) to the prose
ENGINE (the base): the system SEES a written WORD, recognizes its LETTERS with the grounded recognizer, composes the
string, cleans up to the nearest KNOWN word, then REASONS about it via what it READ. No transformer / no pretrained.

## Method
- The learner has grounded its letters; the engine has READ a taxonomy. A word = a row of centred letter cells.
- READ a word: recognize each cell's letter -> raw string -> cleanup to nearest VOCAB word (edit distance).
- READING -> UNDERSTANDING: read 'POODLE'/'ROBIN' from pixels, then reason is_a(word, animal). Seeds 42 & 7.

## Bars (locked pre-run)
| ID | Criterion | Bar |
|----|-----------|-----|
| J290a | reads words | cleaned-to-vocab word accuracy >= 0.90 (both seeds) |
| J290b | cleanup helps (redundancy cure) | cleaned word accuracy >= raw letter-string accuracy (both seeds) |
| J290c | read THEN reason | a word read from PIXELS is then reasoned about via read prose ('POODLE'->is_a animal) (both seeds) |

## Prediction (locked BEFORE run) [predict-calibrate]
🔮 PASS: per-letter ~0.98 -> a multi-letter word has a few letter errors (raw word acc ~0.7-0.85), but word-level
CLEANUP to a small known vocabulary recovers it (~1.0) -- the same compounding/aggregation/cleanup cure as the
substrate arc, now in READING. read-then-reason works (the read word IS a concept the engine knows). Established
(template letter recognition + edit-distance lexicon cleanup + symbolic reasoning).

## RESULT (2026-06-05): PASS — the engine READS words from pixels and UNDERSTANDS them
| seed | raw letter-string word acc | cleaned-to-vocab word acc | read+reason | demo |
|------|----------------------------|---------------------------|-------------|------|
| 42 | 0.75 | 1.00 | True | saw 'DOG' -> read 'OUG' -> 'DOG' |
| 7  | 0.797 | 1.00 | True | saw 'DOG' -> read 'DUG' -> 'DOG' |

- **J290a ✓** — reads words at 1.00 after vocab cleanup. **J290b ✓** — cleanup RECOVERS per-letter errors (raw 0.75-0.80
  -> cleaned 1.00): the redundancy/cleanup cure (JEP-138/241) in reading -- a known-word lexicon error-corrects noisy
  letter recognition, exactly as the engine's compounding/aggregation insight predicts. **J290c ✓** — a word read from
  PIXELS ('saw DOG -> read OUG -> cleaned DOG') is then reasoned about via read prose.

**FINDING (the perception thread, the developmental ladder per Michael):** JEP-286 (perceive real images + reason) ->
287 (slow ask-when-unsure TEACHER loop + GUI) -> 288 (hear<->write cross-modal) -> 289 (teacher-grounded perception ->
reasoning) -> 290 (LETTERS -> WORDS -> understanding). The system now perceives the world via senses (sight + sound),
grounds symbols from a human teacher (querying only when unsure), READS written words from raw pixels (with lexicon
cleanup error-correcting the letters), and UNDERSTANDS them via what it READ -- the full developmental arc letters ->
words -> meaning, no transformer / no pretrained model. The symbol-grounding gap (a long-mapped frontier) now has a
working, demonstrated, teacher-in-the-loop loop. HONEST scope: prototype/template perception is coarse, audio is
synthesized, the vocabulary is small; the contribution is the demonstrated developmental loop, ready to scale.
predict-calibrate HIT (tally 169/205). Established (template recognition, lexicon cleanup, active learning, symbolic
reasoning), named; no novelty -- the value is the working perceive->read->understand ladder with a teacher in it.
