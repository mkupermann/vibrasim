# Material-learning experiments: evidence and limitations

**Evidence date: 12 September 2026.** This report separates measured effects,
failed criteria and implementation corrections. It is a research snapshot, not a
claim that the overall learning objective has been achieved.

## Evidence at a glance

| Experiment | Substrate | Finding | Unmet requirement |
|---|---|---|---|
| G183 | World, engineered spectral input ports | Retained response changes after audio exposure | Reciprocal sound selectivity |
| MM3 | Engineered audiovisual spring-association instrument | Test accuracy remains 1/3 across controls and exposure checkpoints | Useful transfer to new recordings |
| G189 | Guided continuous mechanical reference | Paired exposure changes subsequent transfer relative to separated exposure | Complete retained-read criterion |
| G191 | Guided continuous mechanical reference | Further exposure reverses source preference in both directions | Return-to-rest criterion; unbranched read/relearn lifecycle not tested |

## G183: real-audio selectivity

Eight fixed spectral ports transduce ESC-50 audio into an engineered material
fixture. Training and query recordings are disjoint within the experiment; the
corpus itself was already known during development. Two allocation orderings give
the same reported contrasts. They are implementation controls, not independent
replications of the scientific hypothesis.

One execution used 136,880 World ticks. Physical and assay checks passed. The
required selectivity threshold was 0.10 for **each** contrast:

| Contrast | Observed | Required minimum |
|---|---:|---:|
| Bell | 0.1316616014 | 0.10 |
| Dog | 0.0000000000 | 0.10 |
| Rain | −0.0104067751 | 0.10 |

The bell-trained mean bell response, 0.6050, met a separate response-reduction
criterion of at most 0.80. That does not compensate for the two failed contrasts.
The result is **NULL for reciprocal real-audio selectivity**. Bell and dog histories
converged to the same limiting binary material mask; this is explanatory evidence,
not proof that all information in their full material states was identical.

[Original result](../../../archive/run-logs/g183/first/result.json) ·
[Saved measurements and snapshots](../../../archive/run-logs/g183/first/)

## MM3: audiovisual scene transfer

The engineered audiovisual model uses fixed audio bands and visual features,
with externally imposed exposure and a fixed evaluation procedure. At 6, 12 and
24 seconds of total exposure, all five evaluated conditions scored 1/3 on the
three test recordings. This is a **NULL** result.

The small media pool includes scene and synchronization confounds, so it cannot
isolate the learning rule as the sole cause of failure. All nine recordings are
now development-exposed. They must not be described as fresh data in a later
validation. The positive synthetic demonstration in the same line of work did
not establish real-video transfer.

[Original result](../../../archive/run-logs/mm3/20260912-first/result.json)

## Guided reference models

G189 and G191 use a declared, constrained spring model with local stiffness aging:

\[
E = \frac12\sum_e k_e\,\Delta\ell_e^2,\qquad
\dot{k}_e = -\gamma k_e\,\Delta\ell_e^2.
\]

This is a published directed-aging mechanism, not a new VibraSim learning rule.
An ideal guide supplies transverse stability. Mechanical node dynamics are
integrated using SciPy's DOP853 solver. During teaching, boundary trajectories are
imposed; during readout, displacement of a physical receiver is measured. These
models are distinct from the production World stepping scheme.

**G189.** Seven exposure conditions used 301 integration segments. Paired exposure
produced gains of approximately 0.696–0.699; temporally separated exposure produced
approximately 0.309–0.311. The smallest paired-minus-separated contrast was 0.3868.
Stiffness drift, response drift, finite rigidity and energy checks passed, but the
combined return-to-rest condition failed in **all seven** conditions. The verdict
is mixed, not complete retained-read success.

[Original result](../../../archive/run-logs/g189/first/result.json) ·
[Saved trajectories](../../../archive/run-logs/g189/first/)

**G191.** Two initial source preferences were tested, each with acquisition,
opposite teaching, continued original teaching, separated teaching and frozen
adaptation conditions. All five read pairs in each condition are retained in the
published result. Let D be the gain of the originally preferred source minus the
other source's gain:

| Condition | Initially A: D range | Initially B: D range |
|---|---:|---:|
| Acquisition | 0.130593 to 0.130995 | 0.130876 to 0.131081 |
| Opposite teaching | −0.135999 to −0.135357 | −0.135467 to −0.134767 |
| Continue original | 0.383624 to 0.384066 | 0.382902 to 0.384118 |
| Separated teaching | 0.115274 to 0.115769 | 0.115716 to 0.116240 |
| Frozen adaptation | 0.130583 to 0.130758 | 0.130758 to 0.131019 |

