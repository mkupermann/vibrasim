# JEP-19 — does local predictive coding match backprop with DEPTH + on a harder dataset? (AMD GPU)

## Motivation
JEP-10b: 1-hidden predictive coding matched backprop on MNIST (CPU). Open question: does substrate-compatible
LOCAL learning still match backprop with DEPTH (PC's approximation to backprop is known to degrade with depth)
and on a HARDER dataset? Now testable at scale on the AMD GPU (JEP-18). Fashion-MNIST, deep MLP, torch-directml.

## Pre-registration (locked BEFORE run)
- Fashion-MNIST (60k/10k, 784, 10 classes; harder than MNIST). Nets: 1-hidden (784-1024-10) and 2-hidden
  (784-1024-1024-10), tanh. Trained on the AMD RX 7700S via torch-directml.
- Learners: BACKPROP (Adam) and PREDICTIVE CODING (hierarchical local error nodes + inference relaxation,
  no backprop), same arch.
- Bars: backprop 1-hidden >= 0.86 and 2-hidden >= 0.86 (Fashion-MNIST MLP range, confirms task). PC matches
  backprop within 0.04 at EACH depth. PASS = local learning scales with depth + harder data. PARTIAL/NULL if PC
  degrades with depth (an honest, known limitation if so). Predictive coding (Whittington-Bogacz 2017) established.

## Result — NULL (confounded: optimizer mismatch + likely PC implementation bug at depth)
| net | backprop (Adam) | predictive coding |
|-----|-----------------|-------------------|
| 1-hidden | 0.8837 | 0.8066 |
| 2-hidden | 0.8851 | 0.1000 (chance) |

**VERDICT: NULL — do NOT over-interpret.** Two confounds prevent any clean conclusion: (1) the comparison is
UNFAIR - backprop used Adam (adaptive, momentum) while PC used plain local updates; on MNIST with MATCHED plain
SGD, PC matched backprop (JEP-10b). (2) The 2-hidden PC collapsed to CHANCE (0.10) = it did not learn at all,
almost certainly an IMPLEMENTATION bug in my hand-rolled hierarchical PC (messy indexing / eval mismatch), NOT a
fundamental depth limitation of predictive coding (the literature shows multi-layer PC trains fine). I will not
claim "PC degrades with depth" from a buggy implementation. Honest fix (JEP-19b): a CLEAN, validated multi-layer
PC + MATCHED optimizers (both plain SGD), sanity-checked on easy MNIST (must reach ~0.97 at 2-hidden) BEFORE
testing Fashion-MNIST. Bars locked, not tuned. GPU itself works fine (JEP-18); this is a science/implementation
issue, device-independent.
