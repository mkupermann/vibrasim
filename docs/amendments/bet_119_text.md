# BET-119 — Single-Sequence Character Replay (what works, and the limit on text)

Pre-registered bars (defined before the run, in tools/run_bet119_text.py):
| ID | Criterion | Bar |
|----|-----------|-----|
| T119a | Works on text | a text with UNIQUE characters is recalled EXACTLY from its first char |
| T119b | Shows the limit | a text with a REPEATED character does NOT recall exactly (breaks at the repeat) |

PASS = both: the working single-sequence predictor replays real character strings,
and the context limit is demonstrated on readable text.

## RESULT (2026-05-31): PASS

- 'BRAIN' (unique) -> 'BRAIN'  (exact)
- 'GEOMTRICAVS' (unique, longer) -> 'GEOMTRICAVS' (exact)
- 'HELLO' (repeated 'L') -> 'HELOL' (breaks at the repeat)

The working capability (BET-113) is demonstrated on text: a character sequence is
stored and replayed self-supervised, no transformer. And the wall (BET-114-118) is
shown concretely: a repeated token in different contexts (L->L vs L->O) is an
ambiguous transition the pairwise mechanism cannot disambiguate — exactly the
structure that pervades written language. 'HELLO'->'HELOL' is the sequence wall in
one word.
