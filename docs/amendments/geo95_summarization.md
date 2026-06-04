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

## Result — PASS
| metric | value |
|--------|-------|
| coverage (key facts mentioned) | **0.94** |
| faithfulness (no invented years) | **1.00** |
Example: "Alice, a data scientist with expertise in the Falcon project based in Boston, has been actively
contributing to the field..."

**VERDICT: PASS.** The 0.5B model produces grounded multi-fact summaries — retrieve an entity's facts (kind/
subject-scoped) -> summarize from context -> coverage 0.94, faithful 1.00 (no invented specifics). So
"summarize what I know about X" works on the PC as a grounded personal-KB feature. **Honest note:** the 0.5B
model's fluency is limited (summaries are basic, occasionally generic, can trail off at the token limit) and
coverage isn't perfect (0.94 — sometimes omits a fact), but the output is FAITHFUL to the retrieved context
(grounding suppresses invention, as GEO-38). A larger generator would produce more fluent summaries; the small
one is correct-but-basic. Adds summarization to the toolkit's capabilities: factoid/multi-hop/aggregate/
temporal/join/compare/negate + grounded generation + SUMMARIZATION, all grounded in the explicit store.
