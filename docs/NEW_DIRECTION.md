# New Direction — Engineered Modular Scaffold, Emergent Dynamics

Written 2026-05-31, after the spontaneous-substrate memory programme (BET-089→109)
reached its honest ceiling (3/4 bars; persistent selective RECALL never closed).

## The one lesson, stated plainly

Every failure in 20 amendments traced to the SAME root: the substrate is a
**homogeneous, spontaneously self-assembled, tiny, fully-connected blob**.
- Activity **percolates** (no compartments) → memory spreads, can't stay local.
- Structure **churns** (~13 s atom turnover before we froze it; bridges still
  form/break) → the readout is diluted by new weak elements.
- It is **too small and too connected** (~10–70 atoms) → noisy, metastable.

We solved the pieces — persistent atoms (BET-091), selective write (096/099),
containment via an engineered wall (106) — but composing them into stable
selective recall fails because the medium itself fights it. More knob-tuning will
not change this; we proved it from five angles.

## The pivot

**Stop waiting for cognition to self-assemble from physics. Engineer the
modular architecture; let only the dynamics/weights emerge.**

This is not a violation of the charter — it is the charter's own principle
(CONCEPT §4.8: *ports are engineered; internals emerge*) applied one level up.
We keep the substrate's *verified* learning primitives and run them on a *stable,
engineered scaffold* instead of a churning blob.

### Concretely

1. **Fixed neuron modules.** Pre-place K persistent "neuron" sites (atoms frozen
   in position, immune to turnover) — a real, stable scaffold, not a soup.
2. **Engineered sparse, directed connectivity.** A real connectivity matrix:
   sparse, modular (clusters with few inter-cluster links). This bounds
   percolation by construction — the thing the homogeneous blob could never do.
3. **Emergent weights only.** The mechanisms we validated *in isolation* —
   integrate-and-fire atoms, Hebbian co-firing on bridges, the bistable
   latch/hold, charge-blank — operate ON this scaffold. Only the synaptic
   weights change; the topology is fixed.
4. **Per-module readout.** No region-mean over a churning core; read the state of
   named modules. Turnover-immune by construction.

### Why this should work where the blob failed

| Blob blocker | Scaffold fix |
|---|---|
| percolation | engineered sparse/modular connectivity bounds spread |
| turnover dilution | frozen scaffold; per-module readout |
| metastable cascade | directed, sparse links → controlled, not runaway |
| tiny noisy n | choose K; modules are named, not statistical |

If selective persistent memory still fails on a *stable, modular, engineered*
scaffold with the *validated* learning rules, THAT is a deep result. But it is
the honest next experiment — and the first one in the whole programme where the
medium is not actively sabotaging the mechanism.

## First step (BET-110, a NEW track)

Pre-register a minimal scaffold: ~8–16 frozen neuron modules in 2 compartments,
a hand-built sparse directed bridge matrix (dense within compartment, 1–2 links
across), the validated Hebbian+bistable write, per-module readout. Re-test the
four bars (selective firing, selective write, persistent recall, containment).
Build it with the `bet-experiment` skill; watch with `watch-results`.

## Decided learning paradigm (2026-05-31): energy-based, predictive, self-supervised — no transformer

Constraint from Michael: NO transformer. If anything, **geometric math AI** that
is **self-supervised-learning capable**. That fits the substrate's nature (it is
already a geometric dynamical system) and it fits the scaffold above. The decision:

**A modular, energy-based / predictive-coding geometric substrate that learns
self-supervised by minimizing the prediction error of its own dynamics, using
LOCAL plasticity — no backprop, no attention, no transformer.**

Three pillars, each non-negotiable:

1. **Geometric / energy-based.** The substrate state (module activations, bridge
   weights) defines an **energy landscape**. Memory = **attractor basins** —
   "sliding into an energy valley" (the README's own Phase-6 framing, now made
   central, not incidental). Recall = relaxation dynamics to the nearest
   attractor; pattern completion falls out for free. This is geometry of the
   state manifold, not a sequence model.

2. **Self-supervised objective.** No labels, ever. The system learns by
   **predicting / reconstructing its own input** — mask part of a pattern and
   force the dynamics to complete it; or predict the next state of the geometric
   field. The training signal is the substrate's *own* prediction error (EQMOD
   already has prediction-error machinery in G16/G17 and offline replay in
   G15/G18 — reused, not bolted on).

3. **Local, biologically-plausible learning — explicitly NON-transformer.** The
   weight updates come from local rules in the spirit of **predictive coding**
   (Rao–Ballard / Millidge–Bogacz) and **equilibrium propagation** (Scellier–
   Bengio): the network settles to an equilibrium, a small nudge toward lower
   prediction error is applied, and the difference of the two equilibria gives a
   purely local weight update. This is the established alternative to backprop and
   transformers, and it maps cleanly onto the substrate's existing Hebbian /
   bistable bridge plasticity.

Why this is the right synthesis: the modular scaffold gives **stable structure**
(fixes percolation + turnover, the two things that killed the spontaneous run);
the energy/attractor formulation gives **geometric, content-addressable memory**
(the thing the latch could only approximate); and the predictive self-supervised
objective gives a **label-free learning signal** grounded in the project's own
prediction-error and replay primitives. Nothing here is a transformer, and nothing
requires a pretrained model.

### First falsifiable experiment (BET-110, new track)

A minimal energy module: a small modular scaffold of frozen sites whose bridge
weights define an energy. Train SELF-SUPERVISED on a handful of unlabeled spatial
patterns by masked-completion (present a pattern with part masked; relax; apply a
local predictive-coding / equilibrium-prop weight update toward the un-masked
pattern). Then test **pattern completion**: present a partial cue, relax, measure
overlap with the stored pattern vs a control with no training. Bars: completion
accuracy clearly above the untrained control; distinct patterns settle to distinct
attractors (content-addressable); zero labels used. Build with `bet-experiment`,
watch with `watch-results`.

If a tiny energy-based module learns to complete patterns self-supervised on a
stable geometric scaffold, that is the first thing in the whole project that is
genuinely *learning* — and it is reusable far beyond the substrate.

## The meta-option (worth naming)

The most reusable thing this project produced is **the autonomous, pre-registered
research pipeline itself** (the loop, parallel sweeps, the live watcher, the
discipline, the honest NULL-mapping). If the substrate-as-mind goal is not the
real objective, the pipeline is a product on its own — point it at a problem with
a clearer payoff and the substrate becomes just its first proving ground. This is
a decision for Michael, recorded here so it is not lost.
