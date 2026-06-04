# GEO-99 — Shipped-API verification gate (catch heredoc-introduced bugs)

## Motivation
GEO-98 caught a BROKEN shipped sanitize_text (heredoc regex-escaping artifact) — a reminder to VERIFY shipped
code, not assume it works from the experiments. GEO-99 verifies every public GeometricReasoner method against
its documented behavior end-to-end, catching any other subtle bugs in the deliverable's shipped API.

## Pre-registration (locked BEFORE run)
- For each public method, a minimal test asserting the documented behavior:
  add_fact/add_document, retrieve(+kind), ask, chain, count_where, resolve_entity, check_contradiction,
  values_for, calibrate_abstention, sanitize_text.
- Metric: number of methods passing their assertion. Bar: ALL pass (the shipped API works as documented).
  Any failure = a real shipped bug to fix (honest QA finding).
