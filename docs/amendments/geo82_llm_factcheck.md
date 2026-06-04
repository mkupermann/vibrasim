# GEO-82 — LLM-prior fact-checking of stored facts (and its tension with updatability)

## Motivation
GEO-81: the residual GIGO is a single WRONG fact (no conflicting correct one) — conflict detection can't catch
it. Idea: use the LLM's PRIOR to sanity-check stored facts (if the store contradicts the LLM's confident
belief, flag it). GEO-82 tests whether this catches injected errors — and maps its inherent TENSION with
updatability (GEO-30): it would also flag LEGITIMATE counterfactual updates, and cannot check PRIVATE facts.

## Pre-registration (locked BEFORE run)
- Three fact types: (a) CORRECT well-known (France->Paris), (b) WRONG well-known (France->Lyon, an error),
  (c) PRIVATE (Alice->Acme, LLM has no prior).
- Check: ask the 0.5B LLM the question (no context); if its answer disagrees with the stored answer, FLAG.
- Metrics: (a) correct facts NOT flagged, (b) wrong facts FLAGGED (catches errors), (c) private facts behavior
  (LLM can't check -> likely flags or random).
- Bars (characterization): if wrong-flagged high AND correct-not-flagged high, LLM-prior catches errors on
  KNOWN facts; but if private facts also get flagged, it breaks updatability/private-fact use. Honest tradeoff map.
