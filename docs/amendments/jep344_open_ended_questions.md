# JEP-344 — Open-ended questions, once it's ready (Michael rule #1)

## Motivation (Michael's teaching rule #1)
"Ask open-ended questions ('Why do you think this happened?' / 'What do you think comes next?') ONCE IT IS READY, to
encourage independent thought." Substrate-legally: once the brain has enough connected knowledge, after a teaching
turn it occasionally asks an open-ended question back — a "why?" for a causal fact, a gap-probing "What is an X?"
when a taxonomy chain doesn't reach a root, or "what comes next?" for a temporal chain. Gated on readiness. Honest:
the brain poses the question (Socratic prompting), it does not itself creatively answer it (the JEP-332 wall).

## Method
`Conversation`: track readiness (fact count ≥ threshold). After learning a statement, `_open_ended(text, subject)`
returns ONE open question: causal text → "Why do you think {cause} causes {effect}?"; an is-a whose chain-top has no
known parent → "What is a/an {top}?"; temporal → "What do you think comes after {last}?". Appended to the reply.

## Pre-registered bars (BEFORE the run)
- **J344a (asks when ready):** with a ready brain (≥ threshold facts), teaching a causal fact elicits a "why do you
  think…" question naming the cause/effect, AND teaching an is-a whose top is unknown elicits a "what is …?"
  question naming the top concept, both seeds (0, 7).
- **J344b (gated on readiness):** a NOT-ready brain (few facts) asks NO open-ended question, both seeds.
- **J344c (well-formed + no regression):** the questions are relevant (name the right concept) and JEP-340/342
  still PASS.

Predicted most-likely failure: asking a redundant question (the top IS a known root, or the "why" duplicates a
just-asked one). Gate "what is X" only when the top has no stored parent and isn't a generic root; one question per
turn. If J344a over/under-fires, report the trigger condition.

## Result (seeds 0, 7): **PASS**
- **J344a:** ready brain — teaching "Smoking causes cancer." → *"Why do you think smoking causes cancer?"*; teaching
  "A guppy is a fish." (fish unknown) → *"What is a fish?"*, both seeds. **PASS.**
- **J344b:** not-ready brain (1 fact) → no open-ended question, both seeds. **PASS.**
- **J344c:** questions name the right concepts; JEP-340 + JEP-342 still PASS. **PASS.**

## Verdict: **PASS**
Implements Michael's teaching rule #1: once the brain is READY (≥6 connected facts), after a teaching turn it asks
an open-ended Socratic question back — "why do you think X causes Y?", a gap-probing "what is an X?", or "what comes
after X?" — gated on readiness, to encourage the teacher to extend/explain. Honest: the brain POSES the question
(prompting), it does not creatively answer it (the JEP-332 creative wall). **All three teaching rules now live:**
#1 open-ended questions (this), #2 make connections (JEP-342), #3 visual aids (JEP-343). No transformer.

