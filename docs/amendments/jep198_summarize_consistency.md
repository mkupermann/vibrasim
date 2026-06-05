# JEP-198 — summarize() integrates an honest consistency assessment (flag a source's contradictions)

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 summarize() reports the overview AND flags any internal contradiction (via the audit); consistent sources get
  no note. RISK: phrasing the note coherently.

## Result — PASS (HIT)
Integrated consistency_audit (JEP-196) into summarize (JEP-197): after the knowledge overview, summarize() now
appends an honest note if the source is internally inconsistent. Results:
- CONSISTENT source: 'I learned about an animal. A mammal is an animal. Some things have parts — for example, a heart
  is part of a dog.' (no inconsistency note).
- INCONSISTENT source: '... But I noticed an inconsistency: a whale is said to be a fish, which conflicts with what
  else I was told.' (flags the contradiction; '(and N other contradictions)' if more).
This is the human-like behavior of summarizing a source AND honestly flagging where it contradicts itself — combining
generative communication (JEP-197) with consistency checking (JEP-195/196). Fixed a sentence-capitalization template
artifact in summarize. 67/67 regression tests green (+1). Prediction HIT; tally 87/114. Established (template NL
generation + consistency audit); named; no novelty.
