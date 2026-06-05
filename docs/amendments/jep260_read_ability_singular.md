# JEP-260 — read() captures 'X can/cannot VERB' + singular ability question ('can a penguin fly?')

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 QA showed 'can a penguin fly?' -> 'I cannot parse' (only the universal 'can all X fly?' was handled). Adding a
  singular handler fixes the question; investigation also showed read() never stored 'X can/cannot VERB' as
  properties (only tell() did) -> add property capture to read() too. Risk: the capture pattern must not swallow
  'a penguin is a bird that cannot fly' (the np spans spaces).

## Result — PASS (HIT), with a gated-regression self-catch
Two fixes: (1) read() now routes 'X cannot VERB'/'X can VERB' sentences to (not_)properties (it previously captured
NONE -- only tell() did, so read passages lost all ability facts); (2) respond() answers the SINGULAR 'can a X VERB?'
from properties/not_properties.
- 'A penguin cannot fly. An eagle can fly.' -> not_properties{penguin:{fly}}, properties{eagle:{fly}}.
- 'can a penguin fly?' -> 'No. A penguin cannot fly.'; 'can an eagle fly?' -> 'Yes. An eagle can fly.'; the universal
  'can all birds fly?' -> 'No - not all. For example, a penguin cannot fly.' now works too (read populates properties).
GATED-REGRESSION SELF-CATCH (the predicted risk materialized + was caught by the test gate BEFORE commit): the first
cut's np (which allows spaces) matched 'penguin is a bird that' in 'a penguin is a bird that cannot fly' and the
unconditional `continue` SWALLOWED the sentence -> is_a(penguin,bird) lost, 1 test failed. Fix: only CONSUME when the
subject is a valid bare NP (guard the continue). Re-verified green. 101/101 regression tests (+1). Prediction HIT;
tally 139/175. Established (ability/property predication, singular vs universal quantification), named; no novelty.
