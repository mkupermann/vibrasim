# JEP-201 — self-extensible reading: read_open() auto-induces open relations from a passage

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 read_open() collects (subject, connective, object) triples, finds connectives recurring >=2x (not among the 5
  fixed relations), auto-induces those templates and extracts all instances. RISK: false-inducing on incidental
  repeated phrases (mitigated by >=2 threshold + fixed-relation exclusion).

## Result — PASS (HIT)
read_open() makes the engine SELF-EXTENSIBLE from prose: it collects subject-connective-object triples from a
passage, excludes connectives that are one of the 5 FIXED relations (is-a copula, 'has', part-of, causes, located-in,
'...than'), and for connectives recurring >=2 times auto-induces the template (learn_relation) + extracts all
instances. On a mixed passage:
  'Paris is the capital of France. London ... England. Rome ... Italy. Einstein discovered relativity. Darwin
   discovered evolution. A dog is a mammal. A cat is a mammal.'
-> auto-induced {'is capital of': 3, 'discovered': 2}; the fixed-relation sentences (dog/cat is-a mammal) were NOT
mis-treated as open relations. relation_true('rome','is capital of','italy') True; relation_true('darwin',
'discovered','evolution') True; a NEW instance extracts ('Berlin is the capital of Germany') and queries True. A
passage with NO repeated pattern induces nothing ({}). So the engine now AUTO-DISCOVERS new relation types defined by
repeated examples in a passage, with NO prior knowledge of the relation and NO transformer — extending JEP-200
(manual learn_relation) to automatic induction from prose. Honest limit (the no-transformer wall): needs a CONSISTENT
recurring surface pattern; paraphrase variation and single-occurrence relations are out of scope. 70/70 regression
tests green (+1). Prediction HIT; tally 90/117. Established (OpenIE-style pattern induction, frequency-thresholded);
named; no novelty.
