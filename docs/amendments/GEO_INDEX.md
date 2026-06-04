# EQMOD-3 Geometric programme — experiment index (GEO-1 → GEO-90)

One line per rung. Verdict + the finding. Full write-up in each `geo*.md`. Authoritative narrative:
`docs/GEOMETRIC_ANSWER.md`; structured summary: `GEOMETRIC_PROGRAMME_SUMMARY.md`.

## Core geometry — does the geometric view work?
- GEO-1  PASS — compose relations on a grid (0.52, ctrl 0.00).
- GEO-2  PASS — inverses + multi-hop (5-hop 0.38 vs chance 0.03).
- GEO-4  PASS — clean geometry via MDS (analogy 0.76, comp 1.00).
- GEO-5  PASS — analogy on real LLM word embeddings (0.88).
- GEO-6  PASS — few-shot relation = mean-offset beats linear map (0.94–1.00).
- GEO-7  PASS — compose LEARNED relations multi-hop on LLM (1.00).
- GEO-8  PASS — survives distractor vocab (0.97).
- GEO-9  BOUND — antonyms weak (0.54), sit close in embedding space.
- GEO-10 NULL — geometry can't generalize ARBITRARY new facts (random offsets).
- GEO-11 PASS — hybrid memory(new facts)+geometry(known) (0.88).
- GEO-12 PASS — learn NEW structured knowledge, infer derived facts (grandparent 0.63, ctrl 0.00).
- GEO-13 INCONCLUSIVE — linear-chain + normalized TransE degenerate (setup flaw).
- GEO-14 PARTIAL — LLM-prior + new-structure entanglement tension (resolved by GEO-21).

## Sentences, multi-hop, integration
- GEO-15 PASS — relational geometry lifts to SENTENCES (retrieval 1.00, analogy 1.00).
- GEO-16 PASS — multi-hop reasoning by iterative retrieval, generator-free (1.00, chain necessary).
- GEO-17 PASS — 3-hop robust to 100 distractors + paraphrase (1.00).
- GEO-18 PASS — aggregation via retrieval + SYMBOLIC layer (1.00; pure geometry 0.00).
- GEO-19 PASS MILESTONE — integrated learn->apply->chain->aggregate on held-out data (1.00).
- GEO-20 PASS-as-designed — geometry weak on NEGATION (F1 0.50), BELOW chance on COMPARISON (0.29); symbol fixes.
- GEO-21 PARTIAL/RESOLVED — orthogonal subspaces: LLM semantics preserved (drift 0.00) while structure trains.
- GEO-22 — scale: 1-hop 0.98, 2-hop 0.87 at 400 facts.

## When geometry genuinely helps (the irreducible core)
- GEO-23 PASS — grounded ABSTENTION (decision 1.00 calibrated; bare-LLM control confabulates 100%).
- GEO-24 PASS — LLM-prior data-efficient for SEMANTIC-aligned structure (+0.12@k4); HARMFUL for arbitrary (-0.06).
- GEO-25 DEFLATION — named-entity retrieval is LEXICALLY solvable (string matcher ties geometry).
- GEO-25b PASS — semantic retrieval of DESCRIPTIONS (no shared token): geometry 0.80 vs lexical 0.10.
- GEO-26 INCONCLUSIVE — descriptive multi-hop confounded (description restated in fact).
- GEO-27 PARTIAL / GEO-27b PASS — ZERO-SHOT relational transfer to UNSEEN entities (0.81/0.88 vs random 0.51).
- GEO-28 NULL — compositional zero-shot (conjunction of attributes) collapses (0.53).
- GEO-29 PARTIAL — composition RECOVERS (0.69) as attributes are cleanly encoded; bounded, not fundamental.
- GEO-30 PASS — grounded UPDATABILITY: stored counterfactuals override prior 1.00, runtime edit flips.
- GEO-31 PASS — clean NON-LEXICAL multi-hop (real epithets): geometric 1.00 vs lexical 0.10.
- GEO-32 PARTIAL / 32b — integrated agent; abstention needs per-KB CALIBRATION (relevance != answerability).
- GEO-33 PASS — focus-term answerability verification (in-domain-unanswerable) 1.00.

## Grounded generation (small LLM) + reproducibility
- GEO-34 PASS — grounded GENERATION: 0.5B LLM follows store over prior (1.00 vs 0.00), abstains vs confabulates.
- GEO-35 PASS — MULTI-HOP grounded generation over private facts (1.00 vs bare 0.00).
- GEO-36 PASS — findings REPLICATE on all-mpnet-base-v2 (model-robust; improve to 1.00 / 0.88).
- GEO-37 PARTIAL / 37b PASS — DOMAIN-robust (materials-hardness zero-shot; tools semantic retrieval 0.90 vs 0.20).
- GEO-38 — generation FAITHFULNESS: 25% confabulation naive prompt, ELIMINATED (0.00) by explicit instruction.
- GEO-39 PASS — hardened GroundedQA acceptance 5/5 (clean).
- GEO-40 NULL / 40b PASS — per-hop cross-encoder re-rank recovers scale 2-hop 0.87->1.00 at 400.

