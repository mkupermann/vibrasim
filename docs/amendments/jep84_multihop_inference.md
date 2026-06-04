# JEP-84 — where retrieval ends and understanding begins: multi-hop inference on the substrate

## Why (waypoint 2 toward Michael's "learn from sources WITH UNDERSTANDING")
JEP-83 showed the substrate RETRIEVES from a source. Understanding requires INFERENCE the source does not state
literally: if "A is B" and "B is C" appear in different passages, can the system answer "is A a C?" — a 2-hop
chain never written as one sentence. This is the honest line between retrieval and understanding. Tested directly,
with a real chance of NULL.

## Setup
- Corpus states facts as SEPARATE single-hop passages (e.g. "A poodle is a dog." / "A dog is an animal."), never
  the 2-hop conclusion ("A poodle is an animal.").
- Bare-substrate baseline: the world.knowledge VSA retrieval system (JEP-83) asked the 2-hop question directly.
- Substrate + structure: parse retrieved single-hop facts into the concept reasoner / a transitive IS-A graph
  (the substrate's OWN structured primitive) and answer by transitive closure.

## Pre-registration (locked BEFORE run)
- (i) BARE retrieval on 2-hop questions: EXPECTED to be poor (it has no inference) — report accuracy; if it is
  high (>=0.8) that itself is a finding.
- (ii) Substrate + structured transitive-closure layer: PASS if 2-hop IS-A accuracy >= 0.90 AND >> bare retrieval
  by >= 0.3. This would show understanding-by-inference is reachable WHEN facts are parsed into the substrate's
  structured primitive (not from raw retrieval alone).
- Honest reading either way: a gap means raw retrieval != understanding (the structure layer does the inference);
  a NULL on (ii) means even with structure the parse/closure is unreliable. Established (transitive closure,
  distributional retrieval), named; no novelty. The HONEST point is locating the retrieval->understanding line.

## Result — PASS (locates the retrieval->understanding line)
- 2-hop+ IS-A queries: 14 true, 14 false (conclusions NEVER stated in the source).
- (i) BARE VSA retrieval accuracy = **0.429** (chance — retrieval cannot infer).
- (ii) substrate + structured transitive closure = **1.000**.

**VERDICT: PASS.** Multi-hop inference is reachable WHEN single-hop facts are parsed into the substrate's
structured IS-A primitive: 1.00 on conclusions never written, vs 0.43 bare retrieval. The line is located:
RETRIEVAL alone does not infer; STRUCTURE over retrieved facts does — the inference is the structure layer's, not
the corpus'. HONEST BOUNDS (the substance): the "understanding" is transitive closure over PARSED facts — it needs
reliable parsing of source sentences into relations (here a regex; real text needs robust relation extraction) and
only handles IS-A chains. Arbitrary inference, robust parsing, and LEARNING the structure (vs hand-coding it)
remain the open frontier. Established (transitive closure, distributional retrieval), named; no novelty. Waypoint 2
of "learn from sources WITH understanding": the inference mechanism works; the parse + learned-structure gaps are
what the multi-year frontier is made of.
