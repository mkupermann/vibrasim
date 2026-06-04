# A proper LEARNING + UNDERSTANDING method on the PC, with geometric ML/LLM — the answer

Written after the autonomous EQMOD-3 run (GEO-1 → GEO-73), every claim a pre-registered experiment with
controls. Honest verdicts; established methods named as such. This is the Phase-2 deliverable, replacing the
abandoned EQMOD physics substrate (which Phase-1 proved computationally empty — see STRATEGIC_ANSWER.md).

## Short answer
**Yes — a working, fast, deployable learning+understanding TOOLKIT runs on your PC.** Honest framing (after
rigorous self-testing, GEO-66/68/69/70b/73): it is a *neuro-symbolic SYNTHESIS of established methods*. An LLM
embedding does SEMANTIC MATCHING (resolving meaning to the right entry — mostly distributional, with a modest
genuine compositional/word-order add from the transformer); everything built on top is classical — composition
= database joins, learning = a linear probe, aggregation/negation/comparison = set logic, grounding = RAG with
abstention, plus a thin small-LLM generator. No single piece is novel, but the SYNTHESIS genuinely matters
(GEO-73: 3x naive RAG on a mixed workload). It is sound, integrates end-to-end, and is precisely bounded — NOT
open-domain NLU, NOT human-level AI, NOT a new algorithm; a real, useful engineering synthesis, honestly scoped.

## What the method IS (one entity = one point in a learnable concept space)
1. **Concept space** — a real sentence-embedding model (all-MiniLM-L6-v2, 384-dim) provides prior semantic
   geometry for free, on CPU. (GEO-5,15)
2. **Understand by geometry** — questions retrieve their answer facts; relations are consistent OFFSETS;
   multi-hop questions are answered by *iterative* retrieval + symbolic bridge chaining. Robust to 100
   distractor facts and to paraphrased (non-template) questions. (GEO-7,15,16,17)
3. **Learn new knowledge** (NB: this is ordinary linear ML on the embeddings, NOT geometrically special —
   a logistic probe does identically, GEO-66) —
   - *structured* knowledge: train a linear readout (offset/TransE ≈ logistic probe) and generalize to
     derived facts by composition (grandparent from parent). (GEO-12)
   - *relations from few examples*: few-shot linear readout (GEO-6); zero-shot transfers to unseen entities,
     a property of the EMBEDDINGS not the framing (GEO-27b/66).
   - *arbitrary* facts: a key-value MEMORY (no readout generalizes these — GEO-10,11).
4. **Integrate prior + new knowledge without conflict** — per entity, concatenate a FROZEN LLM block
   (semantics) with a TRAINABLE structure block (new relations). Semantics preserved exactly (drift 0.00)
   while new structure trains. (GEO-21)
5. **Aggregate / negate / compare** — a thin SYMBOLIC layer over geometric resolutions (count, filter,
   `>`), because pure geometry cannot do these. (GEO-18,20)
6. **End-to-end** — learn a relation few-shot → apply to unseen entities → chain by retrieval → symbolic
   aggregate, all on held-out data. (GEO-19, milestone)
7. **Auto-dispatching agent** — one agent symbolically ROUTES a query (factoid/count/temporal/join/
   negation/comparison), GEOMETRICALLY resolves entities, applies the SYMBOLIC operator; schema-general via
   field-parameterized operators (GEO-49/50/54, 1.00 across schemas, operator-complete). Three usable
   modules: `geometric_reasoner` (primitives), `grounded_qa` (grounded generation), `unified_reasoner`.
8. **Unstructured DOCUMENTS too (not just structured KBs)** — `add_document()` sentence-splits raw prose;
   the layer does retrieval, abstention, and single/multi-hop QA over free text (GEO-56/58/59), including
   GENERIC entity-bridge extraction (no domain list). Honest envelope: prose retrieval is the limiter
   (~0.67 bi-encoder), lifted by re-ranking (0.83) and multi-passage context (document generation 0.17->0.67,
   GEO-56b/61); structured retrieval is EXACT so structured QA/generation (1.00) is far more reliable than
   document QA (~0.7-0.8). Abstention keeps document QA honest (1.00 on unanswerable — no silent hallucination).

