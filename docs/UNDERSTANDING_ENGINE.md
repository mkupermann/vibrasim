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
| 4 | COMMUNICATE reasoning in English | JEP-95 |
| 5 | LEARN by correction (belief revision) | JEP-96 |
| 6 | LEARN a concept from examples shown | JEP-97 |

## Honest scope and the frontier (not arrival)
This is 100% on a **simple, controlled, parseable** language with **given/learned-from-features** prototypes. It is
the **foundation to scale FROM**, not human-level understanding. The named open frontier (deliberately outside the
engine's contract):
- **Parse at scale** — dense real prose (Boole) yields almost no structure with classic extraction (JEP-89); the
  no-transformer rule forbids learned extractors. This is the hard gate.
- **Unsupervised structure learning** — concepts/relations are still given/told, not discovered from raw experience
  (JEP-69/70 NULL).
- **Open dialogue / free generation** — communication is template-based on the domain, not open-ended.
- **Rich grounding** — perception here is toy/easy (JEP-91/97 caveat); human-level grounding needs embodied
  experience (symbol-grounding, JEP-54..63).

Strategy: develop on simple language, hold 100%, scale gradually; Boole's "Laws of Thought" is the final exam, not
the primer. Everything established and named (VSA/HRR, transitive closure, prototype perception, Boolean logic,
template NL generation); the transferable output is the working engine + the predict-calibrate discipline.
