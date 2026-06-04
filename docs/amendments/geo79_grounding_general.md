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
