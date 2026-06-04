# GEO-95 — Grounded multi-fact SUMMARIZATION ("summarize what I know about X")

## Motivation
A real personal-KB use case: summarize multiple facts about a topic. GEO-95 tests grounded summarization —
retrieve all facts about an entity, feed them to the 0.5B generator, produce a summary. Genuinely uncertain:
does a small model synthesize multiple grounded facts COHERENTLY and FAITHFULLY (no added facts)?

## Pre-registration (locked BEFORE run)
- KB with several facts per entity (e.g. a person: role, location, project, tenure). 4 entities.
- For each: retrieve the entity's facts (kind-scoped by subject), feed as context, prompt "summarize what is
  known about X using only the context".
- Metric: (a) COVERAGE — fraction of the entity's facts mentioned in the summary; (b) FAITHFULNESS — no facts
  NOT in the context (check for invented specifics). Bars: coverage >= 0.7 AND faithfulness (no hallucination)
  on >= 0.75 of summaries. Honest about the small-model ceiling.
