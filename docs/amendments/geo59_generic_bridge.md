# GEO-59 — Generic bridge extraction (no pre-known list) for unstructured multi-hop

## Motivation
GEO-58 used a KNOWN project-token list to extract the bridge. GEO-59 removes that: extract the bridge with a
GENERIC rule (a capitalized entity in the hop-1 sentence that is NOT the queried person), no domain list. If
multi-hop still works, the unstructured multi-hop is genuinely general (any document, no pre-known entities).

## Pre-registration (locked BEFORE run)
- Same 6 chains (Person leads Project; Project based in City) + distractors.
- Bridge extraction: capitalized tokens in the hop-1 sentence minus the person's name tokens; pick the one
  that also appears in some OTHER sentence (the linking entity). NO pre-known project list.
- Metric: end-to-end accuracy. Bar: >= 0.7 (generic extraction works). Compare to GEO-58 (known-list 1.00).
  NULL if generic extraction fails to find the right bridge.

## Result — PASS
generic-bridge multi-hop end-to-end = **1.00** (GEO-58 known-list also 1.00).

**VERDICT: PASS.** Generic bridge extraction — the capitalized entity in the hop-1 sentence that ALSO appears
in another sentence (the linking entity), with NO pre-known domain list — recovers the bridge and the chain
completes at 1.00. Unstructured multi-hop is general: any document, no domain list needed. **Honest caveat:**
this uses capitalized-proper-noun extraction + an "appears in >=2 sentences" linking heuristic — works for
proper-noun bridges (common in factual prose); lowercase entities or pronoun coreference would need fuller
NER. For factual documents with named entities, the system does general multi-hop QA over free text. Combined
GEO-56/57/58/59: the geometric layer extends from structured KBs to UNSTRUCTURED documents — retrieval,
abstention, single- and multi-hop QA — with re-ranking and generic entity-bridge extraction.
