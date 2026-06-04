# GEO-65 — Ambiguous reference handling (surface candidates, don't silently pick one)

## Motivation
Real queries reference entities ambiguously ("Smith" when several people share that surname). A trustworthy
system should SURFACE the candidates (or ask to disambiguate), not silently answer for one. GEO-65 tests
ambiguity detection: when a query's entity descriptor matches multiple stored entities, flag AMBIGUOUS and
return the candidate set.

## Pre-registration (locked BEFORE run)
- 12 people, some sharing a surname (Smith x3, Lee x2) and some unique. Facts carry full name + surname.
- Reference query uses a surname; resolver gathers all entities with that surname.
- Detection: >1 match -> AMBIGUOUS (return candidates); 1 match -> resolve; 0 -> not found.
- 8 reference queries (4 ambiguous surnames, 4 unique). Metric: balanced accuracy of ambiguity detection.
  Bar: >= 0.9. Compare to naive (silently returns nearest one, 0 ambiguity awareness).

## Result — PASS
ambiguity detection balanced-acc = **1.00**. 'Smith' -> AMBIGUOUS [John/Mary/Peter Smith]; 'Khan' -> OK [Carol Khan].

**VERDICT: PASS.** A surname matching >1 stored entity is flagged AMBIGUOUS with the candidate set, instead of
silently answering for one. Purely symbolic (group-by attribute, flag if >1).

## Trustworthiness suite — consolidated (honest note)
The system's "trustworthy answering" features are all instances of geometry-RESOLVES + symbol-CHECKS, and all
score exactly 1.00 because they are exact SET LOGIC over the structured store:
- ABSTENTION — don't answer the ungrounded (GEO-23/33).
- CONTRADICTION — flag conflicting writes (GEO-41/52).
- CONFLICT — surface inconsistent stored facts at query time (GEO-62).
- AMBIGUITY — surface multiple matches for a reference (GEO-65).
Together: the system never silently guesses — it abstains, flags conflicts, and surfaces ambiguity. Honest
note: these symbolic checks are PREDICTABLE 1.00s (set logic), not uncertain findings; the genuinely-uncertain
results are the GEOMETRIC ones (semantic matching, zero-shot transfer, prose retrieval), which carry the real
boundaries. The trustworthiness suite is a completeness feature, not a research surprise.
