# JEP-143 — temporal reasoning with PERSISTENCE (the frame problem), a classic distinct faculty

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 100%: a fluent (state) holds from when an event sets it UNTIL a later event changes it (frame axiom); state-
  at-time queries are correct across an event sequence. MOST-LIKELY MISS: the persistence default vs explicit-
  change boundary.

## Acceptance
- PASS: fluent_at returns the persisted value across events = 100%. Established (situation/event calculus, the
  frame axiom; McCarthy), named; no novelty. HONEST: qualitative discrete timeline; no concurrent events,
  durations, or ramifications (indirect effects).

## Result — PASS (HIT)
Temporal battery 9/9: a fluent set by an event PERSISTS through unrelated later events (door stays open through the
'turn on light' event — the frame axiom) until an event changes it (closed -> False); fluents are None before first
set; light/seated persist once set. Prediction HIT; tally 38/57; 35 tests gated green. Correctly implements default
PERSISTENCE (the frame problem, McCarthy's situation/event calculus) — state-at-time = the most recent event that
touched the fluent. A genuinely distinct faculty (event-based state reasoning, not taxonomy/relation). Established
(situation calculus + frame axiom), named; no novelty. HONEST: qualitative discrete timeline; no concurrent events,
durations, or ramifications (indirect/derived effects of an event).
