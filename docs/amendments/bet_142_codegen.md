# BET-142 — Can a non-LLM system give a NEW combination of code?

Pre-registered: 2026-05-31 (BEFORE the run). Michael's question: if it learns a
programming language, can it answer with a NEW combination of code? Tests the honest
boundary between RETRIEVAL (returns seen snippets — cannot) and COMPOSITION
(recombines learned fragments — can, within limits).

Method: the system learns atomic code FRAGMENTS of a small Python DSL (maps: square,
cube, double, increment; filters: positive, even, odd, negative; reducers: sum, max,
min, count, average) with trigger words. A written query is parsed (keyword ->
operation) into a PIPELINE and the system EMITS composed Python. Test queries request
compositions NEVER shown as a whole (e.g. "sum of the squares of the positive
numbers"). The generated code is EXECUTED on sample inputs and compared to an
independent reference. A generated function counts as a NEW combination if its pipeline
chains more than a single bare reducer.

## Bars (locked pre-run)
| ID | Criterion | Bar |
|----|-----------|-----|
| T142a | Code runs | >= 0.90 of generated functions execute without error |
| T142b | Code is correct | >= 0.80 produce the reference output on test inputs |
| T142c | Genuinely new combinations | >= 0.60 of correct outputs chain multiple ops (not taught whole) |
| T142d | Honest ceiling shown | a query outside the DSL is NOT fabricated as valid code |

PASS = T142a-d. PASS = the substrate-native composer produces NEW, correct code
combinations by recombining learned fragments — answering Michael's question YES, with
an explicit boundary (it recombines a learned DSL; it does not invent algorithms
outside it). No LLM, no transformer. Honest provenance: rule/grammar-based program
synthesis (decades old).

## RESULT (2026-05-31): PASS — yes, NEW correct combinations, with an honest ceiling

| metric | value | bar |
|--------|-------|-----|
| generated functions that run | 10/10 | T142a >=0.90 ✓ |
| correct vs reference (executed on 5 inputs) | 10/10 | T142b >=0.80 ✓ |
| correct outputs that chain multiple ops (new combos) | 10/10 | T142c >=0.60 ✓ |
| out-of-DSL request fabricated as valid? | No | T142d ✓ |

PASS. Example: "the sum of the squares of the positive numbers" — never taught as a
whole — produced and verified:

```python
def f(xs):
    xs = [x for x in xs if x > 0]
    xs = [x * x for x in xs]
    return sum(xs)
```

Answer to the question: YES, a non-LLM system CAN give a new combination of code — by
recombining learned fragments into pipelines it was never shown whole, and here every
one executes correctly. The CEILING is explicit and honest: a request needing
operations outside the learned DSL ("median with a custom comparator") yields NOTHING
rather than a confident fabrication — the opposite failure mode to an LLM. To extend
the reach you TEACH more fragments; it then recombines those too. Provenance:
rule/grammar-based program synthesis (decades old), no LLM/transformer.