## Deployability, multilingual, agent assembly
- GEO-41 PASS — contradiction detection (hybrid 0.94; pure geometry 0.50).
- GEO-42 PASS — relational JOIN queries (same-city/same-team, 1.00).
- GEO-43 FRAGILE / 43b — noisy store drops to 0.53; cause = character TYPOS x near-duplicate entities.
- GEO-44 PASS — character-trigram entity resolution recovers noisy retrieval 0.53->1.00.
- GEO-45 PASS — full hardened stack under noise (entity-res + multi-hop) 0.50->1.00.
- GEO-46 PARTIAL / 46b PASS — cross-lingual DE->EN (named 1.00, descriptive 0.67 vs English-only 0.25).
- GEO-47 PASS — temporal/versioned-fact reasoning (time-filter) 1.00 vs non-temporal 0.50.
- GEO-48 NULL / 48b PASS — intent ROUTING: geometry 0.56 (clusters by content), symbolic keywords 0.90.
- GEO-49 PASS — UnifiedReasoner auto-dispatch on mixed workload (1.00).
- GEO-50 PASS — schema-GENERAL (field-parameterized operators on people & products, 1.00 each).
- GEO-51 PASS — symbolic numeric COMPARISON operator 1.00 (closes GEO-20 comparison gap).
- GEO-52 PASS — contradiction hardened with same-subject pre-filter 0.94->1.00.
- GEO-53 PASS — symbolic NEGATION operator (set-complement) 1.00 (closes GEO-20 negation gap).
- GEO-54 PASS — UnifiedReasoner OPERATOR-COMPLETE (factoid/count/temporal/join/negate/compare, 1.00).
- GEO-55 PASS — conjunctive multi-constraint queries (AND-filter) 1.00 (a test-data error of mine, not the system).
- GEO-56 PARTIAL / 56b PASS — QA over UNSTRUCTURED prose (bi-encoder 0.67 -> re-rank 0.83; abstain 1.00).
- GEO-57 PASS — long-document QA holds at 30 sentences (0.86); re-ranking situational (helps under ambiguity).

## Organizing principle (every layer)
Geometry for SEMANTICS (relevance, entities, relations); SYMBOLS for STRUCTURE (route, count, negate,
compare, join, time-filter, contradiction). Auto-dispatch: query -> symbolic route -> geometric resolve ->
symbolic operate -> optional grounded generator. Modules: geometric_reasoner / grounded_qa /
unified_reasoner (+ demo, README, 14 pytest). Honest bottom line: real, robust, deployable, but NAVIGATES an
LLM's understanding — not new-as-method, not human-level AI. ~11 honest self-corrections en route.

## GEO-58 -> GEO-90 (deployment, deflation, validation, design)
- GEO-58/59 PASS — multi-hop over UNSTRUCTURED text (text-bridge; generic extraction, no domain list).
- GEO-60 PARTIAL / 61 — document GENERATION bottlenecked by prose retrieval; multi-passage 0.17->0.67.
- GEO-62 PASS — query-time conflict surfacing (set logic).
- GEO-63/64 — INTERACTIVE on CPU (~7ms/query, brute-force fine to ~200k facts; precision not speed is the limiter).
- GEO-65 PASS — ambiguous-reference surfacing (set logic).
- GEO-66 DEFLATION — relation LEARNING = a logistic probe (not geometrically special).
- GEO-67 — semantic retrieval works on a TINY 17M model (efficiency floor).
- GEO-68 DEFLATION — multi-hop COMPOSITION = a database JOIN (geometry only resolves the entry entity).
- GEO-69 DEFLATION — semantic matching is mostly DISTRIBUTIONAL (static word vecs 0.70 vs contextual 0.80).
- GEO-70b/71/72 — transformer's genuine add = COMPOSITIONAL/word-order (0.75 vs static 0.38); doesn't scale
  with size (mpnet 0.62); cross-encoder fixes it (0.88). Compositional story complete.
- GEO-73 PASS — engineering SYNTHESIS 3x naive RAG (0.92 vs 0.33); quantifies the contribution.
- GEO-74 PASS — validates on REAL data (periodic table).
- GEO-75 PARTIAL — does lookup+set-logic, NOT causal/counterfactual inference (leaks on why/what-if).
- GEO-76 PASS — question-type guard closes the inference leak (abstains).
- GEO-77 PASS — symbolic counterfactual SIMULATION (store-manipulable what-ifs).
- GEO-78 PASS — semantic matching extends to ABSTRACT concepts (0.83).
- GEO-79 PASS — grounding makes a small model reliable (0.17->1.00).
- GEO-80 CONFIRMED — grounding propagates WRONG retrievals (0.90->0.00); double-edged.
- GEO-81 — GIGO risk narrowed: abstention catches coverage gaps; residual = wrong PRIVATE fact (data quality).
- GEO-82 — LLM-prior fact-check tradeoff (catches public errors, breaks private/updatable use).
- GEO-83/84 PASS — realistic PERSONAL KB (0.90) + vague colloquial queries (0.88).
- GEO-85 PARTIAL — keyword kind-routing insufficient (0.90 ceiling).
- GEO-86 PASS — TRAINED kind-router fixes cross-type (1.00); shipped as LinearRouter.
- GEO-87 PARTIAL — naive best-practice integration HURTS (0.67 < 0.90): over-stacking compounds errors.
- GEO-88 PASS — SOFT scoping (small boost) is the right design (1.00); simpler is robust.
- GEO-89 PASS — mixed German+English KB + cross-language queries (1.00, multilingual model).
- GEO-90 PASS — quantitative operators range/sum/sort (operator coverage complete).
