# GEO-34 — Grounded GENERATION: the geometric layer makes an LLM generator follow the store + abstain

## Motivation
Generation was the one out-of-scope frontier. The user allows LLM, and a small instruct model
(Qwen2.5-0.5B-Instruct) runs on this CPU (~0.5s/gen). GEO-34 tests the capstone synthesis: does the
geometric retrieve+verify layer (GEO-30 updatable store + GEO-33 answerability) make a generative LLM
GROUNDED — i.e., (a) follow the STORE over its parametric prior (answer updated/counterfactual facts), and
(b) ABSTAIN instead of confabulating on unanswerable questions? This is geometry+LLM as grounded generation,
the genuinely useful combination (RAG with verified retrieval + abstention), all on the PC.

## Pre-registration (locked BEFORE run)
- 12 COUNTERFACTUAL capital facts (contradict the model's prior), stored in the GeometricReasoner.
- (a) Counterfactual following: for each, compare
  - PARAMETRIC: model answers "capital of <country>?" with NO context.
  - GROUNDED: geometric layer retrieves the stored fact -> put in context -> model answers.
  Metric: fraction matching the STORED (counterfactual) city. Bar: grounded >= 0.8 AND parametric <= 0.2
  (grounding overrides the prior; the model alone gives the real-world answer).
- (b) Hallucination control: 6 UNANSWERABLE questions (focus absent from store). Compare
  - UNGROUNDED generator: answers anyway (confabulates).
  - GROUNDED system: focus-verification (GEO-33) -> abstain ("I don't know"), no generation.
  Metric: grounded abstains >= 0.8; ungrounded confabulates (answers) on most. Bar: grounded abstains >= 0.8
  AND ungrounded answers >= 0.5 (shows grounding prevents confabulation the bare LLM commits).

PASS if (a) grounding overrides prior AND (b) grounding prevents confabulation. NULL/PARTIAL otherwise.
