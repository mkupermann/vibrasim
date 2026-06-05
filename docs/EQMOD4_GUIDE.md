# EQMOD-4 (JEPA / EBM / MPC) — user-facing guide

What was built, how to use it, and the honest bounds. Full rung-by-rung log: `docs/JEPA_PROGRAMME_SUMMARY.md`
(JEP-1..50). Reusable lessons: `docs/patterns/`. This guide is the practical entry point.

## What this is
Michael's directive: pursue Model-Predictive Control + Energy-Based Models in joint-embedding (JEPA), toward
human-level understanding. The result is a set of working, tested demonstrations that build and COMPOSE the
structured *building blocks* of understanding - perception, world models, planning, and conceptual reasoning -
all from established methods (named throughout), validated on real data. It is NOT human-level understanding;
the frontier is left open and honestly drawn.

## The usable deliverables

### 0. The Understanding Engine — `world/understanding.py` (the headline deliverable)
A 100%-working, substrate-legal (NO transformer, NO LLM, NO pretrained model) engine that does all three of
Michael's verbs — human-like LEARNING, UNDERSTANDING, and COMMUNICATING — and now does them END TO END from PROSE.
Built bottom-up across JEP-92..170, 53 gated regression tests, the predict-calibrate discipline (62/86, every miss
diagnosed). The closed loop:
- **LEARN FROM PROSE** — `e.read(passage)` extracts is-a + part-of + causal + spatial-containment from an
  encyclopedic-register passage via classic Hearst-style patterns + a bare-NP guard + recency coreference + negation
  (belief revision). ~0.90 recall / high precision on connected prose; domain-general (biology/geography/technology).
- **UNDERSTAND** — multi-hop deduction over a multi-parent DAG, Boolean AND/OR/NOT, three-valued Yes/No/I-don't-know,
  quantification, comparison, analogy, hypothetical, causal + intervention (do-operator), probabilistic, temporal,
  provenance/TMS, spatial frames, mereology — and RELATION-TYPE INTERACTIONS with correct distinct semantics (a
  dog's heart is part of an animal; smoking causes a disease; but a dog's heart is NOT part of a cat).
- **COMMUNICATE** — conversational Q&A across is-a/part-of/causal, multi-relation English profiles (`describe`),
  explanations of the reasoning chain, learning-through-dialogue, belief revision when a source corrects it.
Full guide: `docs/UNDERSTANDING_ENGINE.md`; demos: `python tools/demo_learn_from_prose.py` and
`tools/demo_full_conversation.py`. HONEST scope: works on encyclopedic/descriptive prose; the named frontier is
DENSE logic/argument prose (Boole ~2%, the GENRE not the extractor — JEP-155/156), a real encyclopedic corpus at
scale (needs the long tail of NL constructions, the no-transformer wall), abstract words, open generation, and rich
grounding (symbol-grounding). The engine is the foundation to scale FROM, NOT human-level understanding.

### 1. Concept reasoner — `tools/concept_reasoner.py`
A mixed-curvature reasoner over any taxonomy (parent->children dict): Euclidean for RELATEDNESS, hyperbolic /
order embeddings for IS-A. No pretrained models.
```python
from tools.concept_reasoner import ConceptReasoner
cr = ConceptReasoner(tax).fit(isa_method="poincare")   # or "order"
cr.is_a("cat", "mammal")     # True
cr.nearest("cat", k=3)       # taxonomic neighbours
cr.relatedness("cat", "dog") # higher = more related
```
- Choose `isa_method` BY USE CASE (not benchmark accuracy - JEP-46/47):
  - `"order"` (Vendrov 2016): best for IS-A CLASSIFICATION on large/irregular real hierarchies (0.91 on WordNet).
  - `"poincare"` (default): best for GROUNDING/planning (cross-branch precision) and clean/shallow taxonomies.
- Honest bounds: per-query is-a is ~0.86-0.91 (a minority wrong); poincare has a sibling residual, order a
  cross-branch residual; entailment cones (`tools/run_jep39*`) fix both on SMALL clean trees but don't scale.
  Full guidance: `tools/README_concept_reasoner.md`. Tests: `pytest tests/test_concept_reasoner.py`.

### 2. Substrate-native world-model agent (demos in `tools/run_jep*`)
A backprop-free agent: perception (denoise/discriminate) -> world model (Successor Representation learned by
local TD = the substrate's BTSP) -> value/MPC planning -> adaptation. Robust to stochastic transitions.
- Capstone integrated agent: `tools/run_jep16_integrated.py`.
- Concept-grounded planning ("reach a carnivore"): `tools/run_jep34_abstract_goal.py` (single),
  `run_jep35` (logical AND/OR/NOT), `run_jep36` (sequential). Uses `isa_method="poincare"` for grounding.

## Your hardware (AMD GPU) — `docs/AMD_GPU_COMPUTE.md`
- GPU TRAINING works via `torch-directml` on Python 3.11 (`.venv-dml311`): normal PyTorch, `torch_directml.device()`.
  Beats the 16-thread CPU 2.5-6x on large workloads; slower on small ones. GPU inference also via onnxruntime-directml.
- Run GPU code with `.venv-dml311/Scripts/python.exe`; CPU/main work with `.venv/Scripts/python.exe`.

## The headline findings (honest)
- The substrate's primitives ARE the backprop-free versions of JEPA/EBM/MPC: EBM inference = relaxation, learning
  = local plasticity (predictive coding matches backprop on MNIST/Fashion at depth).
- Conceptual reasoning needs the right GEOMETRY: metric relations -> Euclidean, taxonomic (IS-A) -> hyperbolic /
  order embeddings (JEP-23/42).
- Composition works in the reliable regime but INHERITS component error-patterns - higher benchmark accuracy can
  mean worse task performance (JEP-46). Measure on YOUR task's distribution.
- LEARN-FROM-SOURCES: the real-prose parse gate is the GENRE, not the extractor (JEP-155/156) — encyclopedic prose
  yields ~0.90-recall taxonomy with classic Hearst+NP-chunking; dense logic/argument prose (Boole) yields almost
  none. The engine learns multi-relation structure from a passage and reasons multi-hop over it, no transformer.
- THE COMPOUNDING / AGGREGATION INSIGHT (the deepest finding, JEP-134..158): multi-step inference COMPOUNDS errors;
  the cure is REDUNDANT AGGREGATION, not deeper chains. The compounding EXPONENT is representation-dependent —
  symbolic-independent edges decay exponentially, continuous-distributed reps AVERAGE independent noise (sqrt-k,
  a concrete reason learned representations help), systematic bias accumulates linearly; substrate Hopfield cleanup
  cures the continuous cases. One principle across structure-learning, reasoning, and learn-from-prose.

## What is NOT claimed
Human-level / open conceptual understanding; any novelty (all methods established and named); a single best is-a
method (use-case-dependent). The open frontier: language grounding, multi-parent (DAG) reasoning, convergent-
scale learning. ~50 rungs, NULLs as findings, ~17 self-corrections - the discipline (measure before claiming) is
the transferable output. See `docs/patterns/honest_evaluation.md` and `docs/patterns/grounding.md` (concept formation -> reason -> act), and `docs/patterns/compositional_cognition.md` (set/relational/recursive composition toward human-level structured thought).
