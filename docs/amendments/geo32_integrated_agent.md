# GEO-32 — Capstone: integrated grounded QA agent on a realistic mini-KB (dogfoods GeometricReasoner)

## Motivation
Each capability was shown in isolation. GEO-32 runs them TOGETHER as one usable agent on a coherent mini
knowledge base, using the packaged tools/geometric_reasoner.py (so the module is proven usable, not just the
experiments). Measures: semantic (non-lexical) Q, multi-hop, abstention on out-of-KB Q, symbolic
aggregation, and runtime update — end to end.

## Pre-registration (locked BEFORE run)
- Mini-KB: a small company domain — ~10 employees (role + team + city facts), giving ~30 facts.
- Test set (locked): (a) 5 semantic questions using ROLE descriptions not names (non-lexical); (b) 3
  multi-hop (person->team->city); (c) 3 out-of-KB questions that must ABSTAIN; (d) 2 aggregation counts;
  (e) 1 runtime update then re-query.
- Metric: per-category accuracy + overall. Bars: semantic >=0.6, multi-hop >=0.6, abstain >=0.8, aggregate
  exact, update flips. PASS if all categories meet bars (the integrated agent works on a realistic task).
- Honest: this reuses small clean entities; it demonstrates the system integrates + is usable, not scale.
