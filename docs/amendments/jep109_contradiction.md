# JEP-109 — contradiction detection (consistency checking), a human-like reasoning capability

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 100%: would_contradict() flags conflicts — "X is not C" when C is currently derivable for X; "X is C" when X
  was explicitly told NOT to be C; unknown categories don't conflict. Non-blocking (corrections via tell still
  override). MOST-LIKELY MISS: polarity parse, or confusing a defeasible exception with a hard contradiction.

## Acceptance
- PASS: contradiction battery = 100%. Established (consistency/contradiction checking over a knowledge base),
  named; no novelty. HONEST: detects IS-A contradictions (direct + via closure); property-level and cross-branch
  conflict detection is a later tier.

## Result — PASS (HIT)
Contradiction battery 6/6: "whale is not a mammal" -> contradicts (direct); "whale is not an animal" -> contradicts
(via closure); "whale is a fish" -> no conflict (unknown); "whale is a mammal" -> no conflict (already true); after
"whale is not a fish", "whale is a fish" -> contradicts (explicit negative); correction still works (non-blocking).
Prediction HIT; tally 12/21; 20 tests gated green. The engine checks consistency: it notices when a new claim
conflicts with current beliefs (direct or via transitive closure), without blocking intentional corrections.
Established (consistency checking over a KB), named; no novelty. HONEST: IS-A contradictions only; property-level
and cross-branch conflicts are a later tier.
