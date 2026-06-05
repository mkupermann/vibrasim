# JEP-223 — multi-turn context for numeric comparison + clean context-switching across all domains

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 tracking the last numeric comparison and having 'what about X?' reuse it (same first entity + attribute, new
  second entity) completes multi-turn context across all yes/no comparison domains. RISK: new entity's number unknown.

## Result — PASS (HIT)
Extended 'what about X?' to also reuse the last NUMERIC comparison (keep first entity + attribute, substitute the new
second entity), and made the THREE recency trackers (_last_query is-a, _last_rel_query part/cause/order, _last_num_query
numeric) MUTUALLY EXCLUSIVE — each query type clears the other two — so the follow-up always reflects the MOST RECENT
question with no staleness. 'does a spider have more legs than a dog?' -> 'Yes.' then 'what about an ant?' -> 'Yes.'
(spider 8 > ant 6); 'what about a dog?' -> 'Yes.' Then switching domain: 'is a dog an animal?' -> 'what about a
spider?' -> 'No...' (IS-A context, the numeric tracker was cleared). Multi-turn conversational CONTEXT now spans
is-a + comparison + temporal + NUMERIC, with correct context-switching. 89/89 regression tests green (+1). Prediction
HIT; tally 112/139. Established (multi-tracker dialogue context with mutual exclusion); named; no novelty.
