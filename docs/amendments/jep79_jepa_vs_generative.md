# JEP-79 — the core JEPA thesis: latent prediction beats generative under UNPREDICTABILITY

## Motivation (four pillars: WHY joint-embedding / regularized over generative)
LeCun's central argument for JEPA: predict in REPRESENTATION space, not observation space, so the model can
IGNORE inherently unpredictable detail instead of wasting capacity modeling it. Test directly with a generative
(observation-predicting) negative control.

## Setup
- Observation o in R^64 = [PREDICTABLE 32-d: tanh(P s), s = controllable 2D state, s'=clip(s+a)] ++
  [DISTRACTOR 32-d: tanh(Q d), d = an UNCONTROLLABLE random-walk uncorrelated with action a].
- JEPA: enc:R^64->z(8); predictor pred(z,a)->z'; loss = latent-prediction + VICReg. Encoding the distractor RAISES
  prediction loss (it's unpredictable from a) -> pressure to SUPPRESS it.
- GENERATIVE control: enc + decoder dec(z,a)->o' (predict next OBS, MSE over all 64 dims). Reconstruction PRESSURES
  the encoder to ENCODE the distractor (to lower its reconstruction loss) -> capacity split.
- Sweep distractor strength sigma_d in {0, 0.5, 1.0, 2.0}. Metric: state-probe R^2 (linear-decode controllable s
  from z); secondary: MPC-to-goal on s.

## Pre-registration (locked BEFORE run)
- PASS: at HIGH distractor (sigma_d=2.0), JEPA state-R^2 >= 0.80 AND (JEPA - GENERATIVE) state-R^2 gap >= 0.20 —
  i.e. JEPA suppresses unpredictable features and stays state-faithful where the generative model degrades.
  Demonstrates the JEPA latent-prediction advantage under unpredictability (LeCun's core rationale).
- NULL is a valid outcome: if the generative model stays robust (small gap), report it honestly — the advantage
  would then be smaller than the standard story claims. Established (JEPA rationale, VICReg), named; no novelty.

## Result — NULL (honest; the advantage did NOT appear at this scale)
| sigma_d | JEPA state-R^2 | GENERATIVE state-R^2 | gap |
|---------|----------------|----------------------|-----|
| 0.0 | 0.484 | 0.990 | -0.506 |
| 0.5 | 0.991 | 0.989 | +0.002 |
| 1.0 | 0.992 | 0.987 | +0.005 |
| 2.0 | 0.991 | 0.988 | +0.003 |

**VERDICT: NULL.** The generative model stayed state-faithful (R^2 ~0.99) at EVERY distractor level; JEPA showed
NO advantage (gap ~0) and was WORSE at sigma_d=0 (0.48) — there the distractor is constant hence PREDICTABLE, so
JEPA correctly encodes it (capacity split). As the distractor becomes unpredictable (sigma_d>0) JEPA SUPPRESSES it
(R^2 -> 0.99) — the mechanism works — but it only catches UP to the generative model, never beats it. The standard
"JEPA >> generative under unpredictability" story is NOT demonstrated at this toy scale: with ample capacity an
8-d latent + wide decoder encodes BOTH controllable state and the 32-d distractor with no measurable cost. Honest,
hype-deflating finding. HYPOTHESIS for where the advantage should appear: a CAPACITY BOTTLENECK where modeling the
unpredictable content genuinely competes with modeling state (tested next, JEP-79b). Established rationale, named.
