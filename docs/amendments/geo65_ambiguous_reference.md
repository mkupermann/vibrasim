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
