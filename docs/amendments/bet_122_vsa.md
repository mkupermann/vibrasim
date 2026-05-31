# BET-122 — Vector-Symbolic Composition & Generalization (new substrate math)

Pre-registered: 2026-05-31. Goal: communicate in language => need GENERALIZATION
(compose meaning for inputs never seen), which memorization (n-gram/least-squares)
cannot do. New mathematics on the substrate: Vector-Symbolic / Hyperdimensional
algebra on the ±1 codes (world/vsa.py: bind = elementwise product, bundle =
sign-sum, cleanup = the energy attractor). NOT an LLM, NOT a transformer.

## Method
Roles {SUBJ,VERB,OBJ} and a vocabulary are random ±1 hypervectors (D large). A
"sentence" (s,v,o) is encoded as bundle(bind(SUBJ,s), bind(VERB,v), bind(OBJ,o)).
Query a role by unbinding + clean-up: cleanup(bind(F, role)). Test retrieval on
random sentences, and CRUCIALLY on NOVEL word combinations never stored — if it
works equally, composition is systematic (generalization), not lookup.

## Bars (locked pre-run)
| ID | Criterion | Bar |
|----|-----------|-----|
| T122a | Binding works | role retrieval accuracy on random sentences >= 0.95 (D=4000, vocab 30/role) |
| T122b | Generalizes | accuracy on NOVEL (unseen) combinations equals the seen accuracy (>= 0.95) — systematic composition |
| T122c | Capacity | still >= 0.90 with a larger vocabulary (60/role) |
| T122d | Control FAILS | randomized (no binding structure) retrieval < 0.10 |

PASS = T122a-d. PASS = the substrate composes structured meaning and GENERALIZES
to novel combinations with new (hypervector) mathematics, no transformer — the
capability memorization lacks and the foundation for autonomous language.

## RESULT (2026-05-31): PASS — but HAND-DESIGNED composition, not emergent

role retrieval 1.000, novel combinations 1.000, vocab-60 1.000, control 0.038.
Vector-symbolic algebra on the substrate composes structured meaning and handles
arbitrary (novel) combinations perfectly, no transformer. T122a-d all pass.

IMPORTANT CAVEAT (Michael's correction): this composition is ENGINEERED by hand —
the roles and the bind operation are designed, not discovered. The substrate does
not generalize BY ITSELF here; it executes a hand-built scheme. The real goal is
EMERGENT self-generalization: a substrate-native mechanism the substrate learns on
its own. BET-123+ is the experiment series toward that. BET-122 stands as a useful
clean-up/composition primitive, not as the answer.
