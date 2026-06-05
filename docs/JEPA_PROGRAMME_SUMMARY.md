# EQMOD-4 (JEPA / EBM / MPC) — programme summary

Michael's directive: "model predictive control and energy based models in joint based embedding" + "We will
find a way for Human level understanding." This is the honest synthesis of the JEP rungs. Charter:
docs/JEPA_PROGRAMME.md. Substrate-benefit analysis: docs/SUBSTRATE_FOR_JEPA.md.

## What was asked
Pursue JEPA (LeCun: predict in representation space), Energy-Based Models (LeCun/Hinton: inference = argmin
energy), and Model Predictive Control (plan by rolling a model forward to a low-energy goal), and find how the
vibrasim SUBSTRATE is a genuine benefit for this.

## Rungs (all pre-registered; honest verdicts)
| rung | verdict | finding |
|------|---------|---------|
| JEP-1 | PARTIAL | toy JEPA predicts masked rep 0.20 > baselines ~0, but weak standalone. |
| JEP-2 | NULL (informative) | energy-based MPC with a RANDOM encoder fails (0.07 ~ random): random rep -> uninformative energy. The reason JEPA must LEARN representations. |
| JEP-3 | PARTIAL | hand-rolled backprop-free predictor too weak to plan (next-cell acc 0.30). |
| JEP-4 | **PASS** | substrate-native EBM: LOCAL Hebbian learning + RELAXATION inference (no backprop/optimizer); recall 0.905@load0.1N, energy monotone, capacity ~0.14N (Hopfield). |
| JEP-5 | **PASS** | a LOCALLY-LEARNED rep (contrastive temporal-coherence, no backprop) makes energy meaningful (Spearman 0.88) -> energy-based MPC 0.08 -> 0.90. Confirms JEP-2 diagnosis. |
| JEP-6/6b/6c | PARTIAL/NULL | PC tracks backprop on easy regression (0.19/0.19, 0.12/0.12) but grid task confounds (extrapolation; classification=memorization, held-out 0.00; PC lags on hard softmax). |
| JEP-6d | **PASS** | on a well-posed iid task (two-moons), local predictive coding MATCHES backprop (test 0.97 vs 0.98). The substrate-compatible local-learning path for the JEPA predictor is validated. |
| JEP-8/8b | NULL | simple contrastive rule learns POSITIONAL not geodesic structure (tracks Euclidean>geodesic even in serpentine); greedy 1-step nav also invalid for mazes. |
| JEP-9 | PARTIAL | Successor Representation is locally learnable (TD vs closed-form corr 1.00) + tracks geodesic>euclidean>contrastive (right trend), but greedy maze nav metric invalid. |
| JEP-10/10b | **PASS** | SCALING: predictive coding (local, no backprop) matches backprop on full MNIST (PC 0.947 vs bp 0.968, within 0.03) on 16 CPU threads. Local learning is not toy-only. |
| JEP-10c | **PASS** | AMD GPU usable for INFERENCE via DirectML (x3.51 @200k batch, exact-match acc). Training stays CPU (no AMD PyTorch-train path on Win/Py3.13). |
| JEP-11 | **PASS** | SR-as-VALUE-function (local TD) navigates a maze PERFECTLY (1.00) vs Euclidean-greedy 0.03; closes JEP-8/9 (failure was the planner, not the rep). TD/eligibility-traces = substrate BTSP primitive. |
| JEP-12/12b/12c | **PASS** (12c) | GROUNDING from noisy high-dim PERCEPTION (no privileged indices): perception (discriminate+denoise) + world model (local TD SR) + value planning -> optimal nav 1.00. Lesson: perception must DISCRIMINATE, value must be SMOOTH - separate modules; denoise or noise compounds. |
| JEP-13/13b/13c | PARTIAL | ABSTRACTION via spectral basis: compact task-agnostic proto-value functions reconstruct novel-goal value at R^2 0.90 @1/8 size (>> random) = strong REPRESENTATION abstraction; but greedy CONTROL needs full rank (compression-vs-control tradeoff; high R^2 != good policy). |
| JEP-14/14b | **PASS** (14b) | TRANSFER boundary of the SR: REWARD revaluation instant (V=M@r, 1.00, zero relearning); TRANSITION change makes cached SR stale (0.63) until relearned (1.00). Reward-general, transition-specific (Momennejad 2017). [14 caught a tree-maze design flaw -> fixed with loops in 14b.] |
| JEP-15/15b | **PASS** (15b) | MODEL-BASED advantage: explicit locally-editable transition model + MPC replanning recovers from transition changes INSTANTLY (mean 1.00, zero relearning) vs cached SR stale 0.81. Complementarity: SR=reward changes, model+MPC=transition changes. |
| JEP-16 | **PASS** | CAPSTONE integrated agent: from noisy perception (no privileged indices) one agent navigates (1.00), instantly retargets (1.00), and adapts to blocked passages via local model edit + MPC replan (1.00). Perception + world model (BTSP/SR) + value planning + model-based adaptation, all local/backprop-free. |
| JEP-17 | **PASS** | RELATIONAL REASONING: SR/cognitive-map does transitive inference (A<B,B<C => A<C) from local adjacency, 1.00 incl internal pairs. (Honest: symbolic-distance-effect NOT shown, ceiling - retracted.) Bridge navigation->reasoning. |
| JEP-18/18b | **PASS** | AMD GPU TRAINING works: torch-directml on Python 3.11 trains a net on the RX 7700S (0.98 MNIST); GPU beats 16-thread CPU x2.1-6.0 on big matmuls, x2.56 large-MLP. Answer to 'CUDA-like but not NVIDIA': yes. |
| JEP-19/19b/19c | **PASS** (19b/c) | SCALING local learning: clean predictive coding matches backprop on MNIST AND Fashion-MNIST at 1- AND 2-hidden depth (matched comparison). JEP-19 NULL was an impl bug+optimizer mismatch, honestly corrected. |
| JEP-20/20b | **PASS** (20b) | 2D RELATIONAL inference: cognitive map recovers a latent 2D concept grid from local relations (corr 0.98, grid-cell codes) + infers global 2D relations on never-co-observed pairs (0.97/0.98). With JEP-17 (1D), relational reasoning in 1D+2D concept space. [JEP-20 PARTIAL = square-grid eigen-degeneracy, fixed by rectangular grid.] |
| JEP-21/21b | PARTIAL | FACTORIZATION: a low-dim structural prior generalizes SPARSE relational observations far beyond transitive closure (0.97 vs 0.77 @10% obs) - structure reduces what must be observed. (JEP-21 re-derivation test downgraded honestly; JEP-21b margin missed locked 0.2 bar by 0.002 at p=0.10 - claim supported, threshold technical-miss. Cross-content transfer still open.) |
| JEP-22/22b | **PASS** (22b) | STOCHASTIC robustness: closed-loop SR-value policy stays near-optimal under action slip (1.01x det -> 1.32x @20% -> 2.26x @50%), ~50x better than random. (JEP-22 reach=1.0 was budget-saturated - caught honestly; efficiency is the real metric.) |
| JEP-23/23b | **PASS** (23b) | BOUNDARY mapped: Euclidean cognitive maps embed metric structures well (ring 0.99, grid 0.92) but DISTORT hierarchies (tree 0.41, WORSE at higher dim 0.35 = geometry mismatch, not dim). Conceptual hierarchies (IS-A, taxonomies) need HYPERBOLIC geometry - honest signpost for what understanding needs. |
| JEP-24/24b | PARTIAL | HYPERBOLIC fix: proper Poincare embedding (transitive-closure + Riemannian SGD) recovers the tree hierarchy 0.41->0.83 (doubled) where Euclidean failed - confirms hierarchies need hyperbolic geometry. (Missed 0.85 bar by 0.019, not tuned; claim supported.) Signpost: understanding needs MIXED-curvature maps. |
| JEP-25/25b | NULL | MIXED-curvature: could NOT cleanly demonstrate Euclid x hyperbolic beating pure geometries in synthetic toys (L1-graph vs L2-manifold metric mismatch; Spearman forgiving of small-tree distortion). Established (Gu 2019) but not reproduced here - honest limitation, not overclaimed. |
| JEP-26 | PARTIAL | REAL taxonomy (77 concepts): geometries are COMPLEMENTARY - Euclidean better for relatedness/distance (0.93 vs 0.76), but ONLY hyperbolic captures IS-A GENERALITY (hypernym direction 0.88 vs Euclidean 0.39 below-chance). Hypernym inference needs hyperbolic. (Conjunctive bar mis-specified; core IS-A result decisive.) |
| JEP-27 | PARTIAL | MIXED-curvature REDEEMED task-based: mixed map is the best ALL-ROUNDER - worst-task 0.82 beats pure Euclidean (0.51, fails IS-A) and pure hyperbolic (0.72, weak relatedness). Synthesis supported; missed absolute 0.85 relatedness bar by 0.034 (2D capacity), not retuned. Conclusion: conceptual reasoning needs mixed-curvature maps. |
| JEP-28/28b | PASS (28b) | CONCEPT REASONER (tools/concept_reasoner.py): generalizes IS-A to held-out hypernym pairs (0.91 on 77-concept toy at >=5D); per-query reliable at >=5D (JEP-28's 2D demo failures fixed). |
| JEP-29/29b | PASS (29b) | SCALES to REAL WordNet (366-concept carnivore subtree): held-out IS-A 0.86 with adequate compute (20D/12k iters). JEP-29 NULL (0.68) was under-training, not a limit - honest scaling caveat: real scale needs more compute (GPU). |
| JEP-30/30b/30c | PARTIAL | COMPOSITIONAL LCA query ('what category includes both X and Y') from hyperbolic geometry: exact-LCA 0.63 (meets bar), common-ancestor 0.81 (just under 0.85); improves with embedding dim. Genuine but bounded step beyond pairwise IS-A. (JEP-30 NULL was a readout bug, fixed.) |
| JEP-31 | NULL | FULL mammal subtree (1170 concepts) GPU-trained: held-out IS-A 0.53 (~chance), trained 0.575 = UNDER-TRAINED (6k minibatched iters insufficient at 16x scale/depth-12). GPU itself worked (170s on AMD RX 7700S). Honest boundary: result needs compute scaled to hierarchy size; not pushed to convergence. |
| JEP-32/33 | PASS/NULL | is_a HARDENED: calibrated classifier (generality+containment) fixes cross-branch flaw (0.96 acc); JEP-33 lateral-feature did NOT fix sibling residual (reverted, honest - needs entailment cones). Caught+fixed a shipped bug AND a pushed-red test. |
| JEP-34 | **PASS** | INTEGRATION: abstract-goal agent - concept reasoner GROUNDS a conceptual goal ('reach a carnivore') via IS-A, world-model SR planner navigates to it (reaches correct-category entity 1.00 vs random 0.38). Conceptual knowledge + planning compose into understanding-informed behaviour. |
| JEP-35 | **PASS** | COMPOSITIONAL goals: set logic (AND/OR/NOT) + relatedness over IS-A ground the goal, world-model navigates - 1.00 across all 4 types (random 0.27). AND_NOT depends on the JEP-32 cross-branch fix. Symbolic operators + concept geometry + planning compose. |
| JEP-36 | **PASS** | SEQUENTIAL goals: 'visit a <A> THEN a <B>' grounded + navigated in order, 1.00 (random ~0.05). Temporal composition. Integration trio (34/35/36) complete - composes in the RELIABLE regime, inherits component limits at scale (honest). |
| JEP-37 | CHARACTERIZED | STRESS-TEST: integration on real WordNet degrades 1.00->0.79 (inherits component limits - caveat CONFIRMED). Unexpected: raw norm-direction is_a 0.126 = embedding generality-sign can INVERT run-to-run; calibrated is_a (JEP-32) compensates. Explains why calibration is needed + partly re-explains JEP-31. |
| JEP-38 | PARTIAL | radial-depth ANCHOR stabilizes raw generality-sign (0.80->0.86, no inversion) but doesn't reach 0.9 or improve calibrated is_a; corrects JEP-37 (0.126 was a RARE run). Kept as default for robustness. |
| JEP-39/39b | PASS/NULL | ENTAILMENT CONES (Ganea 2018, angular containment) FIX the sibling residual on toy (1.00, all siblings rejected where JEP-33 distance-features failed) but inherit the compute-scaling limit at 366 (TPR 0.42). Kept calibrated classifier as default; cones for small/clean taxonomies. Honest tradeoff. |
| JEP-40 | SELF-CORRECTION | compute-scaling CURVE on WordNet 366: held-out IS-A 0.65->0.78 with iters but PLATEAUS at ~0.78 (32k=16k). CORRECTS my repeated 'under-convergence is just compute' over-claim: it's compute up to a ~0.78 CEILING; the gap to toy 0.91 is NOT iterations (dims/method/inherent difficulty). |
| JEP-41 | CONCLUSIVE | dimension-scaling CURVE: held-out IS-A FLAT vs hyp_dim (10D:0.78, 80D:0.77). The ~0.78 ceiling is the METHOD, NOT compute or capacity (neither iters nor dims break it). Definitively corrects 'just compute'; closing it needs a DIFFERENT is-a method, not bigger budgets. |
| JEP-42 | **PASS** | ORDER EMBEDDINGS (Vendrov 2016, partial order) BREAK the ~0.78 ceiling -> 0.91 held-out IS-A on WordNet 366 (toy-level at real scale). Confirms the limit was the Poincare METHOD; the right partial-order method solves it. The self-correction (JEP-40/41) led to the actual fix. |
| JEP-43 | PARTIAL | order embeddings ALSO fix the sibling residual on the toy (1.00 siblings) but introduce a CROSS-BRANCH residual (rose is_a animal, TNR 0.97). No is-a method is universally best: order=large real, cones=small clean, Poincare=robust middle (kept default). Honest method-landscape map. |
| JEP-45 | **PASS** | Integrated order embeddings as isa_method='order' (siblings fixed, 0.91 at scale); poincare default unchanged. Tests 6/6, README method-guide. Ships JEP-42. |
| JEP-46 | NULL (key finding) | Better-AGGREGATE is-a (order 0.91) gave WORSE integration (0.50) than poincare (0.79): grounding needs CROSS-BRANCH precision, which is order's weakness; poincare's errors (siblings) don't arise in entity-vs-category grounding. ERROR PATTERN, not aggregate accuracy, predicts downstream utility. Best method is USE-CASE-dependent. |
| JEP-47 | NULL (deepens) | Predicted cones (highest random-pair precision TNR 0.98) -> best grounding; they gave WORST (0.24). Aggregate precision on RANDOM pairs doesn't predict precision on the TASK distribution (leaf-vs-general-category: wide cones -> cross-branch FPs). Lesson sharpened: measure on YOUR task's input distribution. Poincare confirmed grounding default. |
| JEP-48 | **PASS** | CROSS-DOMAIN replication: on vehicles (520, artifacts not animals) order embeddings (0.92) beat Poincare (0.86) on held-out IS-A, same as carnivores. The order>Poincare-at-scale finding is DOMAIN-GENERAL. Strengthens shipped method guidance. |
| JEP-49 | NULL (refutes) | DEPTH hypothesis REFUTED: on synthetic balanced trees Poincare IMPROVES with depth (0.80->0.925) and beats order at depth 7-9. So order's real-WordNet advantage is from IRREGULARITY (uneven branching/multi-parent), NOT depth. 3rd refuted mechanism-prediction in a row (46/47/49) - trust measurement over intuition. |
| JEP-50 | PARTIAL (concludes) | Irregularity NARROWS the gap (order catches up -0.05->-0.01) but does NOT flip it on synthetic single-parent trees. After 4 mechanism hypotheses, the real-WordNet order>>Poincare flip ELUDES synthetic reproduction (likely multi-parent DAG). CONCLUDED the why-investigation per own discipline; the measured WHAT stands. |
| JEP-51/52 | finding | Added multi-parent DAG support (correctness); DAG RULED OUT as the order>poincare mechanism (WordNet subtree is a tree). A test failure exposed an under-stated LIMITATION: held-out is_a generalization is weak on SMALL taxonomies (<50: ~0.4 recall) - but decent at scale (>=50: balanced 0.85, JEP-52). In-sample is_a perfect. Docs+README corrected. |
| JEP-7 | **PASS** | END-TO-END: contrastive-learned encoder + PC-learned predictor + energy-MPC reaches 0.97 of goals (untrained-predictor ablation 0.05, random 0.25). Nuance: exact prediction only 0.23 — planning needs correct ACTION RANKING, not exact prediction; world model accurate ENOUGH to plan. |

## The honest bottom line
- The SUBSTRATE'S genuine benefit is ARCHITECTURAL: its native primitives are the backprop-free versions of
  what JEPA/EBM/MPC need. Demonstrated, both halves: EBM inference == physical relaxation + local Hebbian
  (JEP-4); learning (representation AND predictor) == local rules that match/enable the digital versions
  (JEP-5 rep-learning -> EBM/MPC works; JEP-6d local predictor == backprop). Bridge = predictive coding /
  active inference.
- NOT shown / honest limits: toy scale; CPU (no speed or accuracy advantage over digital JEPA today - the
  benefit is realized only on physical/neuromorphic hardware); the substrate MEMORY thread closed NEGATIVE
  (G88-96), so "substrate as the long-term world-model STORE" is unsupported - the defensible claim is
  "substrate as the energy ENGINE + local learner". Human-level understanding remains an OPEN research program;
  nothing here closes it.
- Everything used (Hopfield, EBM, predictive coding, slow-feature/contrastive learning, MPC, active inference)
  is an ESTABLISHED method, named as such. No novelty claimed. The contribution is a coherent, pre-registered,
  honestly-bounded demonstration that the substrate has a principled (backprop-free, relaxation-based) job in
  the JEPA/EBM/MPC program - instead of bolting a neural net onto it.
- Open next work (JEP-7+): scale the local-learning rep + PC predictor; couple them (learn rep AND transition
  with local rules jointly); test on the REAL substrate dynamics, contingent on progress on the persistent-
  memory blocker (substrate memory thread).


## Substrate connection strengthened (JEP-11)
The planning piece is now substrate-native too: SR is learned by LOCAL TD, and TD-with-eligibility-traces is
exactly the substrate's BTSP primitive (CLAUDE.md). So the whole backprop-free loop maps onto the substrate's
own toolkit: BTSP/TD -> Successor Representation (geodesic value) -> value-based planning (DP/MPC) -> optimal
goal-reaching; plus Hebbian+relaxation EBM (JEP-4) and predictive coding (JEP-6d/10b, scales to MNIST). What is
NOT claimed: human-level understanding (open), GPU training on this AMD/Win machine (unavailable), or any
novelty (all established methods, named as such).

## (EARLIER) HONEST ASSESSMENT (JEP-1 .. JEP-25b) — superseded by the FINAL ASSESSMENT at end of file

### What was genuinely achieved
1. **A substrate-native realization of JEPA/EBM/MPC.** The full world-model agent - perception -> world model
   (BTSP/TD Successor Representation) -> value/MPC planning -> reward & transition adaptation - runs entirely on
   LOCAL learning + relaxation (no backprop), mapping onto the substrate's own primitives. Integrated end-to-end
   from noisy perception with no privileged state (JEP-16), robust to stochastic transitions (JEP-22b).
2. **Local learning scales.** Predictive coding (backprop-free) matches backprop on MNIST and Fashion-MNIST at
   depth (JEP-19b/c).
3. **The substrate's benefit is concrete and demonstrated**, not hand-waved: EBM inference = relaxation, learning
   = local plasticity, predictor = predictive coding (JEP-4/5/6d).
4. **GPU enabled** on AMD/Windows (torch-directml, Py3.11) - training + inference (JEP-18).
5. **Bridge to relational reasoning**: cognitive maps do 1D transitive and 2D relational inference (JEP-17/20b);
   low-dim structural priors generalize sparse relations (JEP-21b).
6. **Honest geometric boundary**: Euclidean cognitive maps fit metric structure, need HYPERBOLIC for hierarchies
   (JEP-23b/24b).

### What was NOT achieved (honest)
- **Human-level / conceptual understanding.** Everything is sensorimotor navigation + STRUCTURED relational
  inference on small graphs. No language, no open concepts, no genuine semantic grounding beyond toy structure.
- **Cross-content structural transfer** (TEM factorization): not cleanly demonstrated (JEP-21 downgraded).
- **Mixed-curvature synthesis**: established (Gu 2019) but I could not reproduce it in toys (JEP-25 NULL).
- **No novelty.** Every method is established and named (Hopfield, predictive coding, SR/grid-cells, TD, MPC,
  proto-value functions, Poincare embeddings, product manifolds). The contribution is pre-registered, honestly-
  bounded demonstration + a clean map of what works where - NOT new methods.

### Integrity record
~25 rungs, many NULLs treated as findings; multiple self-corrections (JEP-10 mistuned baseline retracted, JEP-17
SDE retracted, JEP-19 impl-bug diagnosed, JEP-21 self-downgraded, JEP-22 budget-saturation caught, JEP-25 honest
limitation). No post-hoc bar tuning; near-misses (JEP-21b 0.002, JEP-24b 0.019) reported as misses, not rounded up.

### The honest signpost forward
Toward conceptual understanding, the concrete next needs (each established, none trivial): MIXED-CURVATURE
cognitive maps (metric + taxonomic relations); grounding the structural machinery in real perceptual/linguistic
data at scale (now feasible on the GPU); and language as the interface to compositional concepts. These are
genuine research directions, not a finished path - stated honestly rather than overclaimed.

## ASSESSMENT UPDATE — JEP-26 .. JEP-38 (reasoning, integration, hardening)

After the JEP-25 assessment, the programme extended into real-data reasoning, integration, and deliverable
hardening. Honest additions:

### New genuine results
- **A working concept reasoner on REAL data** (JEP-26/28/29): mixed-curvature (Euclidean relatedness + hyperbolic
  IS-A) over WordNet; generalizes IS-A to held-out hypernym pairs (0.86 on 366 concepts with adequate compute);
  shipped + tested + documented (tools/concept_reasoner.py, +README, +pytest).
- **The two threads COMPOSE** (JEP-34/35/36): an agent acts on conceptual goals - single ("reach a carnivore"),
  logical ("mammal AND NOT carnivore"), and sequential ("a carnivore THEN a plant") - grounding via IS-A and
  navigating with the world model. Knowledge informs action.
- **The honest boundary is demonstrated, not just claimed** (JEP-37): on real WordNet the integration degrades
  1.00 -> 0.79, inheriting the component's is_a reliability.

### New honest limits / corrections
- **Scaling needs compute proportional to hierarchy size/depth** (JEP-29/31): 0.91 (77) -> 0.86 (366) -> 0.53-0.65
  (1170, under-converged). The GPU enables it; I did not push the full mammal tree to convergence.
- **is_a had a real correctness bug** (cross-branch false-positives) found by stress-testing my OWN deliverable,
  fixed with a calibrated classifier (JEP-32, 0.96); a residual remains on SIBLINGS (JEP-33 NULL - the distance-
  feature fix failed; needs entailment cones).
- **The hyperbolic generality SIGN is unpinned** and can rarely invert (JEP-37/38); a radial-depth anchor stabilizes
  it modestly (kept as default) but does not improve the calibrated accuracy.
- Caught and fixed a pushed-RED test (JEP-32 follow-up); reverted a fix that did not work (JEP-33); corrected my own
  over-strong framing of an anomaly (JEP-38 vs JEP-37).

### Net honest bottom line (unchanged in spirit, sharper in detail)
The EQMOD-4 programme builds and COMPOSES the structured building blocks of understanding - perception, world
models, planning, relational/conceptual reasoning, and goal-directed action over concepts - validated on real
data, shipped as usable tested tools, with every limit (scale, siblings, sign-stability, the toy regime) drawn
honestly. It is NOT human-level understanding and claims NO novelty (every method named as established: SR/grid-
cells, predictive coding, Poincare embeddings, product manifolds, set logic, MPC). The frontier (entailment-
geometry for fine relations, convergent-scale grounding, language) is open and named as such. ~38 rungs, NULLs as
findings, ~13 self-corrections including catching a shipped bug, a red test, and an over-claimed anomaly.

---

## FINAL HONEST ASSESSMENT (whole programme, JEP-1 .. JEP-118c)

### What was actually built
1. **The substrate's primitives ARE backprop-free JEPA/EBM/MPC** (JEP-1..18): energy-based inference = relaxation,
   learning = local plasticity (predictive coding matches backprop on MNIST/Fashion at depth); the full perception
   -> world-model(SR/BTSP) -> MPC-planning loop runs backprop-free. The four-pillar capstone (JEP-78) shows
   regularized JEPA (VICReg) + latent MPC with a collapse negative control; JEP-79/79b locate WHEN latent-
   prediction beats generative (only under a capacity bottleneck, not automatically).
2. **The substrate is IN the chain** (JEP-81/82): after an honest audit (0 of 108 prior runs imported it), the
   EBM + predictor + MPC pillars were run on world.energy.EnergyNet itself.
3. **The Understanding Engine** (world/understanding.py, JEP-92..115, 26 gated tests): a 100%-working,
   substrate-legal (NO transformer) conversational system spanning all three of Michael's verbs — LEARN (told,
   correction, examples, induction, observation, self-taught), REASON (multi-hop DAG, Boolean, three-valued,
   contradiction, quantification, comparison), COMMUNICATE (Q&A with reasoning, WH, why, dialogue-teaching,
   generation/describe).
