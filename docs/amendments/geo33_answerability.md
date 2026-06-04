# GEO-33 — Answerability via FOCUS-TERM verification (does the question's focus exist in the store?)

## Motivation
GEO-32b: threshold abstention can't reject in-domain-but-unanswerable questions ("Who is the CEO?" when no
CEO is stored). Principled fix: verify the question's FOCUS (the role/entity asked about) actually exists as
a value in the structured store before answering. This is a hybrid — geometric focus-matching + a symbolic
existence check over the store's meta — not a similarity threshold. GEO-33 tests if it separates answerable
from in-domain-unanswerable cleanly.

## Pre-registration (locked BEFORE run)
- Same employee KB (roles stored as meta).
- Questions of form "Who is the <FOCUS>?" where FOCUS is a role. Answerable focuses (stored roles: data
  scientist, backend engineer, UX designer, SRE, product manager) and UNANSWERABLE focuses (CEO, CTO,
  janitor, lawyer, chef) not in the store.
- Verification: extract focus, compute max cosine of focus vs the SET of stored role values; answer only if
  max >= tau_focus (focus exists), else abstain. Calibrate tau_focus on a dev split of stored vs absent roles.
- Metric: balanced accuracy separating answerable (stored role) vs unanswerable (absent role). Bar: >= 0.8.
  Compare to the GEO-32b plain-similarity baseline (which fails this).

PASS if focus-verification cleanly rejects absent-role questions while accepting stored-role ones (>=0.8).
NULL if absent roles (CEO/CTO) are too close to stored roles to separate — an honest boundary.
