# VibraSim

Research software for studying memory and learning in simulated physical systems.

VibraSim investigates whether local changes in material properties and bonds can
store experience and produce useful responses to later inputs. The long-term
question is learning from sensory streams without replacing the material with a
trained classifier or language model.

**Current evidence:** controlled fixtures show local memory and finite changes in
mechanical input preference. The tested real-audio and audiovisual transfer tasks
have not demonstrated reliable recognition. Autonomous multimodal learning remains
an open research objective.

![Measured effects and unmet criteria in two representative experiments](docs/research/2026-09/evidence.png)

*Left: only one of three required audio-selectivity contrasts clears its threshold.
Right: mechanical preference reverses in a guided reference model; its separate
return-to-rest requirement fails at every endpoint. These are different experiments
and do not form a combined learning score.*

## What is implemented

| Component | Purpose | Scope |
|---|---|---|
| [World simulator](world/) | Evolve interacting elements, bonds and material state | A rule-based research substrate; its “atoms” and “molecules” are model abstractions, not validated atomic physics |
| [Audiovisual reference code](docs/research/2026-09/reference-source/vibrasim2/) | Study fixed sensory encodings and engineered associations | Archived implementation snapshots; separate from the installed World simulator |
| [Guided mechanical references](docs/research/2026-09/REPORT.md#guided-reference-models) | Isolate local stiffness adaptation, transfer and numerical effects | Constrained numerical models; they have not replaced the production simulator |

![Experimental scope: sensory input, local material changes, and controlled readout](docs/research/2026-09/method.png)

The distinction between these components matters. A result in a small, externally
driven spring fixture is evidence about that fixture, not evidence of a brain,
consciousness, language understanding or unrestricted learning.

## Selected results

Evidence snapshot: **12 September 2026**. Verdicts apply to the registered question
and model, rather than to the project as a whole.

| Study | Result | Interpretation |
|---|---|---|
| G183 — real-audio selectivity | **NULL** | Bell contrast 0.132, dog 0.000, rain −0.010; all three had to reach 0.100 |
| MM3 — audiovisual scene transfer | **NULL** | All five evaluated conditions scored 1/3 on three test recordings at every checkpoint |
| G189 — timing-dependent mechanical transfer | **Mixed** | Transfer depends on exposure timing; the return criterion fails in all seven conditions |
| G191 — finite source-preference reassignment | **Scoped positive finding** | Preference reverses in both tested directions; return fails at all ten endpoints, and acquisition was measured on a sibling state copy |

[Methods, measurements, corrections and evidence files →](docs/research/2026-09/REPORT.md)

These results do not establish continued learning over long periods, robust
recognition across recordings, spontaneous functional specialization, or learning
by repeatedly playing a video. Visible motion and changing bonds are observations;
a learning claim additionally requires a discriminating task and controls.

## Research method

Each confirmatory experiment specifies a question, prediction, comparison and
acceptance criteria before execution. Reports distinguish experimental validity,
prediction accuracy and contribution to the research objective. A valid experiment
can have a negative result; an accurate prediction of failure does not satisfy a
missing capability.

The record includes unsuccessful hypotheses and implementation errors. In the
recent series, a snapshot-decoding error invalidated the first G185 analysis, and
G186's first design was withdrawn before execution because its proposed boundary
intervention did not change the condition. Numerical traversal sensitivity and
residual motion also required explicit diagnosis. These corrections are described
in the [research report](docs/research/2026-09/REPORT.md#corrections-and-numerical-limitations).

Known methods are treated as prior work. Local material memory, directed aging and
physical learning networks predate this project. The current experiments do not
establish scientific novelty. [Prior work and reuse](docs/research/2026-09/REPORT.md#prior-work)

## Run the simulator

Requires Python 3.13 or later and [uv](https://docs.astral.sh/uv/).

```sh
git clone https://github.com/mkupermann/vibrasim.git
cd vibrasim
uv sync --locked --extra dev
uv run python -m world --help
```

For interactive inspection:

```sh
uv run python -m world gui
```

The viewer requires a graphical environment. Running it demonstrates simulation
behavior; it does not reproduce the findings listed above. The evidence package
contains saved measurements from separate experimental revisions.

To verify the published file checksums and regenerate the README figures:

```sh
uv run python tools/render_research_overview.py --verify
uv run python tools/render_research_overview.py
```

These commands inspect saved evidence and render figures. They do not rerun a
learning experiment. See the report for the limits of this evidence release.

## Repository guide

- [Research report and evidence index](docs/research/2026-09/REPORT.md) — current findings and their limits.
- [World source](world/) and [tests](tests/) — simulator implementation and software checks.
- [Concept document](docs/CONCEPT.md) — historical model rationale and terminology.
- [Experiment history](LOGBOOK.md) and [programme record](FRONTIER.md) — detailed development history; older programme statements are not current capability claims.

VibraSim is an experimental research codebase. Its useful output is a testable
model and an auditable record of its capabilities and limitations.
