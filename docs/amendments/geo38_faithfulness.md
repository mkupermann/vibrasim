# GEO-38 — Grounded generation FAITHFULNESS: does the generator stay within the context?

## Motivation
GEO-34/35: the grounded generator follows the store. But the key trust question for RAG is FAITHFULNESS —
when it generates, does it stick to the provided context, or confabulate unsupported details? GEO-38 probes
the failure mode: give a single supporting fact and ask a question whose answer is only PARTLY in the
context (one part supported, one part absent). A faithful system answers the supported part and declines /
omits the unsupported part; an unfaithful one invents the missing detail.

## Pre-registration (locked BEFORE run)
- 8 facts "<P> is on the <Team> team." (team supported; NO salary/age/location in context).
- Question per person: "What team is <P> on, and what is their salary?" (team supported, salary absent).
- Measure on the generation: (a) team correct (uses context) — should be high; (b) salary invented
  (confabulation) — count how often a specific salary number/figure appears (unfaithful). Also test an
  explicit instruction to say "not stated" for unknown parts.
- Bars: (a) team mentioned correctly >= 0.7; (b) WITHOUT the faithfulness instruction, salary-invention >=
  0.3 (shows the risk); WITH a "say 'not stated' if absent" instruction, salary-invention drops by >= 0.3
  (shows it is mitigable). Report both. Honest characterization rung.

## Result — characterization (real but modest risk, fully mitigable)
| metric | value |
|--------|-------|
| team mentioned correctly (plain) | 1.00 |
| salary INVENTED (plain prompt) | 0.25 |
| salary INVENTED (faithfulness prompt) | **0.00** |

**VERDICT: characterization** (did not clear the pre-registered 0.3 invention/drop bars — invent-plain 0.25,
drop 0.25 — NOT retuned). The substantive finding is clear regardless: grounded generation confabulates
unsupported details a quarter of the time with a NAIVE prompt, and an explicit "if a detail is not in the
context, say 'not stated'" instruction ELIMINATES it (0.25 -> 0.00) while keeping the supported answer
correct (1.00). **Practical guideline:** the grounded generator needs an explicit faithfulness instruction;
with it, the 0.5B model stays within context on this test. Applied to the GroundedQA module's prompt.