## The precise BOUNDARY (what geometry does vs what needs symbols/memory/training)
| task | geometry alone | resolution |
|------|----------------|------------|
| named-entity retrieval / multi-hop chaining | STRONG (≈1.0) but LEXICALLY solvable (GEO-25) | — |
| semantic retrieval (descriptions), analogy | STRONG, NOT lexical (GEO-25b 0.80 vs 0.10) | — |
| semantic MULTI-HOP (epithets, real knowledge) | STRONG, NOT lexical (GEO-31 1.00 vs lexical 0.10) | — |
| relations linear in embedding space | STRONG (few-shot) — but = a logistic probe, not geometric (GEO-66) | — |
| arbitrary unstructured new facts | FAILS (random offsets) | key-value MEMORY |
| antonyms / fine sense distinctions | WEAK (0.54) | — |
| negation ("not in Europe") | WEAK (F1 0.50) | symbolic filter → 1.00 |
| comparison ("larger population") | BELOW CHANCE (0.29) | symbolic compare |
| counting / aggregation | FAILS (0.00) | symbolic count → 1.00 |
| open-domain NLU | OUT OF SCOPE | needs a large LLM |
| grounded GENERATION (follow store, abstain) | DONE via small LLM (GEO-34) | geometric retrieve+verify + Qwen-0.5B |
| MULTI-HOP grounded generation (private facts) | DONE (GEO-35 1.00 vs bare LLM 0.00) | geometric chain feeds generator |

## When does the LLM geometry HELP learning? (GEO-24)
The LLM prior is not universally good. For learning a NEW relation that correlates with semantics (a size
ordering over animals), LLM-init is a data-efficient prior: +0.12 accuracy over random-init at 4 examples,
the gain largest when data is scarce. For an ARBITRARY relation (random permutation), LLM-init is WORSE than
random (-0.06): the semantic geometry misleads. Design rule: LLM-init for semantically-aligned structure;
random init (or the orthogonal struct-subspace, GEO-21) for arbitrary structure. This is the mechanism
behind why geometry can read known relations but not arbitrary new ones.

## Honest caveats
- GEO-15–19 saturate at 1.00 because they use small, clean, well-known entities where MiniLM is excellent.
  They prove the method is **sound and integrates**, not that NLU is solved. Scale was measured (GEO-22):
  1-hop holds (0.98 at 400 facts) but 2-hop falls to 0.87 as the pool grows and error compounds across hops.
  Usable to a few hundred facts / 2-3 hops on CPU. The degradation is MITIGABLE (GEO-40b): a cross-encoder
  re-ranker applied PER HOP recovers 2-hop accuracy from 0.87 to 1.00 at 400 facts, extending the envelope at
  modest latency. Real ambiguous entities (not synthetic names) would still degrade further.
- Every reasoning primitive here (TransE, MDS, word-vector analogy, RAG-style retrieval, key-value memory,
  neuro-symbolic split) is an ESTABLISHED method. The contribution is the honest synthesis on a PC + a
  precise boundary map, NOT a new algorithm.
- This reads/uses an existing LLM's geometry; it does not replace the LLM. It is a generator-free reasoning
  layer ON an embedding model.

## Does the geometry ADD value over just using the LLM? (GEO-23) — yes, grounding
A generative LLM confabulates: asked the capital of a country it has no fact for, it invents one. The
geometric retrieval method ABSTAINS instead — calibrated similarity threshold separates answerable (sim
0.87) from unanswerable (0.53) cleanly, giving decision accuracy 1.00 and abstain-on-unanswerable 1.00,
while the no-abstention control is confidently WRONG on 100% of unanswerable questions. So the value-add over
raw generation is concrete: **grounded, hallucination-free reasoning that knows what it doesn't know**, plus
updatable memory (new facts without retraining) and composable trainable structure. The method is a
controllable reasoning layer ON an LLM, not a replacement for it.

**Updatability (GEO-30):** with a store of facts that CONTRADICT common knowledge, grounded retrieval returns
the STORED answer 100% (overriding the prior) and a runtime edit flips the answer instantly — facts update by
editing one entry, no retraining. Grounding + abstention + updatability are the concrete practical edges over
using a frozen LLM's parametric knowledge directly.

**Grounding's honest limit (GEO-32b):** similarity-threshold abstention reliably rejects OUT-OF-DOMAIN
questions (low similarity) but NOT in-domain-but-unanswerable ones (e.g. "Who is the CEO?" when no CEO is
stored sits at sim 0.43, close to the role facts). Calibration can't separate these without rejecting valid
in-domain queries — that needs answer VERIFICATION (does the retrieved fact entail an answer?), not just a
retrieval threshold. Geometry filters relevance, not answerability.

