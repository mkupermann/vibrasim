# JEP-202 — integrate auto-learned open relations into COMMUNICATION (describe)

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 rendering multi-word relations verbatim (no added -s, no 'the') fixes describe to 'It is capital of france';
  single-verb relations ('chases the cat') unaffected.

## Result — PASS (HIT)
describe() rendered open relations brokenly: a (paris, 'is capital of', france) fact became 'It is capital ofs the
france' (the single-verb SVO renderer 'f"{r}s the {o}"' wrongly adds -s and inserts 'the' on a multi-word relation).
FIX: render a multi-word/open relation VERBATIM ('is capital of france'), keep the single-verb form ('chases the
cat') for one-word verbs. Now:
- describe('paris') -> '... It is capital of france.' (the auto-learned open relation rendered naturally).
- describe('dog') -> 'It chases the cat.' (single-verb relation unaffected).
This completes the OPEN-RELATION loop: the engine LEARNS a new relation from prose (JEP-200), AUTO-INDUCES it from a
passage (JEP-201), queries it role-sensitively, and now COMMUNICATES it correctly. (A separate known limitation
surfaced, not fixed here: PROPER NOUNS get a wrong article / no capitalization — 'A paris', 'france' — because the
engine treats all nouns as common; proper-noun handling is out of the current scope.) 71/71 regression tests green
(+1). Prediction HIT; tally 91/118. Established (template NL generation); named; no novelty.
