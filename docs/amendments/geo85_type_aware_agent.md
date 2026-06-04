# GEO-85 — Type-aware agent: auto-kind-routing eliminates cross-type confusion

## Motivation
GEO-83/84: cross-type retrieval confusion ("the pipe fixing person" -> a 'fix' TASK over the plumber CONTACT)
is the recurring personal-KB miss. Fix: a TYPE-aware layer that detects the query's target kind and scopes
retrieval (kind-scoped retrieval shipped in GEO-83). GEO-85 adds auto-kind-routing and verifies it removes
the cross-type miss end-to-end on the personal KB, including the vague queries.

## Pre-registration (locked BEFORE run)
- Personal KB (contacts/tasks/notes). A kind-router: keyword/semantic cues map a query to its target kind
  (who/person/role -> contact; task/due/when/fix -> task; note/about -> note); fall back to unscoped.
- Re-run the GEO-83 + GEO-84 queries with kind-scoped retrieval driven by the router.
- Metric: accuracy with auto-kind-routing vs without (GEO-83 0.90, GEO-84 vague 0.88). Bar: >= 0.95 combined
  (the cross-type misses are removed). NULL if routing mis-detects and hurts.

## Result — PARTIAL/NULL (routing just moves the error)
| method | accuracy |
|--------|----------|
| without kind-routing | 0.90 |
| with auto-kind-routing | 0.90 |
New miss: "when's the tax thing" routed to kind=note ("thing" matched the note pattern) -> retrieved vacation
note instead of the tax task.

**VERDICT: PARTIAL/NULL.** Auto-kind-routing via keywords does NOT improve over unscoped (0.90 = 0.90) — it
just MOVES the error: an ambiguous query ("thing") mis-routes to the wrong kind, trading cross-type retrieval
confusion for mis-routing. Same ~0.90 ceiling as keyword intent-routing (GEO-48). **Honest conclusion:** the
cross-type miss is fundamentally a DISAMBIGUATION problem that keyword heuristics can't fully solve. Explicit
kind-scoping WORKS when the caller knows the type (GEO-83 manual scoping fixed the plumber case); AUTO-
detecting the type from a vague query is as error-prone as the retrieval it's meant to fix. So: expose
kind-scoping as an OPTION (let the app/user specify the type when known — shipped in retrieve(kind=)); do not
rely on automatic keyword routing for mixed-type vague queries (accept ~0.90, or use a trained intent
classifier). NOT retuned — the honest 0.90=0.90 stands. Cross-type confusion on vague mixed queries is a real,
bounded UX limitation.