**Resolved (GEO-33):** robust grounding needs TWO cheap checks — (1) retrieval-similarity rejects out-of-
domain questions; (2) FOCUS-TERM existence verification against the structured store rejects in-domain-but-
unanswerable ones ("CEO" is not a stored role -> abstain), balanced accuracy 1.00. Geometry filters
relevance; the structured store verifies the focus exists. Together: hallucination-free QA that abstains
correctly in both failure modes.

## How to build it on your machine
CPU is enough (sentence-transformers + numpy). Pipeline: embed your facts once → store with symbolic labels
→ at query time do geometric retrieval/chaining for "what/which/where", drop to the symbolic layer for
"how many / not / bigger". Train a small structure block only when you have NEW structured relations to
generalize. Your AMD GPU is unused (no CUDA / no torch-directml on Py3.13) but unnecessary at this scale.

## CRITICAL honest caveat — what the geometry actually adds (GEO-25/25b)
Adversarial self-review with a trivial lexical (token-overlap) baseline showed that the named-entity
retrieval/QA/grounding tasks are LEXICALLY SOLVABLE: a dumb string matcher also scores 1.00, because each
entity NAME is a unique token shared by question and fact. So those headline numbers demonstrate the
pipeline runs, NOT that the LLM geometry is necessary for them. The geometry's genuine, irreducible
contribution shows only when the lexical shortcut is removed: on DESCRIPTIVE queries sharing no token with
the answer ("the country famous for the Eiffel Tower" -> "The capital of France is Paris"), geometry scores
0.80 vs lexical 0.10 (chance). The real value of geometry-over-an-LLM is SEMANTIC matching — descriptions,
paraphrases, analogies, relation offsets, and a data-efficient prior for semantically-aligned structure
(GEO-5/6/24/25b) — not the templated retrieval numbers. Stated plainly so the deliverable is not read as
overclaiming.

## The single strongest honest result: zero-shot relational transfer (GEO-27b)
The cleanest evidence that the geometric view has irreducible value: a size-ordering relation trained on
some animals transfers to animals NEVER seen in any training pair at 0.81, while the same method with random
initial vectors is at chance 0.51. The LLM's semantic geometry positions unseen entities so a learned
relation orders them with zero examples of them — genuine zero-shot generalization (understanding, not
memorization), and irreducible (random init cannot do it). This, plus semantic resolution of descriptions (GEO-25b), genuinely SEMANTIC multi-hop reasoning over
real-world epithets (GEO-31, 1.00 vs lexical 0.10), and data-efficient structure learning (GEO-24), is where
"geometric" genuinely earns its name — distinct from the lexically-solvable named-entity numbers.

## Honest limit of the irreducible edge: composition of zero-shot attributes (GEO-28)
Single-relation zero-shot transfer is reliable (GEO-27b), but composing TWO zero-shot-transferred attributes
("large AND predator" on unseen animals) collapses to chance (0.53) even though each attribute alone is
0.75-0.78: noisy zero-shot scores compound under conjunction. So geometric zero-shot is per-relation, not
robustly compositional — a concrete gap from human-level understanding. This is NOT fundamental, though
(GEO-29): with more entities and a cleanly-encoded attribute, composition recovers to 0.69 (vs random 0.52)
— the conjunction is bounded by the WEAKEST per-attribute accuracy, so it rises as each attribute is encoded
more cleanly. Clean composition needs trained structure (GEO-7/12) or well-encoded attributes, not noisy
zero-shot transfer.

## Reproducibility (GEO-36)
The genuinely-geometric core (semantic descriptive retrieval, zero-shot transfer) REPLICATES on a different,
architecturally-distinct embedding model (all-mpnet-base-v2): semantic retrieval improves to 1.00 (vs lexical
0.10), zero-shot transfer to 0.88. The findings are model-robust, not MiniLM artifacts; a stronger model
gives cleaner results (use mpnet for quality, MiniLM for speed). They are also DOMAIN-robust (GEO-37/37b):
zero-shot transfer replicates on materials-hardness (0.78 vs random 0.54) and semantic retrieval on tools
(0.90 vs lexical 0.20) — robust across geography, animals, materials, and tools.

## Deployability caveat — noisy stores (GEO-43/43b)
The clean-store 1.00s assume clean text and disambiguated entities. Under realistic noise, 1-hop drops to
0.53. Diagnosis: embeddings are ROBUST to paraphrase (a strength) and even to near-duplicate names when text
is clean (1.00), but FRAGILE to character-level TYPOS (0.73 at 10% typo rate); typos x near-duplicate
entities compound badly (the 0.53 case). Deploy with a front-end: spell/character normalization + exact
entity-ID resolution for identity (use embeddings for relevance, exact keys for who-is-who). Without it, the
headline accuracies are optimistic. VALIDATED (GEO-44): a character-trigram fuzzy entity-resolution
front-end fully recovers noisy-store accuracy (0.53 -> 1.00) — so the system IS deployable on messy data with
this cheap front-end (embeddings for relevance, fuzzy/exact name matching for identity). End-to-end validated under noise:
the full multi-hop stack with the front-end recovers from 0.50 to 1.00 on a noisy store (GEO-45).

