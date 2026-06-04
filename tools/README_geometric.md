# Geometric reasoning tools — usage guide

A grounded reasoning + QA assistant for your own facts, on the PC (CPU). Built and validated in the EQMOD-3
geometric programme (GEO-1..39). It does NOT replace an LLM — it is a grounded, updatable, hallucination-
suppressed reasoning layer ON an embedding model, optionally feeding a small generator.

See `docs/GEOMETRIC_ANSWER.md` for what it is, what it can't do, and the evidence. Honest summary: genuine
semantic matching / zero-shot transfer (model- and domain-robust), grounded abstention, multi-hop, and
grounded generation — NOT open-domain NLU, and named-entity retrieval alone is lexically solvable.

## Install
```
pip install sentence-transformers numpy          # core (extractive, retrieval, reasoning)
pip install transformers torch                    # only for grounded GENERATION
```
First run downloads the models (all-MiniLM-L6-v2 ~90MB; Qwen2.5-0.5B-Instruct ~1GB if generate=True).

## Quick start — reasoning layer (no generator)
```python
from tools.geometric_reasoner import GeometricReasoner
r = GeometricReasoner(abstain_tau=0.40)
r.add_fact("Alice works at Acme.", subject="Alice", relation="works_at", object="Acme")
r.add_fact("Acme is in Boston.",   subject="Acme",  object="Boston")

r.ask("Where does Alice work?")                       # grounded answer or "I don't know"
r.chain(["What company does Alice work at?",          # multi-hop
         "What city is {bridge} in?"])
r.count_where(lambda m: m.get("object") == "Boston")  # symbolic aggregate
r.calibrate_abstention(answerable_qs, unanswerable_qs)  # tune the abstain threshold (recommended)
```

## Quick start — grounded QA assistant (optional generator)
```python
from tools.grounded_qa import GroundedQA
qa = GroundedQA(generate=True)                         # set False for extractive (returns the fact text)
qa.add_fact("The capital of France is Lyon.", focus_value="France", subject="France", object="Lyon")
qa.answer("What is the capital of France?", focus="France")     # -> follows YOUR store ("Lyon"), not the LLM's prior
qa.answer("What is the capital of Atlantis?", focus="Atlantis") # -> "I don't know." (focus not in store)
```
`focus=` enables the answerability check (GEO-33) that abstains on in-domain-but-unanswerable questions.

## Recommended settings (from the experiments)
- Embedding model: `all-mpnet-base-v2` for quality (GEO-36: cleaner), `all-MiniLM-L6-v2` for speed.
- Always `calibrate_abstention()` on a small labelled dev set — a guessed threshold is unreliable (GEO-32).
- Generation needs the faithfulness instruction (built into GroundedQA) or the small model invents details
  (GEO-38) and can revert to its prior (GEO-34); larger instruct models follow context more robustly.
- Operating envelope: a few hundred facts / 2-3 hops on CPU (GEO-22). Beyond that, add an ANN index + a
  cross-encoder re-ranker.

## What it gives you that a raw LLM doesn't
Grounded (abstains instead of confabulating), updatable (edit one fact, no retraining), auditable (you see
the supporting fact), and able to reason over YOUR private facts the LLM never saw — validated end-to-end
(GEO-39, 5/5).
