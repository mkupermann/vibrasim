# JEP-225 — fix: a 'Not that I can tell' follow-up must not update the order context (bug surfaced by the JEP-224 demo)

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 only updating the order context on a TRUE 'what about X?' answer stops 'why?' from wrongly explaining a false/
  unknown comparison.

## Result — PASS (HIT)
The JEP-224 multi-turn demo surfaced a genuine correctness bug: 'is an elephant bigger than a dog?' -> 'Yes.' then
'what about a mouse?' -> 'Not that I can tell.' (mouse not in the order), but 'why?' WRONGLY answered 'Because an
elephant is bigger than a mouse.' — because the 'what about X?' order branch set `_last_rel_query` to (elephant,
mouse) BEFORE checking whether the comparison actually held. FIX: only set `_last_rel_query` when `_order_holds` is
True. Now 'what about a mouse?' -> 'Not that I can tell.' and 'why?' -> 'Because an elephant is bigger than a dog.'
(the prior VALID comparison, not the false one). A self-caught correctness bug from running the definitive demo —
the demo is doing its job as a real-usage check. 90/90 regression tests green (+1). Prediction HIT; tally 113/140.
Established (dialogue-context correctness); named; no novelty.