## Full auto-dispatch architecture (GEO-48/48b)
The multi-capability system self-dispatches: query -> SYMBOLIC intent router (keywords, 0.90; geometry routes
intent poorly at 0.56 because embeddings cluster by content not operation) -> GEOMETRIC resolver/gather
(relevance, entities, relations) -> SYMBOLIC operator (count/compare/join/time-filter/contradiction) ->
optional grounded GENERATOR. The recurring principle at every layer: geometry for semantics, symbols for
structure.

## Performance and scale (GEO-63/64)
Interactive on CPU: ~7ms/query (~150 q/s), ~24ms with re-ranking. Brute-force retrieval stays interactive to
~200,000 facts (12ms/query) — speed is NOT the scale limiter; retrieval PRECISION is (multi-hop degrades by a
few hundred facts, GEO-22, fixed by re-ranking GEO-40b). So: hold 100k+ facts and query in real time; invest
in re-ranking/better embeddings for accuracy, and an ANN index only beyond ~1M facts.

## Honest deflation — what "geometric" genuinely means (GEO-66)
Tested head-to-head: the geometric relation LEARNER (offset/ranking/TransE) is IDENTICAL to a plain logistic
regression on the same embeddings (few-shot and zero-shot both equal). So the geometric framing adds nothing
for LEARNING relations — the value is the LLM embeddings + a linear readout. What IS irreducibly geometric is
the training-FREE vector arithmetic: retrieval, analogy-by-offset, and multi-hop composition (a linear probe
can't do these). Honest refined description: the system is "LLM embeddings + linear readouts + symbolic
operators"; the embedding geometry genuinely powers training-free retrieval/analogy/composition, while the
learned-relation parts are ordinary linear ML — no geometric magic there.

## Maximally-sharpened honest core (GEO-66 + GEO-68 + GEO-69)
Two rigorous deflations narrowed the geometric contribution precisely: relation LEARNING = a logistic probe
(GEO-66), and multi-hop COMPOSITION on structured data = a database JOIN (GEO-68; geometry only resolves the
entry entity). What remains is SEMANTIC MATCHING — resolving meaning (descriptions, epithets, paraphrases) to entities —
but even THAT is mostly DISTRIBUTIONAL semantics: static word vectors do ~0.70, the transformer adds only
+0.10 (GEO-69). So keyword semantic matching is decades-old distributional semantics, modestly LLM-enhanced. BUT the
transformer DOES add one irreducible thing static vectors can't (GEO-70b): COMPOSITIONAL/word-order encoding
(roles, who-did-what-to-whom; 0.75 vs static 0.38). So the LLM's genuine value = modest distributional boost +
real compositional/syntactic understanding — composed with classical machinery for all the reasoning. Honest one-liner: **the system = LLM semantic matching + classical
symbolic/database reasoning + RAG grounding + a thin generator.** The LLM's irreducible job is mapping meaning
to the right entry; the reasoning on top is classical. Real, useful, entirely established methods, precisely
scoped — not new-as-method, not human-level AI.

## The synthesis genuinely matters (GEO-73) — quantified
Although every piece is established, the ENGINEERING SYNTHESIS triples accuracy over naive bi-encoder RAG on a
realistic mixed workload (0.92 vs 0.33): entity-resolution fixes typos, multi-hop fixes chained questions,
symbolic operators fix count/compare, grounded abstention fixes unanswerables — naive RAG fails all of these.
So the value is real at the SYSTEM level even though no single component is novel. THAT is the honest
contribution: a rigorous, deployable synthesis of established methods, 3x naive RAG, precisely scoped.

## Bottom line
Phase-1 verdict was "the physics substrate has no computational value." Phase-2 verdict is the constructive
counterpart: **redefining the substrate as a geometric concept space over an LLM yields a real, working,
honestly-bounded learning+understanding method that runs on your PC** — neuro-symbolic, generator-free for
reasoning, with every capability and every limit measured. The deliverable, per the charter, is a
deadlock-breaking process with an honest map of what is and isn't reachable.
