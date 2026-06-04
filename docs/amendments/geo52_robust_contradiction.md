# GEO-52 — Robust contradiction detection via same-subject pre-filter (hardening from the demo)

## Motivation
The GEO-49 demo exposed a real miss: check_contradiction (embedding-nearest, GEO-41 0.94) matched a token-
colliding fact from a DIFFERENT subject ("Design team is based in Austin" for "Alice is on Design"). A
same-subject pre-filter (only compare against facts about the SAME entity) should fix it. GEO-52 tests the
improvement on a MIXED store (person facts + team-city facts that cause collisions).

## Pre-registration (locked BEFORE run)
- MIXED store: 12 person->team facts + 4 team->city facts (the collision source).
- Candidates: 8 contradictory (existing person, different team) + 8 consistent.
- Compare: (a) embedding-nearest check (current module) vs (b) same-subject pre-filter (only same-subject
  facts, then symbolic object compare).
- Metric: balanced accuracy. Bar: (b) >= 0.9 AND (b) > (a) (same-subject filter is more robust on mixed
  stores). If (a) already >= 0.9 (no collisions hit), report that honestly.