Finite reassignment occurred in both directions, while controls retained positive
preference. Across 840 segments, the minimum stiffness was 2.4004 and the largest
read-period relative stiffness drift was 0.003813. The original return condition
required both position and speed to remain within 10⁻⁵ in their respective model
units during the final two seconds of each blank interval. It failed at **all ten
endpoints**. The largest observed blank magnitude was 7.473 × 10⁻⁵.

The acquisition measurement used a sibling copy of the acquired state. The branch
subsequently retrained had not undergone that measurement. This is not evidence
for a single uninterrupted acquisition → read → relearn lifecycle. Frozen-coefficient
forecasts were initialized from each measured read-start state, so their accuracy
is conditional and is not an independent demonstration of learning.

[Original result](../../../archive/run-logs/g191/first/result.json) ·
[Saved trajectories and checkpoints](../../../archive/run-logs/g191/first/)

## Corrections and numerical limitations

- **G185: invalid first analysis.** A snapshot time-field decoding error stopped
  the original analysis. The repaired analysis was recorded separately. The failed
  attempt is retained rather than counted as a scientific negative result.
- **G186: withdrawn first design.** The proposed boundary ablation was equivalent
  to the existing boundary condition. It was withdrawn before execution. In the
  corrected experiment, freezing adaptation reduced drift by roughly 21–25%,
  below the predicted reduction of at least 50%.
- **G187: traversal sensitivity.** Reversing bond traversal while preserving
  physical assignments changed measured drift by about −0.0164 and +0.0201 in the
  two stages. Numerical update order was therefore consequential in that assay.
- **G188: separate continuous reference.** A consistent continuous model sharply
  reduced order sensitivity, but residual drift remained. Its damping law is an
  explicit model change, not a behavior-preserving fix to World.
- **G190: residual-motion diagnosis.** A saved-data analytic calculation matched
  the frozen control's ringdown to within 4.60 × 10⁻¹⁷. Explaining the residual
  motion does not make the failed return condition pass.

The G185 records are included under [first attempt](../../../archive/run-logs/g185/first/)
and [repaired analysis](../../../archive/run-logs/g185/repaired/). The other
corrections above summarize the development record; this release does not include
all of their intermediate trajectories.

## Prior work

Material memory and physically local adaptation are established research topics.
Relevant precedents include:

- Hexner et al., [Effect of aging on the non-linear elasticity and memory formation in materials](https://arxiv.org/abs/1909.00481), 2020: loading history encoded through changes in strength or geometry.
- Hexner et al., [Periodic training of creeping solids](https://arxiv.org/abs/1909.03528), 2020: mechanical behavior trained through periodic deformation.
- Stern et al., [Supervised learning in physical networks](https://arxiv.org/abs/2011.03861), 2021: local physical learning rules and controlled teaching conditions.
- Li and Mao, [In situ backpropagation training of mechanical neural networks](https://arxiv.org/abs/2404.15471), 2024, with [author code](https://github.com/mao-research-group/Mechanical-neural-networks): a useful reference, with an external optimization procedure that differs from the local material-law objective here.

Existing methods and compatible implementations take precedence over redundant
implementation. No scientific novelty claim follows from the results in this report.

## What remains unresolved

A consequential next test must connect actual sensory exposure to a retained,
specific response on fresh recordings. It must distinguish cross-modal information
from common activity level, pre-existing transmission and recording-specific
backgrounds. The current evidence does not establish that capability.

The audiovisual bipartite topology and fixed transducers already exist in the
codebase; rebuilding them would not resolve the gap. Nor would another successful
scripted association demonstrate general sensory learning. The open work concerns
the physical learning mechanism, continuous recall, informative sensory signals and
a valid evaluation across independent recordings.

## Evidence release and verification

The [manifest](evidence-manifest.json) records SHA-256 hashes for the published saved
measurements. Two internal review-routing fields were omitted from JSON metadata;
the manifest lists their locations and original file hashes. Numerical values and
trajectory files are unchanged. The G183, G189 and G191 packages include numerical snapshots or
trajectories as well as reported measurements. A separate read-only audit during
development checked saved results and relevant state continuity; it was not an
external laboratory replication.

The small plotting utility reads these files directly. It verifies hashes and
regenerates the figures without fitting a model or running a new experiment.

```sh
uv run python tools/render_research_overview.py --verify
uv run python tools/render_research_overview.py
```

This is a **saved-evidence release**, not a complete clean-environment replay
package for every historical run. [Implementation snapshots](reference-source/) are included for code inspection,
with their own source hashes. They retain original import paths and execution
guards and are not a standalone runnable package.

Provenance in the original JSON includes local
experimental revision hashes; those revisions and all their dependencies are not
part of this documentation branch. File integrity, arithmetic reproducibility,
experimental replication and scientific generalization are different claims.
