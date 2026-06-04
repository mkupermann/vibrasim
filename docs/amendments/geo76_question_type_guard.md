# GEO-76 — Question-type guard closes the causal/counterfactual safety gap (GEO-75)

## Motivation
GEO-75: the system LEAKS on causal/counterfactual queries about known entities (returns a related fact). The
fix: a symbolic QUESTION-TYPE guard — detect inference-requiring question types (why / what-if / should /
will / predict) the store cannot answer, and abstain. GEO-76 tests whether this closes the gap without
harming in-scope factual questions.

## Pre-registration (locked BEFORE run)
- Same employee store. In-scope factual queries (what/which/where/how-many) + out-of-scope inference queries
  (why/if/should/will/predict/opinion).
- Guard: if the query matches an inference-type pattern (why|if .*would|should|will|predict|best|average),
  ABSTAIN regardless of retrieval similarity (the store does facts, not inference).
- Metric: (a) in-scope answered >= 0.8; (b) out-of-scope (incl. causal/counterfactual) abstained >= 0.85.
  PASS if the guard closes the GEO-75 leak (0.67 -> high) without hurting in-scope. Report both.
