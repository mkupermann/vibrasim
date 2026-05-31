# BET-121 — Least-Squares Order-2 Sequence Memory (the wall, broken)

Pre-registered: 2026-05-31. BET-120 showed order-2 context fixes repeated tokens
(HELLO) but Hebbian transitions still interfere across sequences. BET-121 replaces
Hebbian with a LEAST-SQUARES (projection) fit of the order-2 transition operator
(world/energy.py SequencePredictor) — the new math that removes interference.

## Bars
| ID | Criterion | Bar |
|----|-----------|-----|
| T121a | Repeats | 'HELLO' and 'MISSISSIPPI' replayed EXACTLY (many repeats) |
| T121b | Many sequences | S=12 length-4 sequences @ N=300, every sequence min overlap = 1.00 |
| T121c | Long + many | S=20 length-5 sequences @ N=400, min overlap >= 0.95 |
| T121d | Control FAILS | a shuffled transition operator fails (< 0.70) |

PASS = T121a-d. PASS = the context-dependent sequence-prediction wall is broken
without a transformer: arbitrary overlapping sequences with repeated tokens are
recalled exactly. This is the language-relevant capability that capacity-scaling
alone could not deliver.

## RESULT
_(filled after the run)_
