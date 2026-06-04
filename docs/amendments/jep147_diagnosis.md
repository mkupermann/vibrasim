# JEP-147 — integrated diagnostic reasoning (abduction + deduction): the full abductive cycle

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 100%: from observed symptoms (effects), abduce candidate causes, deduce each cause's expected effects, and
  rank by coverage of observations (best explanation = explains most symptoms with least over-prediction). MOST-
  LIKELY MISS: the coverage-vs-overprediction scoring with partially-overlapping causes.

## Acceptance
- PASS: diagnosis battery = 100% (picks the best-explaining cause). Established (abductive diagnosis / parsimonious
  covering, Peirce; Reggia), named; no novelty.

## Result — PASS (HIT)
Diagnosis battery 4/4: {fever,ache,cough} -> flu (exact cover); {cough,sneeze} -> cold; {fever,ache,cough,anosmia}
-> covid (anosmia is the distinguishing symptom); {cough} alone -> a plausible candidate (ambiguous, as it should
be). Prediction HIT; tally 42/61. The engine COMPOSES its inference modes into diagnosis: ABDUCE candidate causes
from symptoms, DEDUCE each cause's expected effects, score by COVERAGE of observations minus over-prediction
(parsimonious covering). This is Peirce's full abductive cycle and demonstrates the faculties COMBINE into
sophisticated reasoning, not just coexist. Established (abductive diagnosis / parsimonious set-covering, Peirce;
Reggia/Peng), named; no novelty. HONEST: qualitative coverage scoring (no disease priors or symptom likelihoods —
a probabilistic diagnostic tier would add those via the noisy-OR layer JEP-142).
