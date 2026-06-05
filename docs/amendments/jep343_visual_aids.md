# JEP-343 — Visual aids: the brain draws a picture of what it knows (Michael rule #3)

## Motivation (Michael's teaching rule #3: "give visual aids")
Let the durable brain DRAW its knowledge — render the is-a taxonomy + properties it has learned as an image, so
Michael can SEE what it knows and how concepts connect. Substrate-legal (plotting the stored facts; no neural net).

## Method
`world/visualize.draw_knowledge(mem, path)` — read the is-a edges from the store, compute each concept's depth,
lay out a hierarchy (depth → y, siblings spread on x), draw nodes + child→parent arrows, annotate properties.
Saves a PNG. The conversation/CLI responds to "draw what you know" / "show me what you know" by generating it.

## Pre-registered bars (BEFORE the run)
- **J343a (accurate image):** `draw_knowledge` on a taught brain produces a PNG whose drawn edge set EQUALS the
  store's is-a edge set (every is-a fact depicted, no spurious edges), both seeds (0, 7).
- **J343b (conversation hook):** `Conversation.say("draw what you know")` (and "show me what you know") generates
  the image and returns its path; `tools/talk.py` mentions the command.
- **J343c (real brain):** renders a multi-domain taught brain (≥10 concepts) to a non-empty PNG.

Predicted most-likely failure: a concept with multiple parents (DAG) or a cycle could break the depth layout
(infinite loop); guard depth with a visited set. If J343a misses, report whether it's a DAG-layout or an
edge-extraction issue.

## Result (seeds 0, 7): **PASS** (after under-teach + talk.py-doc fix)
- **J343a:** `draw_knowledge` renders the is-a hierarchy + properties to a PNG depicting all **12** is-a edges,
  no spurious edges, both seeds. **PASS.**
- **J343b:** `Conversation.say("draw what you know")` / "show me what you know" generate the image and return the
  path; `tools/talk.py` documents the command; JEP-340 still PASS. **PASS.**
- **J343c:** renders a 13-fact multi-domain brain to a non-empty PNG (`docs/knowledge_demo.png` delivered). **PASS.**
- First cut PARTIAL: only 9 is-a edges (under-taught) and talk.py lacked the doc; fixed by teaching more is-a facts
  and documenting the command (bar unchanged).

## Verdict: **PASS**
Implements Michael's teaching rule #3 (visual aids): the durable brain DRAWS a picture of what it knows — its is-a
taxonomy with learned properties — and "draw what you know" works in the conversation/CLI. Pure plotting of the
substrate's own facts (cycle-safe depth layout); no neural net, no transformer.

