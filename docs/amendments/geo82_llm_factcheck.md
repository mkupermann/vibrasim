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

## Result — TRADEOFF MAP
| stored fact type | LLM-prior flags it | interpretation |
|------------------|--------------------|----------------|
| CORRECT well-known (France->Paris) | 0.20 | good — low false-positive |
| WRONG well-known (France->Lyon) | 1.00 | good — catches the error |
| PRIVATE (Zarnak project -> Building 7) | 0.80 | BAD — false-flags facts it can't verify |

**VERDICT: TRADEOFF MAP (honest).** LLM-prior fact-checking is a real error-detector for stores that SHOULD
match common knowledge (catches single wrong facts conflict-detection misses, 1.00, with low false-positives
on correct facts, 0.20). BUT it false-flags PRIVATE facts (0.80) and would flag legitimate UPDATES/counterfac-
tuals — which CONTRADICT the prior by design (GEO-30). So it is FUNDAMENTALLY INCOMPATIBLE with the system's
core strengths (updatability, private/proprietary facts). You get EITHER LLM-prior fact-checking (public-
knowledge stores) OR updatability + private facts — not both via the prior.

## Complete GIGO-mitigation map (GEO-80/81/82) — the residual risk, fully scoped
| failure | catchable by | residual? |
|---------|--------------|-----------|
| queried entity ABSENT (coverage gap) | abstention (GEO-81) | NO — caught (1.00) |
| CONFLICTING facts for one entity | conflict detection (GEO-41/62) | NO — caught |
| single WRONG fact, PUBLIC knowledge | LLM-prior fact-check (GEO-82) | NO — caught, IF store should match common knowledge |
| single WRONG fact, PRIVATE/updated | provenance / external verification ONLY | YES — no automatic check (the irreducible residual) |
**Honest bottom line:** the grounding GIGO risk is almost entirely mitigable (abstention + conflict detection
+ optional LLM-prior check for public stores). The ONE irreducible residual is a single wrong PRIVATE fact
with no conflicting fact — which no automatic mechanism can catch, only data provenance/curation. So: keep
your store clean (the system can't fully self-verify proprietary facts), and the safeguards handle the rest.