4. **A mostly-unsupervised grounding pipeline** (JEP-113..118c): perceive -> cluster (structure) -> cross-
   situational word learning (meaning, no clean labels) -> wire taxonomy -> reason/describe, self-taught with
   ZERO told facts in the favorable regime ('A dog is a mammal', learned not told).

### The honest frontier (named, not crossed)
- **Real-prose parsing**: classic/grammar extraction recovers ~2% of Boole's actual sentences (JEP-89/108b); a
  permissive grammar's high parse rate is SPURIOUS (clauses-as-concepts). The no-transformer rule forbids the
  learned extractors modern NLP uses for exactly this. This is the hard gate.
- **Superordinate/abstract word learning**: cross-situational PMI underdetermines hierarchy LEVELS (JEP-118);
  basic-level is robust, superordinate needs LCA-of-extension + adequate exposure (JEP-118c).
- **Arbitrary unsupervised structure** (relations beyond IS-A, non-hierarchical features): JEP-69/70 NULL.
- **Open-ended generation, polysemy/synonymy, rich embodied grounding, language at scale**: open.

### Honest answers to Michael's recurring questions
- **"Something innovative?"** NO. Every method is established and named (SR/grid-cells, predictive coding,
  Poincare/order embeddings, VSA/HRR, TransE, VICReg, SCAN/Lake-Baroni, agglomerative clustering, cross-situational
  learning, Hopfield, MPC). The transferable output is the working FOUNDATION + the DISCIPLINE.
