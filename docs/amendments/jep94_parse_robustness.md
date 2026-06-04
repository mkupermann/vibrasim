# JEP-94 — engine tier 3: parse robustness (attacking the real gate, gradually, at 100%)

## Why
The whole arc found the PARSE is the gate to real-text understanding (JEP-89). Per Michael's "100% engine first,
scale gradually", widen the phrasings the engine accepts for the SAME IS-A facts — plurals, "is a kind of",
universal quantifiers — while HOLDING 100%. Disciplined, incremental scaling of the bottleneck.

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 100%: varied phrasings ("Poodles are dogs", "A poodle is a kind of dog", "Every poodle is a dog", "Dogs are
  animals") all extract the same IS-A as the canonical form, comprehension stays 100%. MOST-LIKELY MISS:
  "kind of"/"type of" leaving "kind"/"type" as the object, or a quantifier captured as subject (surface-form
  class from the log). Mitigated by preprocessing (strip quantifiers, collapse 'a kind/type/sort of') BEFORE the
  IS-A regex, and _norm for plurals. Enumerated. Predict 100%.

## Acceptance
- PASS: every varied phrasing yields the correct IS-A graph AND comprehension (incl multi-hop) = 100%.
- Established (pattern normalization), named; no novelty. Honest: still a closed set of phrasings — full open-prose
  parse (JEP-89) remains the frontier; this scales the boundary outward by one controlled tier.

## Calibration (after) — a REPEATED mistake, owned (the discipline's hardest case)
🔮 predicted 100% with "kind-of/quantifier" as the most-likely miss. ACTUAL 87.5% — and the miss was NOT what I
predicted: "Dogs are animals" parsed the object as "nimal". That is the SAME article-alternation bug as JEP-92 #1
(the optional article ate the leading "a" of "animals"). I had fixed it in ask() but NEVER propagated the fix to
the _ISA regex. This is a "mistake made twice" — exactly what the rule forbids — caused by fixing a surface-form
bug in ONE parser instead of ALL of them.
- META-LESSON (now logged): when a surface-form/parse bug is found, fix it in EVERY parser/regex in the module and
  grep to confirm; a fix in one code path is not a fix. Re-run after propagating: 16/16 = 100% (HIT).

## Result — PASS (100%)
Parse-robustness battery 16/16 = 100%. Varied phrasings ("Poodles are dogs", "A poodle is a kind of dog", "Every
poodle is a dog", "Dogs are animals", "Dogs are a type of animal", "All animals are living_things") all yield the
correct IS-A structure and comprehension (incl multi-hop). Audit confirmed: all article slots now require a
trailing space (longest-first an|a|the), so a noun's leading "a"/"an" is never mistaken for an article. Regression
suite green. HONEST: still a closed set of phrasings; open-prose parse (JEP-89) remains the frontier — this scaled
the boundary outward one controlled tier. Established (pattern normalization), named; no novelty.
