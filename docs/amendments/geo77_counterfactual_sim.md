# GEO-77 — Symbolic counterfactual SIMULATION (answer store-manipulable what-ifs, not just abstain)

## Motivation
GEO-75/76: the system ABSTAINS on counterfactuals. But a CLASS of counterfactuals is answerable by symbolic
SIMULATION over the structured store: "if X moved to team T, who is on team S?" = copy store, apply the
change, re-query. GEO-77 tests whether a symbolic counterfactual operator answers these correctly —
extending the system from "abstain on what-ifs" to "answer store-manipulable what-ifs".

## Pre-registration (locked BEFORE run)
- Employee store (person -> team). Counterfactual queries: "if <P> moved to <T>, who would be on <S>?"
- Operator: parse (P, new-team T), copy the membership, set P's team = T, list members of the asked team S.
- 8 counterfactual queries with known correct answer-sets (under the hypothetical).
- Metric: set-F1 vs the counterfactual ground truth. Bar: >= 0.85 (symbolic simulation answers store-
  manipulable counterfactuals). Honest: this is ONE class of counterfactual (membership changes); causal
  ("why") and open counterfactuals remain out of scope (GEO-75).
