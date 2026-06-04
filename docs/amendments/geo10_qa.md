# GEO-10 — Multi-hop QA on ARBITRARY facts: the critical boundary

## Result (MiniLM; synthetic KB: person→company→city→language, arbitrary assignments)
| query | hits@1 |
|-------|--------|
| 2-hop (person→company→city) | 0.08 |
| 3-hop (→language) | 0.02 |

**VERDICT: NULL** — multi-hop QA fails on ARBITRARY facts.

## Finding (CRITICAL) — the geometric method reasons over the LLM's EXISTING knowledge, it does NOT learn new arbitrary facts
GEO-6/7/9 worked because their relations (capital, language, plural, …) are ALREADY ENCODED in the LLM's
pretrained geometry — all country→capital offsets are consistent because the model KNOWS those facts, so a
mean offset generalizes. GEO-10's facts ("Alice works at Google") are ARBITRARY assignments the LLM has
never seen, so each person→company offset is a different random direction; no consistent relation exists and
the mean offset is noise → composition collapses (0.08/0.02).

**So the honest boundary of EQMOD-3:** the geometric+LLM method does relational REASONING by reading out and
composing structure the LLM ALREADY has. It is NOT a general new-knowledge learner — it cannot acquire
arbitrary new facts geometrically (there is no geometry to exploit). The "few-shot learning" of GEO-6 was
extracting a pre-existing relation direction, not learning new knowledge.

## Implication for the goal (a learning+understanding method)
- UNDERSTANDING (reason/compose over what the model knows): geometric operations work (GEO-5–9).
- LEARNING NEW arbitrary facts: needs explicit MEMORY (key→value store), NOT geometric generalization.
The honest architecture is a HYBRID: a key-value memory for new facts + geometric reasoning over the LLM's
structured knowledge. Next (GEO-11): test that hybrid — store new facts in memory, reason over them.
