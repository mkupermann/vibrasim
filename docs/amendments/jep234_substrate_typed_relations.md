# JEP-234 — can the substrate be a TYPED relational store (multiple relation types, no crosstalk)?

Pre-registered 2026-06-05 (BEFORE the run). JEP-232/233 showed the substrate stores is-a relations and chains them
for transitive inference. The Understanding Engine has SEVEN relation types (is-a, part-of, causal, …). This BET
asks whether the energy-based substrate can hold DIFFERENT relation types in one net and retrieve the right object
for a (subject, relation) query — i.e. serve as the engine's full typed relational memory, not just an is-a store.

## Method (no transformer; VSA role-binding + Hopfield key→value, both established, named as such)
- EnergyNet, single dense module, N=80. KEY=[0:40], VALUE=[40:80].
- Each concept and each RELATION TYPE → a fixed random ±1 code (length 40). A typed fact (subject, relation, object)
  → bipolar pattern `concat(subject_code ⊙ relation_code, object_code)`, where ⊙ is the Hadamard (element-wise ±1)
  product = VSA binding: the KEY is unique to the (subject, relation) pair. Store via `train_epoch`.
- RETRIEVE(subject, relation): clamp KEY = subject_code ⊙ relation_code, relax VALUE → nearest concept = the object.
- Mixed store: 4 facts each across 3 relation types {is-a, part-of, causal} = 12 typed facts. Seeds 42 & 7.

## Bars (locked pre-run)
| ID | Criterion | Bar |
|----|-----------|-----|
| J234a | Typed retrieval works | (subject,relation)→object recall ≥ 0.85 over all 12 facts (both seeds) |
| J234b | Relation type DISCRIMINATES | query a stored subject with a WRONG relation → returns the correct object < 0.20 of the time (both seeds) |
| J234c | Above an untrained control | untrained net: typed recall ≤ 0.40 (both seeds) |
| J234d | All three types equally served | per-type recall ≥ 0.85 for is-a AND part-of AND causal (both seeds) |

PASS = J234a–d → the substrate is a TYPED relational store: it holds multiple relation types in one net, the
relation binding discriminates, no type is starved. NULL (honest): J234a fails → binding overloads the shared
capacity; J234b fails → the relation code does not discriminate (subject alone drives retrieval); J234d fails →
one type dominates. No post-hoc threshold tuning.

## Prediction (locked BEFORE run) [predict-calibrate]
🔮 The Hadamard bind subject⊙relation yields well-separated random ±1 keys (different relations → different keys
for the same subject), so J234a PASS (12 ⊂ ~20 capacity → recall ≥ 0.85, ~1.00) and J234d PASS (types symmetric by
construction). J234b PASS: a wrong-relation key is an unrelated random vector → retrieves an unrelated object, hits
the correct object only at chance (~1/n ≪ 0.20). J234c control fails (≤0.40). RISK (counter-cases run in-rung per
error-class 11): (i) capacity is now over the TOTAL fact count (12), not per-type — within the ~20 cliff, fine;
(ii) if two facts share a subject across types, their keys must stay separated — the relation code ensures this
ONLY if relation codes are well-spread (verify is-a/part-of/causal codes are near-orthogonal). Net: typed store
works within capacity; established role-binding + CAM, no novelty — the value is the demonstrated typed substrate
memory completing the JEP-232/233 relational-substrate arc.

## RESULT (2026-06-05): PASS — all 4 bars, as predicted

| seed | typed recall | wrong-rel hit | control | per-type (is-a / part-of / causal) |
|------|--------------|---------------|---------|------------------------------------|
| 42 | 1.00 | 0.00 | 0.00 | 1.00 / 1.00 / 1.00 |
| 7  | 1.00 | 0.04 | 0.00 | 1.00 / 1.00 / 1.00 |

- **J234a ✓** — (subject, relation)→object retrieval over 12 mixed-type facts = **1.00**, both seeds.
- **J234b ✓** — querying a stored subject with a WRONG relation returns the original object only **0.00–0.04** of
  the time (≈ chance): the `subject ⊙ relation` bind genuinely **discriminates** relation type.
- **J234c ✓** — untrained control **0.00**: the trained attractors carry the typed facts.
- **J234d ✓** — is-a, part-of, causal each **1.00**: no type is starved; symmetric by construction, confirmed.

**FINDING — the JEP-232/233/234 arc complete:** the energy-based substrate is a full **typed relational memory +
inference engine** for the Understanding Engine's relations:
- **store** (J232) — is-a facts as content-addressable key→value attractors, capacity ~20/module (sharp cliff);
- **chain** (J233) — transitive multi-hop inference by iterated retrieval, raw or cleaned, 1.00 to 3 hops;
- **type** (J234) — multiple relation types in one net via VSA role-binding, no crosstalk, all types served.

This is the concrete answer to Michael's recurring "where is the substrate in the chain?": the Understanding
Engine's relational knowledge AND its reasoning CAN live in the energy-based substrate (`world.energy.EnergyNet`),
not only in Python dicts. Established methods throughout (Hopfield content-addressable memory + iterated associative
recall + VSA Hadamard role-binding), each named as such — **no novelty**; the contribution is the demonstrated
end-to-end CONNECTION and its measured envelope (bounded by the ~20-fact/module capacity, scalable linearly by
adding modules/units). Verdict: **PASS.**