- **"Human-level understanding and communication?"** NO, and not pretended. A genuine, working, SMALL version of
  human-like learning/understanding/communication on simple-to-natural language — the foundation to scale FROM,
  with the hard, genuinely-open-under-no-transformer frontier honestly drawn. Boole is the final exam, not the primer.

### The discipline (the real deliverable)
~120 rungs, every acceptance bar pre-registered and never post-hoc tuned; predict-calibrate (19/32 hits, EVERY miss
diagnosed into a durable lesson); ~25+ honest self-corrections including catching a SHIPPED bug, a RED test, an
over-claimed anomaly, a committed-failing-test process error, a FRAGILE success (JEP-117 super-naming) corrected,
and a FAILED fix (JEP-118b) owned. NULLs recorded as findings. Reusable wisdom surfaced as docs/patterns/. The
deadlock-breaking PROCESS — measure before claiming, predict then diagnose, fail cleanly, name the established as
established — is the genuine, transferable result.

---

## KEY CONCEPTUAL FINDINGS (post-JEP-118c: the structure-learning + inference-robustness work, JEP-128..140)

These later rungs produced the programme's most transferable INTELLECTUAL contributions (all from established
methods, no novelty claimed — the value is the honest characterization):

1. **The JEP-69/70 "can't learn arbitrary structure" NULL was too pessimistic — for CLEAN data.** Relation
   properties (transitivity) and composition rules ('uncle = parent o sibling') are LEARNABLE from clean
   observation, UNIQUELY IDENTIFIABLE (exact-match dominates spurious candidates), and ROBUST to distractor
   relations + moderate noise (JEP-128/129/130/131). The limit on clean data is SEARCH COST (|R|^depth), not
   identifiability. Sparse-PASSIVE data is ambiguous, but ACTIVE querying solves it in ~n log n (JEP-135).

