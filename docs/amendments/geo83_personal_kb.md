# GEO-83 — Realistic personal knowledge base (the actual use case)

## Motivation
The user wanted a learning+understanding method "on my PC". GEO-83 validates the system on a realistic MIXED
personal KB — contacts (role/company), tasks (due dates), notes — and realistic personal queries spanning
factoid, temporal, semantic, and aggregation, to confirm the toolkit serves the actual personal-use scenario.

## Pre-registration (locked BEFORE run)
- Mini personal KB: 6 contacts (name/role/company), 5 tasks (description/due-year/owner), 4 notes (topic/text).
- Queries (10, mixed): factoid ("what company is X at?"), temporal ("which tasks are due in 2025?"),
  semantic ("which note is about the budget?"), aggregation ("how many tasks does X own?"), abstain
  (out-of-KB).
- Metric: per-type accuracy + overall. Bar: overall >= 0.8 with abstain correct on out-of-KB. PASS validates
  the personal-use scenario.
