# Pattern: multi-domain learn-from-sources (what the engine extracts + reasons about from prose, JEP-155..212)

The understanding engine (`world/understanding.py`, NO transformer) reads encyclopedic prose and builds a
multi-domain knowledge base. The complete, measured picture of what `read()` extracts, how the domains are kept
separate, how each is queried/communicated, and how consistency is checked — the reusable characterization.

## What `read(passage)` extracts (one call, all domains)
| domain | surface pattern(s) | stored as | query | the GUARD that keeps it separate |
|--------|--------------------|-----------|-------|----------------------------------|
| **is-a** (taxonomy) | 'X is a Y', 'X is a kind of Y', 'Xs are Y', 'Y such as A and B', appositive, 'which is a' | parents DAG | `is_a`, multi-hop | bare-NP + plural-noun/mass guard; adjective predicates skipped |
| **part-of** (mereology) | 'X is part of Y', 'X has Y' | part_of graph | `part_of` | excludes 'has N' (numeric) first |
| **causal** | 'X causes Y', 'X leads to Y' | causes graph | `causes_effect` | — |
| **spatial** | 'X is located/situated/found in Y' | part_of (containment) | `part_of` | matched before generic copula |
| **comparison** | 'X is ADJ-er than Y' | `_orders[comp]` | order Q&A, transitive | requires 'than' |
| **temporal** | 'X (verb) before/after Y' | `_orders['before']` (after=inverse) | 'did X happen before Y?' | matched before is-a |
| **quantitative** | 'X has N Y' (digit or number-word) | `num_attrs[(X,attr)]` | 'how many Y does X have?', numeric compare | matched BEFORE 'has' part-of |
| **OPEN relations** | any recurring connective (>=2x) not among the fixed ones | `facts` + VSA + `learned_rels` | `relation_true`, 'what is the \<rel\> of Y?' | `is_fixed` excludes the fixed connectives |

The ORDER of the handlers is the key design: more-specific / numeric / temporal patterns are matched BEFORE the
generic copula and 'has' patterns, so the domains never collide (verified by the multi-domain integration test and
6000-passage fuzz, JEP-211/205).

## Reasoning + communication, per domain
Every domain composes with the full reasoning faculty set and with grounding (perceive -> symbol -> reason). The
RELATION-INTERACTION matrix (is-a x part-of/causal/comparison, each with correct distinct semantics + a leak guard)
governs cross-domain inference. Communication: `respond()` answers Q&A in every domain; `describe()` renders a
concept's is-a/part-of/causal/numeric profile; `summarize()` overviews a whole source and flags its inconsistencies.

## Consistency across ALL domains
A self-contradicting source is detected and explained: TAXONOMY (an is-a that conflicts with an inherited negative),
QUANTITIES (conflicting counts for one attribute), TEMPORAL (an impossible-timeline cycle). `consistency_audit()`
reports all three; `summarize()` surfaces them.

## Self-extensibility
`read_open()` (folded into `read()`) AUTO-INDUCES new relation types from recurring patterns, so the engine is not
limited to its built-in relations — it learns new ones from the text, then extracts/queries/answers-questions/
communicates them.

## The honest boundary (the no-transformer wall)
Everything above needs a CONSISTENT surface pattern. Paraphrase variation, arbitrary phrasings (the NL long tail),
dense logic/argument prose (the GENRE gate), absolute dates/units/arithmetic, and sentence-start proper-noun
detection are out of scope — they need learned extractors (forbidden) or external resources. Established methods
throughout (Hearst patterns, OpenIE-style induction, transitive closure, VSA role-binding, consistency/truth
maintenance); named; no novelty. The reusable wisdom is the domain-separation-by-handler-ordering + the unified
read->reason->communicate->check-consistency pipeline across domains.
