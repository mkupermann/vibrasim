# JEP-346 — Read a text/book into the brain over time; discuss it; "what is not clear to you?"

## Motivation (Michael's vision)
"The substrate reads a new text and wants to understand it… over 3 days it reads a link or a book and then discusses
what it has learned. Or I ask 'what is not clear to you?' and it tells me." Build: (1) read a whole document into the
durable brain (it learns all of it, memory grows, accumulates across sessions/days); (2) the brain reports its
KNOWLEDGE GAPS — concepts it has heard of but cannot place (no definition) — as open questions back. No transformer.

## Method
`Conversation.read_text(text)` reads a multi-sentence document sentence-by-sentence into the durable store, returns a
summary (facts learned, concepts). `gaps()` = concepts that are REFERENCED (in is-a or relations) but never DEFINED
(no is-a parent of their own) and aren't recognized roots — "I know a dog is a mammal, but what is a mammal?".
"what is not clear to you?" / "what don't you understand?" in conversation reports the gaps. `tools/read_to_brain.py`
reads a .txt file into the durable brain (the same folder accumulates over days).

## Pre-registered bars (BEFORE the run)
- **J346a (read a document, learn, discuss):** reading a multi-sentence document grows the durable memory and, after
  reading, the brain answers questions about its content (≥ 0.90 vs the engine) and the memory persists across a
  reload ("next day"), both seeds (0, 7).
- **J346b ("what is not clear to you"):** the brain reports the genuine gaps — concepts referenced but undefined
  (e.g. an undefined top concept) — and reports NONE when every referenced concept is defined or a root, both seeds.
- **J346c (tool + durability):** `tools/read_to_brain.py` reads a text file into a brain folder; re-reading more text
  next session accumulates (fact count grows), not resets.

Predicted most-likely failure: a document sentence the engine doesn't parse contributes no facts (parse coverage) —
report the parse rate; or a "root" the brain legitimately can't define is flagged as a gap (tune the root set by
naming it, not by hiding). If J346b over-reports, list the flagged concepts.

## Result (seeds 0, 7): **PASS**
- **J346a:** `read_text(DOC)` learned **12 facts**; discussing the document (is-a multi-hop, properties) = **1.0** vs
  the engine; persists across a reload ("next day"), both seeds. **PASS.**
- **J346b:** "what is not clear to you?" → *"A few things aren't clear to me yet — what is a bird?; what is a
  cancer?; what is a heart?; what is a smoking?"* — genuine gaps (concepts referenced but undefined; roots not
  flagged). After next-day reading "A bird is an animal." the bird gap CLOSES. Both seeds. **PASS.**
- **J346c:** next-day reading accumulates (fact count grows, not resets); `tools/read_to_brain.py` reads a text file
  into the durable brain. **PASS.** (Test fix: DOC2 must DEFINE bird to close its gap — adding another bird doesn't.)

## Verdict: **PASS**
Delivers Michael's vision: feed the brain a text/book (`read_to_brain.py`), it learns every parseable sentence (the
memory grows and PERSISTS across days), you discuss it via `talk.py`, and asking "what is not clear to you?" gets an
honest report of its knowledge gaps — concepts it has heard of but cannot yet place. The gap report doubles as
Socratic prompting (it asks YOU "what is a bird?"). No transformer, no pretrained model.