2. **THE COMPOUNDING INSIGHT (the deepest finding).** Both LEARNING structure and REASONING over it are MULTI-STEP
   inference, and multi-step inference COMPOUNDS errors: a k-step derivation is correct only if ALL k steps are, so
   reliability decays ~(1-p)^k EXPONENTIALLY with inferential DEPTH under noise. Measured for noisy structure
   learning (JEP-133/134/136, needs redundancy growing with structure SIZE) and for the engine's multi-hop
   reasoning (JEP-137, depth1 0.90 -> depth4 0.52 @10% noise). This is WHY long brittle chains fail.

3. **CHAINING vs AGGREGATION (the unifying picture).** CHAINING (deduction, closures, sorts) COMPOUNDS errors ->
   fragile. AGGREGATION (induction = majority over instances; redundant DAG paths = vote over derivations) AVERAGES
   errors -> robust to ~50% noise (JEP-140: induction 0.91 vs deduction 0.20 @30% noise). The CURE for chaining
   fragility is REDUNDANT independent paths + voting (JEP-138, a recall tool — NOT a precision tool, JEP-139 NULL).
   LESSON: human-like robust inference under noise = AGGREGATION + REDUNDANCY, not deep clean chains; match the
   inference SHAPE to the noise.

4. **My own predict-calibrate bias, measured.** I was systematically miscalibrated on structure learning in BOTH
   directions: OVER-predicted difficulty on CLEAN data (exact-match is strong, 3x), UNDER-predicted it on NOISY data
   (closures compound, 2x). The discipline surfaced a real bias in my intuition — measure, don't trust it.

