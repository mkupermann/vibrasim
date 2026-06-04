# JEP-125 — parser robustness fuzz test (the engine must never crash on bad input)

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 no crashes across thousands of random/malformed/adversarial strings to tell()/respond()/describe() — OR a
  crash is found (valuable; the Boole data already found one, the data-as-regex-replacement bug). MOST-LIKELY MISS:
  a crash on special chars / empty / pathological input.

## Acceptance
- PASS: 0 crashes (every input handled cleanly, returning a value or 'none'/'I cannot parse'). Any crash is a found
  bug to fix. Established (fuzz testing), named; no novelty.

## Result — PASS (HIT)
0 crashes across 8000 random/malformed/adversarial inputs x 3 entry points (tell/respond/describe), INCLUDING the
backslash/regex-special inputs (r"\x", r"\1", r"\g<0>", "\\") that would trigger the data-as-regex-replacement
crash the Boole data found (JEP-108) — confirming that bug is fixed. Bad input is handled cleanly (parsed, ignored,
or 'none'), never an exception. Prediction HIT; tally 24/39. With JEP-124 (soundness), the engine is now validated
SOUND and ROBUST. A compact fuzz test is locked into the suite. Established (fuzz testing), named; no novelty.
