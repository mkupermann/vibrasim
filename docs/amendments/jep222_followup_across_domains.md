# JEP-222 — multi-turn conversational context across domains (is-a AND comparison follow-ups)

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 extending 'what about X?' to reuse the last ORDER query (reuse first arg + comparative, new second arg) lets
  'is an elephant bigger than a dog?' -> 'what about a mouse?' -> 'is an elephant bigger than a mouse?' Yes. RISK:
  which argument the follow-up replaces.

## Result — PASS (HIT)
Extended the 'what about X?' follow-up (JEP-219, previously is-a only) to ALSO reuse the last COMPARISON: it keeps the
first argument + comparative and substitutes the new second argument. 'is an elephant bigger than a dog?' -> 'Yes.'
then 'what about a mouse?' -> 'Yes, an elephant is bigger than a mouse too.'; 'what about a cat?' -> 'Yes, an elephant
is bigger than a cat too.' The handler picks is-a vs comparison by the MOST RECENT query type (_last_rel_query order
takes precedence, else _last_query is-a), so the conversation tracks context correctly when switching domains
('is a dog an animal?' -> 'what about a mammal?' -> 'Yes, a mammal is an animal too.'). Completes multi-turn
conversational CONTEXT across the is-a and comparison domains. 88/88 regression tests green (+1). Prediction HIT;
tally 111/138. Established (conversational ellipsis across query types); named; no novelty.
