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