5. **The exhaustive structure-learning map + the FULL RECIPE (JEP-141..154, capstone).** The frontier is now mapped
   end-to-end: clean=easy (search-cost), noisy=hard (closures compound; redundancy at cost), sparse-passive=
   ambiguous, sparse=ACTIVE-querying solves (n log n), one-shot=PRIORS help with a bias cost (JEP-151, no free
   lunch), meta-prior=learnable from consistent domains but doesn't solve deep one-shot (JEP-152). The complete
   recipe for efficient learning under the realistic deep+noisy+minimal regime: compositional REUSE fixes the search
   constraint (~5x sample-complexity cut, JEP-153) + few-shot REDUNDANCY beats noise (->0.99) + NOISE-TOLERANT SOFT
   aggregation as the critical enabler (strict consistency is actively HARMED by noisy data, JEP-154b). THE
   UNIFICATION: the chaining-vs-aggregation lesson governs LEARNING as well as REASONING — hard consistency fragile,
   soft aggregation robust, universally. Honest calibration miss recorded (JEP-154: I forgot my own JEP-134 lesson).

6. **LEARN-FROM-SOURCES, end to end + the representation-dependent compounding refinement (JEP-155..163).** A
   complete, positive, no-transformer pipeline that LEARNS from prose and reasons over it: (a) the real-prose parse
   gate is the GENRE, not the extractor (JEP-155/156 — same Hearst + bare-NP extractor gets ~0.87 precision on
   encyclopedic prose vs ~0 on Boole's logic prose); (b) end-to-end learn-from-prose -> CROSS-SENTENCE multi-hop
   understanding works (JEP-157, 1.00 vs bag-of-words 0.00; 'a poodle is an organism' from a passage that never says
   it); (c) extended to MULTI-RELATION (is-a + part-of + causal, JEP-159) and consolidated into first-class tested
   engine methods e.read()/e.describe() — closing the LEARN->UNDERSTAND->COMMUNICATE loop (JEP-160, multi-relation
   English profiles); (d) read() hardened to 8/8 common prose-variation categories (JEP-161 boundary -> 162 shallow
   parse for conjoined/plural/multi-fact/appositive with a POS-free adjective guard -> 163 recency coreference), with
   honest bounds (genre, extraction-noise COMPOUNDING per JEP-157b — the universal insight's THIRD manifestation,
   multi-entity coreference). And (e) the universal compounding insight REFINED to be representation-dependent
   (JEP-158, a MISS that paid off): symbolic-independent edges compound EXPONENTIALLY, continuous-independent errors
   AVERAGE (sqrt-k, robust — a concrete reason the learned path helps), continuous-systematic bias compounds
   LINEARLY; substrate Hopfield cleanup (JEP-4) cures both continuous cases — tying the four pillars + the universal
   insight + the substrate. Two singularization bugs found+fixed; one CARDINAL repeated bug honestly logged (D-dim
   noise = sigma*sqrt(D)).

These are the genuine outputs: a frontier REFRAMED end-to-end with honest bounds, a unifying INSIGHT about inference
under noise (chaining vs aggregation, universal across learning AND reasoning), the full recipe for efficient
structure learning, and a measured account of prediction bias. Established methods throughout; NOT human-level; the
discipline (predict-calibrate 56/79, every miss diagnosed including JEP-154/157/158/159, ~40 self-corrections) is the
transferable deliverable.
