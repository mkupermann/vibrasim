# The Understanding Engine (`world/understanding.py`)

A small, **100%-working, substrate-legal** engine for human-like learning, understanding, and communication —
**NO transformer, NO LLM, NO pretrained model**. Built bottom-up, one tier at a time, each held at 100% with
regression tests (`tests/test_understanding_engine.py`) and the predict-calibrate discipline
(`.claude/skills/predict-calibrate`, log in `docs/PREDICTION_LOG.md`).

## What it does (the three verbs, demonstrated)
- **LEARNS** three ways: told facts ("A dog is an animal."), **correction** ("A whale is not a fish." then
  "A whale is a mammal."), and **examples shown** (form a concept prototype from a few perceptual instances).
- **UNDERSTANDS** beyond retrieval: multi-hop inference never stated (transitive closure), same-bag truth via
  role-binding (who-plays-which-role — bag-of-words can't, JEP-87), Boolean AND/OR/NOT, grounded in perception.
- **COMMUNICATES** in English: explains its reasoning, not just yes/no, with correct a/an + verb agreement.

## Usage
```python
from world.understanding import UnderstandingEngine
e = UnderstandingEngine()
e.tell("A poodle is a dog.");  e.tell("A dog is an animal.");  e.tell("An animal is a living_thing.")
e.is_a("poodle", "living_thing")            # True  (3-hop, never stated)
e.explain("is a poodle a living_thing?")    # "Yes. A poodle is a dog, a dog is an animal, an animal is a living thing."
e.tell("the dog chases the cat.")
e.relation_true("cat", "chases", "dog")     # False (same words, wrong roles)
e.ask_bool("is a poodle an animal and is a poodle not a fish")   # True
# LEARN FROM A PROSE PASSAGE (learn-from-sources, JEP-155..159) — Hearst patterns + bare-NP guard, NO transformer:
e.read("A poodle is a kind of dog. A dog is a mammal. A mammal is an animal. "
       "A heart is part of a dog. A virus causes a fever. Mammals such as dogs and cats are warm-blooded.")
e.is_a("poodle", "animal")        # True  (multi-hop, no single sentence states it)
e.part_of("heart", "dog")         # True  (part-of, kept distinct: is_a('heart','animal') is False)
e.causes_effect("virus", "fever") # True  (causal chain)
# (the gate is the GENRE: encyclopedic/descriptive prose works ~0.87 precision; dense logic prose e.g. Boole yields little)
# correction:
e.tell("A whale is a fish.");  e.tell("A whale is not a fish.");  e.tell("A whale is a mammal.")
e.explain("is a whale an animal?")          # "Yes. A whale is a mammal, a mammal is an animal."
# concept from examples:
e.learn_concept("bird", [features1, features2, ...]);  e.tell("A bird is an animal.")
e.is_a(e.perceive(new_bird_features), "animal")          # True
```

## The tiers (each 100%, pre-registered)
| tier | capability | amendment |
|------|-----------|-----------|
| 1 | parse -> ground -> bind -> infer (comprehension battery 19/19) | JEP-92 |
| 2 | Boolean AND/OR/NOT comprehension | JEP-93 |
| 3 | parse robustness (plurals, "kind of", "every/all") | JEP-94 |
| 4 | COMMUNICATE reasoning in English (explain) | JEP-95 |
| 5 | LEARN by correction (belief revision) | JEP-96 |
| 6 | LEARN a concept from examples shown | JEP-97 |
| 7 | multi-word concepts + natural-input hardening (adjectival/plural subjects) | JEP-98/99 |
| 8 | conversational WH-questions ("what is X?", "what does X do?") | JEP-100 |
| 9 | three-valued comprehension Yes/No/**I-don't-know** (epistemic humility) | JEP-101 |
| 10 | **LEARNING THROUGH DIALOGUE** — identify the gap, get taught, then know | JEP-102 |
| 11 | multi-parent DAG, induction (defeasible), generation (describe) | JEP-104/105/115 |
| 12 | conjunction, coreference, contradiction detection, quantifiers (every/all) | JEP-103/107/109/110 |
| 13 | compositional queries, **analogy**, **hypothetical/counterfactual** | JEP-119/120/121 |
| 14 | learn from OBSERVATION -> self-taught taxonomy; cross-situational naming | JEP-113/116/117 |
| 15 | learn relational composition RULES from data, reason with them | JEP-128/129/130 |
| 16 | **causal reasoning + intervention** (do-operator); **probabilistic** (noisy-OR) | JEP-141/142 |
| 17 | abduction, diagnosis, planning; temporal persistence; provenance/TMS; spatial frames; **mereology** | JEP-145..150 |
| 18 | **LEARN FROM PROSE** — `read()` extracts FIVE relation types (is-a, part-of, causal, spatial, comparison) from a passage; 8/8 sentence-variation types; document-scale ~0.93 recall; cross-domain; belief revision | JEP-155..168, 183/185 |
| 19 | **COMMUNICATE what was learned** — `describe()` multi-relation profile; `respond()` Q&A across all relations; `why?` explanations; `summarize()` a source + flag its inconsistencies | JEP-160/168/173/197/198 |
| 20 | **RELATION-TYPE INTERACTIONS** — taxonomy interacts correctly with part-of, causal, comparison (each with right semantics + leak guard) | JEP-169/170/186 |
| 21 | **GROUNDING** — perceive an instance -> reason via prose-learned taxonomy; the developmental loop (perceive->discover->name->read->reason) on toy AND real images; functional grounding from observed interactions | JEP-178/179/187..192 |
| 22 | **CONSISTENCY** — detect IMPLIED contradictions (inherited negatives); audit a whole source for internal inconsistency | JEP-195/196 |
| 23 | **ABSTRACT concepts** reason symbolically (grounding is what's special); STRUCTURAL not lexical (novel nonsense-word concepts) | JEP-172/182 |
| 24 | **SELF-EXTENSIBLE** — `read_open()` auto-induces NEW relation types from repeated patterns in a passage (beyond the 5 fixed ones); proper-noun handling in generation | JEP-200/201/202/203 |
| -- | VALIDATED: property-based SOUND, fuzz ROBUST (0 crashes/6000), SCALABLE to 1000, STRUCTURAL, full INTEGRATION test; matured engine re-validated | JEP-124-127, 171/184/194 |
| -- | UNIFIED: perceive->understand->plan->ACT on conceptual goals; read->understand->communicate on prose | JEP-122/132/160 |

```python
# learning through dialogue (the capstone):
e.tell("A poodle is a dog."); e.tell("A dog is an animal.")
e.explain("is a poodle a living thing?")   # "I don't know whether a poodle is a living thing."
e.inquire("poodle", "living thing")        # "I know a poodle is an animal, but I don't know whether an animal is a living thing."
e.tell("An animal is a living thing.")     # taught exactly the identified gap
e.explain("is a poodle a living thing?")   # "Yes. A poodle is a dog, a dog is an animal, an animal is a living thing."
```

## Honest scope and the frontier (not arrival)
This is 100% on a **simple, controlled, parseable** language with **given/learned-from-features** prototypes. It is
the **foundation to scale FROM**, not human-level understanding. The named open frontier (deliberately outside the
engine's contract):
- **Parse at scale** — the gate is the GENRE, not the extractor (JEP-155/156): encyclopedic/descriptive prose works
  (`read()` ~0.87 precision with Hearst + bare-NP), but dense logic/argument prose (Boole) yields almost no structure
  even with the same patterns. The remaining gate: a real encyclopedic CORPUS (needs authorization) + the no-
  transformer rule forbidding learned extractors for messier registers.
- **Unsupervised structure learning** — partially SOLVED: the engine learns relational structure from observation
  (transitivity, composition rules, JEP-128..130) and discovers concepts by clustering (JEP-113/179); the residual
  is learning structure from NOISY+SPARSE+ONE-SHOT data simultaneously, which needs REUSE + active querying + the
  right (meta-learned) prior together (JEP-151..154), and DAG REDUNDANCY for generalization (JEP-177).
- **Abstract concepts** — REASONING works (the engine is structural, so justice->virtue->moral quality reasons like
  any taxonomy, JEP-182); only GROUNDING is blocked (an abstract has no perceptual referent — as for humans, it is
  learned relationally/linguistically via `read()`, not perceived).
- **Open dialogue / free generation** — communication is template-based on the domain, not open-ended; factual
  generation (profiles, explanations, Q&A) works, open/creative generation is blocked.
- **Rich grounding** — perception here is toy/easy (JEP-91/97/180 caveat); the BINDING of perception to prose-learned
  structure WORKS (JEP-178/179) and the full developmental loop composes (perceive->cluster->name->read->reason), but
  human-level grounding needs embodied experience (symbol-grounding, JEP-54..63). The developmental loop inherits
  perception's discriminability limits, not the binding's (JEP-180).
- **The NL long tail** — the matured `read()` covers the common encyclopedic constructions at ~0.9 recall / high
  precision (JEP-161..175), but the long tail of NL phrasings (and 'X of Y' nominal compounds, a deliberate
  precision/recall tradeoff) is the no-transformer wall: classic patterns cannot cover arbitrary prose; learned
  extractors are forbidden.

Strategy: develop on simple language, hold 100%, scale gradually; Boole's "Laws of Thought" is the final exam, not
the primer. Everything established and named (VSA/HRR, transitive closure, prototype perception, Boolean logic,
template NL generation); the transferable output is the working engine + the predict-calibrate discipline.
