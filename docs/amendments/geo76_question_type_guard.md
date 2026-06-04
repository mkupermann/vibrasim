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

## Result — PASS (safety gap closed)
| metric | without guard (GEO-75) | with guard (GEO-76) |
|--------|------------------------|---------------------|
| in-scope answered | 1.00 | 1.00 |
| out-of-scope abstained | 0.67 | **1.00** |

**VERDICT: PASS.** A symbolic question-type guard (abstain on why/what-if/should/will/predict/average/best
patterns) closes the causal/counterfactual leak (0.67 -> 1.00) without hurting in-scope factual queries
(1.00). **Safety/honesty story COMPLETE:** the system both KNOWS its limits (factual lookup + symbolic
computation, not causal/counterfactual inference — GEO-75) and ENFORCES them (question-type guard + grounding
+ focus-verification — GEO-76/33/23). It reliably says "I don't do that" for inference queries instead of
returning a related-but-non-answering fact. **Honest caveat:** the guard is a keyword heuristic — it could
over-abstain on edge phrasings or miss novel inference forms; a robust version needs question-type
classification. But as a cheap deployment safety layer it works. Recommended pattern (not hardcoded in the
module, since which types are out-of-scope is deployment-specific).
