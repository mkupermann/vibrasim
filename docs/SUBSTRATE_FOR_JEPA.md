# Using the substrate as a technology for JEPA / EBM / MPC — what is the genuine benefit?

Michael's question (2026-06): "How can we use the substrate as a technology for [JEPA/EBM/MPC] that IS a
benefit?" This is the honest, concrete answer.

## The one-paragraph answer
JEPA, EBMs, and MPC are normally TRAINED by backpropagation and do INFERENCE by gradient descent on a digital
computer. The vibrasim substrate's native primitives are precisely the *backprop-free* alternatives to both
halves of that. So the substrate's benefit is not "a faster/better JEPA today" (it is not) — it is an
ARCHITECTURAL one: the substrate is an analog **energy-minimization machine with local learning**, which is
exactly what an EBM becomes when you stop simulating it digitally. Inference becomes *physical relaxation*;
learning becomes *local plasticity*. One framework — **predictive coding / active inference** — unifies all
three and maps directly onto the substrate.

## The mapping (the bridge is predictive coding / active inference)
| JEPA/EBM/MPC needs | Digital default | Substrate-native primitive |
|---|---|---|
| EBM inference `argmin_y E(x,y)` | gradient descent on learned energy | **physical relaxation** — settle to a low-energy state (Hopfield = an EBM; recall = settling). Demonstrated: JEP-4. |
| Learn the energy/predictor | backprop (global gradient) | **local plasticity** — STDP / BTSP eligibility traces (Hebbian). Demonstrated: JEP-4 Hebbian store. |
| JEPA "predict in representation space" + minimize error | encoder+predictor MLP, latent MSE | **predictive coding** (Rao-Ballard / Friston free energy): hierarchical latent prediction, local error-minimization |
| MPC planning (act toward low energy) | rollout + optimizer | **active inference** — act to minimize expected free energy |

Predictive coding is the key: it IS "predict in latent space and minimize a prediction-error energy, with local
updates and relaxation dynamics." That is JEPA (predict-in-latent) + EBM (free-energy) + local-learning
(substrate) in one formalism, and active inference extends it to MPC.

## What is demonstrated vs claimed (honesty)
- DEMONSTRATED (JEP-4, PASS): substrate-native energy-based inference — local Hebbian learning (no backprop) +
  relaxation inference (no optimizer) recalls stored patterns (0.905 at load 0.1N), energy monotonically
  descends, capacity follows Hopfield's ~0.14N law. This is the EBM half of the benefit, concretely.
- NOT demonstrated / honest limits:
  - No speed or accuracy advantage over a digital JEPA was shown — and on a CPU there is none. The benefit is
    in-principle (analog relaxation, local learning), realized only on physical/neuromorphic hardware.
  - The substrate MEMORY thread closed NEGATIVE (G88-G96): holding persistent, selective learned content is the
    substrate's known weak point. So "substrate as the learned world-model STORE" is NOT yet supported; the
    defensible benefit is "substrate as the energy-minimization ENGINE + local learner."
  - JEPA's full power needs a LEARNED encoder where distance/energy is meaningful (JEP-2 NULL showed a random
    encoder breaks energy-based planning). Learning that encoder with purely local rules at scale is open
    research (predictive-coding-approximates-backprop results exist but are not free lunches).

## Why this is the RIGHT framing (not hype)
Hopfield networks, EBMs, predictive coding, and active inference are all ESTABLISHED methods (Hopfield 1982,
LeCun/Hinton EBMs, Rao-Ballard 1999, Friston free energy). Nothing here is claimed as new. The honest value:
they give the substrate a PRINCIPLED job in the JEPA/EBM/MPC program — be the relaxation-based, locally-learned
energy engine — instead of bolting a backprop net onto it (which CLAUDE.md forbids and which would waste the
substrate). The next rung (JEP-5) would test predictive coding with local learning as the JEPA predictor, the
direct substrate-compatible path to "predict in representation space" without backprop.

## Update — JEP-5 closes the representation-learning half (PASS)
JEP-2 showed energy-based MPC fails with a random encoder (0.07). JEP-5 then showed a representation learned by
a LOCAL contrastive temporal-coherence rule (no backprop, substrate-native) makes energy meaningful (Spearman
0.88) and lifts energy-based MPC to 0.90 (vs 0.08 random). So BOTH substrate-native halves are now demonstrated:
- EBM inference by relaxation + local Hebbian storage (JEP-4 PASS).
- Representation learning by a local contrastive rule that makes energy/MPC work (JEP-5 PASS).
Together: a backprop-free, local-learning, relaxation-based realization of the JEPA+EBM+MPC loop at toy scale.
Honest limits unchanged: toy scale, CPU (no speed win), and the substrate's persistent-memory weakness
(G88-96) still blocks "substrate as the long-term world-model store." The PARADIGM maps; scaling it with purely
local learning on the real substrate is the open work (JEP-6+).
