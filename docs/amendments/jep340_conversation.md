# JEP-340 — Talk to it: a conversation loop where the memory grows live as it learns

## Motivation (Michael's restated goal)
"The substrate learns, understands human-like, I can talk with it human-to-human, and during the talk the memory
grows when it learns something new." Assemble the existing pieces — `learn_sentence` (memory grows + bridges to the
durable store), `BrainQuery` (answers) — into ONE conversational loop: each turn is a STATEMENT (it learns, the
durable memory grows, it acknowledges what's new) or a QUESTION (it answers from what it knows so far). Durable
across the conversation AND across sessions. No transformer.

## Method
`world/conversation.Conversation`: classify each line (question vs statement); statement → `learn_sentence` (record
+ bridge), report the NEW facts added (memory grew); question → `BrainQuery(...).ask`. `tools/talk.py` is the REPL.
Brain loads from / saves to a durable folder, so a later session continues the same growing memory.

## Pre-registered bars (BEFORE the run)
- **J340a (learn-then-answer in dialogue):** in a scripted multi-turn conversation, every question is answered
  correctly from facts taught EARLIER in the same conversation (incl. multi-hop across separately-taught facts) and
  from facts taught in a PRIOR session (after reload) ≥ 0.95, both seeds (0, 7).
- **J340b (memory grows live + persists):** each teaching turn strictly increases the durable fact count; after
  save+reload the grown memory is intact and a new question over it answers correctly, both seeds.
- **J340c (tool):** `world.conversation` + `tools/talk.py` import; a headless scripted conversation runs end to end.

Predicted most-likely failure: question/statement misclassification (a statement phrased like a question, or
vice-versa) routes a teach to the answerer or vice-versa. If J340a misses, report the misclassified turn (a
parser-coverage finding), not a tuned script.

## Result (seeds 0, 7): **PASS**
- **J340a:** scripted dialogue — answers = **1.0** (every question answered from facts taught EARLIER in the
  conversation, incl. multi-hop "is a poodle an animal?" across 3 separately-taught facts, and inherited "can a
  poodle bark?"); prior-session recall True; new-fact-answered True, both seeds. **PASS.**
- **J340b:** every teaching turn strictly grew the durable fact count; memory persisted across save+reload and kept
  growing in a NEW session, both seeds. **PASS.**
- **J340c:** `world.conversation` + `tools/talk.py` import; live CLI demo works (teach → "I learned 1 new fact (I
  now know N facts)" → questions answered → saved durably). **PASS.**

## Verdict: **PASS**
Michael can talk to the substrate human-to-human: statements teach it (the durable memory GROWS live, fact count
rising each turn), questions are answered from everything it knows so far, and the memory persists and keeps growing
across sessions. Directly delivers the restated goal. Honest gap: the question parser covers
is-a/property/why/what-verb templates; a bare "what is a poodle?" (asking for the parent) isn't covered yet —
a small parser extension, noted. No transformer, no pretrained model.
