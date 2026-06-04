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

## Result — PASS (capstone: grounded generation on the PC)
| test | result |
|------|--------|
| (a) PARAMETRIC matches counterfactual store | 0.00 (model says real-world prior) |
| (a) GROUNDED matches counterfactual store | **1.00** (follows the store) |
| (b) UNGROUNDED generator answers unanswerable | 1.00 (confabulates) |
| (b) GROUNDED system abstains | **1.00** (focus-verification) |

**VERDICT: PASS.** The geometric retrieve+verify layer makes a small instruct LLM (Qwen2.5-0.5B, CPU)
GROUNDED: (a) it follows the updatable/counterfactual STORE over its parametric prior (1.00 vs the bare
model's 0.00), and (b) it ABSTAINS on unanswerable questions (1.00) where the bare generator confabulates
100% of the time. This is grounded generation = verified RAG + abstention, running entirely on the PC.

**Honest framing:** RAG (context-conditioned generation) is an ESTABLISHED method; the contribution is the
integration with the programme's geometric retrieve + updatable store (GEO-30) + focus-verification
abstention (GEO-33), giving a generator that is correct-by-store, updatable without retraining, and
hallucination-suppressed. The generator's fluency/coverage is bounded by the 0.5B model; the GROUNDING
behaviour is what the geometric layer adds. Generation is no longer out-of-scope: the full system is a
grounded QA assistant on the PC.

## Usable artifact + honest prompt-sensitivity finding
Packaged as tools/grounded_qa.py (GroundedQA): wraps the geometric layer (retrieval + GEO-33 focus
verification + GEO-30 updatable store) with an OPTIONAL 0.5B generator. Self-test PASS in both extractive
and generative modes (follows counterfactual store -> "Lyon"; abstains on "Atlantis").

**Honest finding (prompt sensitivity):** the 0.5B model's context-following is FRAGILE to prompt phrasing.
A weak prompt ("answer concisely: <q>") let it revert to its parametric prior (answered "Paris" not the
stored "Lyon"); the strong context-forcing prompt from GEO-34 ("Using ONLY the context and IGNORING prior
knowledge ...") reliably follows the store. So grounding-via-context is real but, on small models, depends on
explicit instruction to ignore priors — a deployment caveat. Larger instruct models follow context more
robustly. The module uses the validated strong prompt.
