# JEP-357 — Self-extending reading: the brain learns to read new constructions from the teacher

## Motivation
Capstone of the breakthrough programme (attack B): wire construction induction (JEP-354/355) into the live
Conversation so the brain EXTENDS ITS OWN READING. When it hits a sentence it can't parse, the teacher gives the
fact once; after 2 examples of that construction the brain induces the template and then parses FUTURE sentences of
that form autonomously — composing induction with the durable store. No transformer.

## Method
`Conversation.teach_construction(sentence, fact)` records the example and, when two examples align (anti-unification
induces a template), adds it to `learned_constructions`. `_learn_one` falls back to the learned constructions (with
function-word abstraction) when the engine + normalizer extract nothing — so a previously-unparseable form now
yields facts into the durable store.

## Pre-registered bars (BEFORE the run)
- **J357a (learns to read):** teach 2 examples of a NEW construction ("X was domesticated by Y"); then a HELD-OUT
  sentence of that construction, read normally via `_learn_one`, yields the correct fact into the store and is
  answerable, ≥ 0.90, both seeds (0, 7).
- **J357b (gap → parsed):** BEFORE teaching, the construction's held-out sentences yield no facts; AFTER, they do.
- **J357c (no regression):** normal sentences still parse as before; conversation gate green; persists in-session.

Predicted most-likely failure: a learned construction over-fires on an unrelated sentence (false facts). Require the
fixed-word skeleton to match (induct only aligns same-skeleton examples); if J357c shows false facts on normal
sentences, report and tighten.

## Result (seeds 0, 7): **PASS**
- **J357a:** after teaching 2 examples of "X was domesticated by Y", held-out sentences read via `_learn_one` yield
  the correct facts = **2/2**, both seeds. **PASS.**
- **J357b:** BEFORE teaching the construction parses **0/2**; AFTER, **2/2** — the brain closed its own gap. **PASS.**
- **J357c:** no junk facts injected on an unrelated sentence; conversation gate green. **PASS.**

## Verdict: **PASS — the brain extends its own reading**
Capstone of the breakthrough programme: the durable Conversation now learns to READ a new sentence construction
from the teacher — given 2 examples of a form the engine couldn't parse, it induces the template (JEP-354) with
function-word abstraction (JEP-355) and thereafter reads unseen sentences of that form by itself, dropping the facts
into the durable store. This is the honest, real shape of self-extension WITHOUT an LLM: **construction induction +
the durable store + a teacher**, composed. Where it needs synonymy or deep structure it still needs taught knowledge
(JEP-356) — no single trick, composed learned components + a human in the loop. That is a genuine, measured step
toward the goal, with every boundary named. No transformer, no pretrained model.

