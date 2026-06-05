# JEP-342 — "Make connections": the conversation relates new facts to what it already knows

## Motivation (Michael's teaching rule #2)
"Make connections: relate new concepts to what it already understands." Implement it substrate-legally via deductive
generation (JEP-331): when a statement teaches a new fact, the conversation surfaces the NEW entailments it can now
derive by connecting the new fact to existing knowledge — "A poodle is a dog — and since a dog is a mammal and a
mammal is an animal, a poodle is also a mammal and an animal!" No transformer.

## Method
`Conversation.say` on a statement: after `learn_sentence`, for the taught subject compute its multi-hop ancestors /
inherited properties via the climb (deductive), report those BEYOND the directly-stated parent as connections.
Surface only TRUE, newly-unlocked entailments; none if the fact is isolated.

## Pre-registered bars (BEFORE the run)
- **J342a (correct connections):** teaching a fact that links to prior knowledge surfaces the correct multi-hop
  entailments (e.g. poodle→mammal, poodle→animal after "a poodle is a dog" given dog→mammal→animal); every surfaced
  connection is TRUE and the set equals the new entailments, ≥ 0.95, both seeds (0, 7).
- **J342b (no false connections):** teaching an ISOLATED fact (no prior link) surfaces ZERO connections, both seeds.
- **J342c (no regression):** JEP-340 conversation still PASS; substrate gate green.

Predicted most-likely failure: surfacing a connection that's a re-statement of the direct parent (not novel) or a
non-entailed one. If J342a over-reports, restrict to ancestors strictly beyond the direct parent; reported not tuned.

## Result (seeds 0, 7): **PASS**
- **J342a:** teaching "A poodle is a dog." (given dog→mammal→animal, dog can bark) →
  *"Got it — I learned 1 new fact (I now know 4 facts). **And that connects: a poodle is a mammal; a poodle is an
  animal; a poodle can bark.**"* — correct multi-hop + inherited-property connections, both seeds. **PASS.**
- **J342b:** teaching an isolated "A zorp is a quib." → no connections surfaced, both seeds. **PASS.**
- **J342c:** JEP-340 conversation still PASS. **PASS.**

## Verdict: **PASS**
Implements Michael's teaching rule #2 ("make connections") substrate-legally: when taught a new fact, the
conversation relates it to existing knowledge by surfacing the new deductive entailments (poodle→mammal→animal,
inherited "can bark") — JEP-331 deductive generation applied conversationally. Isolated facts surface nothing.
Makes the dialogue feel connected and alive without any LLM. No transformer, no pretrained model.

