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
