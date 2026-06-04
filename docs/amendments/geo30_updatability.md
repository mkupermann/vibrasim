# GEO-30 — Practical edge: grounded UPDATABILITY under contradiction with the LLM prior

## Motivation
A frozen LLM answers from stale parametric memory; you cannot cheaply update a fact it learned. A grounded
geometric retrieval layer answers from an explicit STORE, so updating a fact = editing one store entry.
GEO-30 tests the concrete advantage: when the store holds facts that CONTRADICT common/LLM-prior knowledge,
does retrieval return the STORED answer (correct-per-store) rather than the prior? This is a real,
demonstrable benefit over using the LLM's knowledge directly.

## Pre-registration (locked BEFORE run)
- 12 "updated" facts that contradict well-known priors, e.g. "The capital of France is Lyon." (counterfactual
  store). Distinct cities, all in-store.
- Questions: "What is the capital of <country>?" Correct answer = the STORED (counterfactual) city.
- Method: geometric retrieval over the store -> read the stored object.
- Metric: fraction returning the STORED answer (not the real-world prior). Bar: >= 0.9 (the store overrides
  the prior because retrieval is grounded in the store text, not parametric memory).
- Control: a "prior" baseline that ignores the store and answers the real capital scores 0.0 on the stored
  target (confirming the questions genuinely contradict the prior).
- Also: update ONE fact at runtime and confirm the answer changes (updatability demo).

PASS if grounded retrieval returns stored answers >= 0.9 and a runtime edit flips the answer.
