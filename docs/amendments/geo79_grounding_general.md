# GEO-79 — Does grounding improve the small LLM on GENERAL-knowledge questions?

## Motivation
GEO-34 showed grounding helps on PRIVATE/counterfactual facts. The standard RAG value is reducing errors on
GENERAL knowledge the model half-knows. GEO-79 tests whether grounding a 0.5B model with a retrieved correct
fact improves accuracy on less-common factual questions where small models often err.

## Pre-registration (locked BEFORE run)
- ~12 less-common but real factual questions (capitals of smaller countries, specific facts) where a 0.5B
  model may be unreliable. Each with a stored CORRECT fact.
- (a) BARE 0.5B: answer from parametric memory. (b) GROUNDED: retrieve the correct fact -> answer from it.
- Metric: accuracy (answer contains the correct entity). Bar: grounded >= 0.8 AND grounded > bare by >= 0.2.
  PASS = grounding reduces small-model errors on general knowledge (standard RAG value). Honest either way.

## Result — PASS (strong practical value)
| system | accuracy (less-common capitals) |
|--------|----------------------------------|
| BARE 0.5B (parametric memory) | 0.17 |
| GROUNDED (retrieved fact) | **1.00** |

**VERDICT: PASS.** The bare 0.5B model is unreliable on less-common facts (0.17 — wrong on Astana,
Naypyidaw, Sucre, Dodoma...), but grounding it with the retrieved correct fact gives 1.00. Grounding
compensates massively for a small model's knowledge gaps — the standard RAG value, quantified at +0.83.
**Strong practical implication:** combined with the efficiency floor (GEO-67, a 17M embedder works), a TINY
embedder + a small 0.5B generator + the grounding layer = RELIABLE factual QA on modest hardware, where the
small generator ALONE fails (0.17). The grounding layer is what makes small-model factual QA trustworthy.
This is the concrete deployment value: you don't need a big LLM for reliable factual answers IF you ground a
small one in an explicit store. (Caveat: only as good as the store; out-of-store questions abstain, GEO-23.)
