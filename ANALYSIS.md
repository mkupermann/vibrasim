# EQMOD — Repository Analysis

Generated: 2026-05-11
Scope: full-repo audit (architecture, code, docs, build, quality, risks, recommendations).

---

## 1. Executive summary

EQMOD is an ambitious, single-author research codebase that builds a 3D continuous-substrate
simulator in which four-property "vibrations" bind, via explicit parameterised rules, into
electrons → pairs → triads → atoms → molecules → bridges, on top of which sit STDP +
BTSP-inspired plasticity, replay/dream consolidation, cross-modal recall, a GNW-flavoured
conjunction-trigger layer, and a homeostatic parameter-feedback driver.

The project is unusually disciplined for a solo research repo:

- 100 test files, 313 non-slow + 22 slow tests reported passing.
- Phase-based development (Phase 1 → G18, now entering "flux F1"), with a phase-log discipline.
- Honest scope statements in the README that explicitly retract earlier overclaims
  (Kuramoto framing, "autopoietic", BTSP equivalence, GNW equivalence).
- Pre-registered marker protocol with negative-control runs (`docs/marker_protocol.md`).
- Reproducible calibrations checked into `renders/*.toml`.
- Postgres-backed dashboard (Streamlit) with versioned SQL migrations.

The main risks are concentrated in three areas: (1) `world/physics.py` has grown to ~2,000
lines and is the project's single largest concentration of complexity, (2) the agent / dream
/ self-aware layer has high conceptual ambition but light external validation, and (3) the
build is Python-3.13-only with a Numba pin that is fragile across NumPy major versions.

Overall verdict: **healthy research codebase**, well above typical for a solo project,
with the usual research-code debt concentrated in one or two hot files.

---

## 2. Repository map

```
EQMOD/
├── world/          — simulator core (substrate, physics, dream, self-model)
│   ├── physics.py      ~2,039 LOC — tick loop + all binding/STDP/BTSP/neuron/speech
│   ├── state.py        ~284 LOC  — SoA world container
│   ├── config.py       ~345 LOC  — WorldConfig dataclass + TOML loader
│   ├── dream.py        ~323 LOC  — replay, blending, NREM/REM gating (G15/G18)
│   ├── self_aware.py   ~194 LOC  — G16 conjunction-trigger layer
│   ├── audio_predictor.py ~215 — speech-loop predictor
│   ├── snapshot.py / spatial.py / preview.py / run.py
│   └── flux/           — new F1 subsystem: thermal/Bénard convection draft
│                         (boundary, grid, bridges, audit, decay, plasticity,
│                          structures, quantum, binding, dynamics)
├── agent/          — sensor/effector + curriculum + experiment runners
│   ├── audio_io.py, video_io.py            — real mic/webcam I/O
│   ├── encoder_audio.py, encoder_video.py  — STFT / Gabor → port writes
│   ├── decoder_audio.py, speak.py, talk.py — port reads → speaker
│   ├── babble.py, run_babble_experiment.py — speech-loop experiment (Plan F)
│   ├── autonomous_loop.py, run_autonomous.py — G17 driver
│   ├── run_negative_control.py             — marker protocol negative-control
│   ├── reward.py, loop.py, curriculum_scheduler.py, library.py, convergence.py
│   ├── corpus_audio_feeder.py, corpus_builder.py, youtube_feeder.py
│   └── flux/           — agent-side bindings for the flux subsystem
├── app/            — Streamlit dashboard (Postgres-backed)
│   ├── main.py, ui.py, db.py, viewer.py, snapshot_import.py
│   ├── machine_gui.py, realtime_gui.py, autonomous_monitor.py
│   ├── report.py (PDF), theme/style.css
│   └── pages/1..7 (Dashboard, Sessions, Config, Runs, Results, Amendments, Acceptance)
├── tools/          — offline analysis tools (detect/construct/measure/render/sweep)
│   ├── detect_*.py     — neurons, synapses, networks, membranes
│   ├── construct_*.py  — neuron, synapse, network, membrane
│   ├── measure_*.py    — neuron activity, network activity, synapse plasticity,
│   │                     attention selectivity
│   ├── render_blender.py, render_animation.py, histogram.py
│   ├── sweep.py        — Optuna sweep driver
│   └── synthesize_carrier_firing.py, classify_molecules.py
├── tests/          — 100 test files (24 G-amendments, 7 audio, 7 encoder,
│                                     5 agent, 4 detect, 4 measure, …)
├── db/             — Postgres schema, seed, and numbered migrations
├── docker/         — streamlit Dockerfile
├── docker-compose.yml — postgres:16 + streamlit
├── docs/           — CONCEPT.md, marker_protocol.md, TUTORIAL.md,
│                     CALIBRATION_GUIDE.md, RESEARCH_GUIDE.md, predictive-babble.md,
│                     research_session4/* (5 phase findings + code review),
│                     flux/principle.md + phase-log.md,
│                     medium_articles/2026-05-09-substrate-night.md
├── renders/        — calibration TOMLs, keyframes, calibration plots
├── snapshots/      — saved World snapshots
├── sweeps/         — Optuna sweep outputs
├── world/          — (also __main__.py → `python -m world`)
├── Makefile        — DB migrate + phase-mark targets
├── pyproject.toml  — hatchling, project.name="world", python>=3.13
├── uv.lock         — uv-managed lockfile (~345 KB)
├── README.md       — 31 KB scope statement + status table
└── LOGBOOK.md      — 42 KB research diary
```

Total Python LOC across `world/`, `agent/`, `app/`, `tools/`, `tests/`: **~31,665 LOC**.
Source TODO/FIXME/XXX/HACK markers across non-test code: **1**. (Unusually low.)

---

## 3. Architecture

### 3.1 Substrate (world/)

The substrate is a **Structure-of-Arrays** simulator over a 3D periodic-boundary cube
(default 60×60×60). Two index spaces co-exist in `world.state.World`:

- **Vibrations** (`s_*` arrays): primitive 4-property units — frequency, polarity,
  position, velocity. `move_vibrations` integrates positions; `cull_excess_vibrations`
  enforces population caps; `ambient_regeneration` re-injects vibrations to maintain
  a target density.
- **Nodes** (`k_*` arrays): bound structures with a `k_level` ∈ {1..6} for
  electron/pair/triad/atom/molecule/bridge. `bind_vibrations_to_electrons` (level 1) and
  `bind_nodes_upward` (levels 2..) implement the rule chain; `decay_unstable_nodes`
  and `decay_high_level_nodes` handle dissolution; `apply_scale_repulsion` keeps
  cross-level placement physical.

The hot path through `world.physics.tick(world, dt)` calls, in order:
move → bind → STDP → synaptic transmission → BTSP → bridge-atom propagation →
neuron dynamics → speech-loop coupling → decay → ambient regen → repulsion → cull.

Performance hot spots use `@numba.njit` (a `__pycache__/physics.*.nbi/.nbc` cache shows
`_bind_check_pairs_njit`, `_decay_*_njit`, `_apply_scale_repulsion_njit`, `_move_nodes_njit`
are JIT-compiled). The Plan A.5 acceptance criterion ("60 sim-min ≤ 30 wall-min") is the
budget these JITs are sized against.

### 3.2 Dream / self-aware / autonomous (G14-G17)

- `world/dream.py` (G15/G18): offline replay, concept blending, NREM/REM gating,
  cross-modal hallucination, retention fix. 8/8 dream tests reported passing.
- `world/self_aware.py` (G16): GNW-flavoured conjunction-trigger layer. README is
  careful to call this "one slice of GNW operationalised, not GNW".
- `agent/autonomous_loop.py` (G17): homeostatic parameter-feedback driver. README
  explicitly retracts the earlier "autopoietic" label — this is the kind of correction
  a research codebase usually does not bother to make.

### 3.3 Flux subsystem (in flight, F1a/F1b/F1c)

A new physics layer split out of `world/physics.py` into `world/flux/{grid, bridges,
binding, decay, plasticity, quantum, dynamics, boundary, audit, structures}`. Git log
shows ~20 commits in the past week walking through F1a (binding + node decay) and F1b
(bridges + plasticity + flux-coupled decay), with F1c ("thermal dynamics for Bénard
convection") just planned. This is the right refactor direction — extracting orthogonal
mechanisms from the monolithic `physics.py` into a sub-package with its own tests.

### 3.4 Agent layer (agent/)

The agent layer is the "ports" boundary between substrate and the outside world:

- **Sensors**: `audio_io` (sounddevice, STFT), `video_io` (opencv-python-headless,
  Gabor patches), corpus feeders (`corpus_audio_feeder`, `youtube_feeder`).
- **Encoders**: write port-region vibrations from sensor frames.
- **Decoders**: read port-region firing into audio buffers (`decoder_audio`, `speak`).
- **Experiments**: `babble` + `run_babble_experiment` (Plan F speech-loop),
  `run_autonomous` (G17), `run_negative_control` (marker-protocol negative control),
  `evaluate_babble`.
- **Curriculum**: `curriculum_scheduler`, `library`, `convergence`, `reward`.

This layer is what makes EQMOD more than a toy — it has real mic/camera/speaker I/O
and a corpus pipeline that pulls audio off YouTube.

### 3.5 Dashboard (app/)

Streamlit app fronted by Postgres 16 (5433 host → 5432 container). Seven pages:
Dashboard / Sessions / Config / Runs / Results / Amendments / Acceptance. PDF reports
via reportlab (`app/report.py`). Real-time and "machine" GUIs (`realtime_gui.py`,
`machine_gui.py`) suggest two display modes. DSN passed via env (`VIBRASIM_DSN`).

### 3.6 Tools (tools/)

Offline-analysis CLIs that work against saved snapshots — `detect_*` find structures,
`construct_*` build canonical examples, `measure_*` produce metrics, `render_*` produce
visuals, `sweep.py` drives Optuna. These are the right primitives to have around a
research substrate; they are the equivalent of `objdump`/`nm` for a binary.

### 3.7 Data flow (canonical)

```
sensor frame  ─►  encoder  ─►  vibrations in port region
                                       │
                                       ▼
                          tick(world, dt)  ◄──  WorldConfig (TOML)
                            ├─ bind     (level 1..6)
                            ├─ STDP / BTSP   (bridge plasticity)
                            ├─ neuron dynamics  (level-4 atoms IF)
                            ├─ replay / blend   (dream mode)
                            └─ markers          (self-aware)
                                       │
                                       ▼
                       snapshot ─► tools/ + app/
                       firing log ─► decoder ─► speaker
                       marker_state.json (on 5-marker conjunction)
```

---

## 4. Build, setup, and runbook

### 4.1 Prerequisites

- Python **3.13** (pinned; pyproject `requires-python = ">=3.13"`).
- Docker Desktop (for Postgres + Streamlit dashboard).
- macOS-arm64 or Linux-x86_64 (the two CI-verified platforms).
- For the agent layer: a working mic, speaker, and webcam, plus PortAudio
  (sounddevice) at the OS level. On macOS: `brew install portaudio`.
- `uv` recommended (uv.lock is checked in).

### 4.2 First-time setup

```bash
# 1. Clone and create the env
cd EQMOD
uv venv -p 3.13 .venv
source .venv/bin/activate
uv pip install -e ".[dev,dashboard,agent]"

# 2. Start Postgres + Streamlit
docker compose up -d postgres
make db-migrate

# 3. Run the test suite (fast slice)
pytest -m "not slow"

# 4. Run the full suite (slow tests included)
pytest

# 5. Smoke-run the substrate
python -m world run --config renders/calibration_session3.toml --duration 60 \
                    --snapshot-dir snapshots/smoke

# 6. Dashboard
docker compose up -d streamlit
open http://localhost:8502
```

### 4.3 Common commands

| Goal | Command |
|---|---|
| Phase-1 first-atom reproduction | `python -m world run --config renders/calibration_session3.toml --duration 30 --seed 42` |
| Phase-2 molecule reproduction | `python -m world run --config renders/calibration_phase2_acceptance.toml --duration 60` |
| Live PyVista preview | add `--preview` |
| Snapshot import to DB | `python -m app.snapshot_import <path>` |
| Optuna sweep | `python -m tools.sweep …` |
| Babble experiment | `python -m agent.run_babble_experiment …` |
| Negative control (markers) | `python -m agent.run_negative_control …` |
| Autonomous G17 driver | `python -m agent.run_autonomous …` |
| DB migrate | `make db-migrate` |
| Mark a plan implemented | `make db-migrate-planX-mark-implemented MERGE_SHA=<sha>` |

### 4.4 Reproducibility checklist (from README + LOGBOOK)

- Phase-1 first atom: `renders/calibration_session3.toml`, `--seed 42`, atom at t=13.4 s.
- Phase-2 ≥5 molecule species in 60 s: `renders/calibration_phase2_acceptance.toml`.
- Acceptance marker fires only under trained-engram run, NOT under the negative
  control. `docs/marker_protocol.md` defines pass criteria; touching thresholds after
  the fact is excluded by protocol.

---

## 5. Code review

### 5.1 Strengths

1. **SoA layout + Numba JIT.** Hot loops are written against contiguous NumPy arrays
   keyed by index, not Python objects. Cache artefacts confirm the JIT path is live
   for binding, decay, repulsion, and motion.
2. **Honest README.** The "What this project is not" section retracts overclaims
   (Kuramoto framing, "autopoietic", GNW equivalence, BTSP equivalence) in a way that
   is rare in research code. Marker protocol is pre-registered.
3. **Test density.** 100 test files for ~14k LOC of production code is ≈ 7 LOC of
   production per test file. The 24 `test_amendment_G*.py` files map 1:1 to the phase
   chain — every amendment lands with its acceptance test.
4. **Phase log and logbook discipline.** `LOGBOOK.md` (42 KB) and
   `docs/flux/phase-log.md` make it possible to reconstruct *why* a change was made,
   not just *what*.
5. **Schema migrations are numbered and ordered.** `db/migrations/0001..0009` with a
   Makefile that applies them deterministically.
6. **Calibrations are checked-in artefacts.** `renders/*.toml` makes "session-3b" or
   "phase-2 acceptance" reproducible by file, not by lore.
7. **Flux refactor is the right move.** Splitting `physics.py` into a `world/flux/`
   sub-package one mechanism at a time, behind tests, is exactly how a 2,000-line hot
   file should be broken up.

### 5.2 Weaknesses and risks

1. **`world/physics.py` is the elephant.** ~2,039 LOC, ~25 top-level functions,
   roughly 12 distinct mechanisms (move, bind L1, bind L≥2, STDP, transmission,
   BTSP, bridge-atom propagation, neuron dynamics, speech-loop, decay-unstable,
   decay-high-level, repulsion, ambient regen, cull). Every new amendment widens it.
   The flux refactor addresses this but only for one mechanism at a time.
   *Recommendation:* keep the same split for STDP/BTSP/synaptic transmission;
   target ≤500 LOC per file.

2. **Python-3.13 pin is aggressive.** `requires-python = ">=3.13"` will lock out
   any contributor not on the bleeding edge. CI-verified on macOS-arm64 + Linux-x86_64
   only. *Recommendation:* relax to `>=3.12` if there is no actual 3.13 feature in use,
   or document the 3.13 feature that requires the pin.

3. **Numba × NumPy coupling is fragile.** `numpy >= 1.26, <3.0` paired with
   `numba >= 0.61, <0.70`. Numba 0.6x supports NumPy 2.x only in recent point releases;
   a fresh `uv pip install` against a NumPy 2.2+ wheel may break the JIT cache.
   *Recommendation:* pin NumPy to `<2.3` until Numba ships a tested matrix, and add a
   `pytest` smoke that exercises every `@njit` once at import-time-equivalent so a JIT
   regression is caught before the long-running tests.

4. **`__pycache__/` directories with `.nbi`/`.nbc` are committed.** They are present
   on disk and not in `.gitignore` excerpts above — verify they are not pushed.

5. **Dashboard secret-handling is weak.** `Makefile` literally contains
   `PGPASSWORD=***` (redacted to `***` in the file). Either it is being templated at
   call time (then say so in a comment) or it is a real placeholder that breaks.
   *Recommendation:* read `PGPASSWORD` from env in the Makefile and fail fast if unset.

6. **Two GUIs (`realtime_gui.py`, `machine_gui.py`) alongside the Streamlit pages.**
   Unclear which is current; risk of bit-rot. *Recommendation:* a one-paragraph
   README in `app/` documenting which entry point is canonical.

7. **Big binary PNGs at repo root** (`vibrasim_*.png`, ~700 KB total). Fine for now,
   but if more accumulate, move under `docs/assets/` and reference from there.

8. **Coverage isn't measured (no `pytest-cov` in dev deps).** With 100 test files,
   adding `pytest --cov=world --cov=agent --cov=app` would let amendments land with a
   coverage delta instead of a vibe check.

9. **Concept drift between amendments and code structure.** G14/G15/G16/G17 each cut
   horizontally across `physics.py`, `dream.py`, `self_aware.py`, and the agent loop.
   The flux sub-package is the right pattern; consider applying it: `world/plasticity/`,
   `world/dream/`, `world/markers/`.

10. **`agent/flux/` and `world/flux/` are parallel namespaces.** Easy to confuse.
    Document the boundary explicitly (substrate side vs. agent side of the flux API)
    or merge.

### 5.3 Single-issue spot checks

- `world/physics.py:323 apply_stdp` and `world/physics.py:603 apply_btsp` likely
  share state-update boilerplate (firing windows, eligibility traces). A shared
  `plasticity` helper would shrink both.
- `world/physics.py:1834 _emit_vibrations` and `world/physics.py:1878 apply_speech_loop`
  are the only writers into the audio_output port — they should be the only ones, and
  a unit test should assert that.
- `world/state.World` (284 LOC) is the right size; do not let it grow.
- 100 test files is healthy, but `tests/test_amendment_G*.py` filenames embed the
  phase tag — if a phase gets renamed, tests are silently orphaned. Consider mapping
  phases to test directories (`tests/amendments/g16_self_aware/test_*.py`).

---

## 6. Documentation review

- `README.md` (31 KB): excellent. Dual-audience structure (plain English + technical
  detail), explicit "is / is not" scope, status table with test counts, references to
  protocol.
- `docs/CONCEPT.md`: long-form concept paper, v3.0 with amendment trail back to the
  German original. The amendment notes at the top are the right way to evolve a
  research document without rewriting history.
- `docs/marker_protocol.md`: pre-registers five markers + negative-control criterion.
- `docs/TUTORIAL.md` + `docs/CALIBRATION_GUIDE.md` + `docs/RESEARCH_GUIDE.md`: cover
  hands-on, calibration, and research workflow respectively.
- `docs/research_session4/`: five phase-findings files + a code review — internal
  research process is documented.
- `docs/flux/principle.md` + `phase-log.md`: the flux subsystem has its own design doc
  and ongoing log. Mirror this for any future sub-package.
- `LOGBOOK.md` (42 KB): chronological research diary. Highly valuable; do not let it
  grow past ~100 KB before splitting per-month.

**Missing / would be high-leverage to add:**

- `docs/ARCHITECTURE.md` summarising §3 of this file (data flow + tick order +
  module boundaries) so newcomers do not have to read `physics.py` to find the entry
  point.
- `docs/CONTRIBUTING.md` covering: Python 3.13 setup, Numba quirks, how to add an
  amendment (test-first, phase-log entry, README status row, marker-protocol impact
  statement).
- `app/README.md`: which of `main.py`, `realtime_gui.py`, `machine_gui.py`,
  `autonomous_monitor.py` is the canonical Streamlit entry.

---

## 7. Test & CI posture

- 100 test files, reportedly 313 non-slow + 22 slow passing.
- `pytest.ini_options` defines a `slow` marker — good discipline.
- No coverage tool wired in.
- No GitHub Actions workflow file visible at repo root (`.github/` not listed).
  *Verify and add* a CI workflow: `pytest -m "not slow"` on push, full suite + slow
  nightly. macOS-arm64 + Linux-x86_64 matrix matches the README's verified set.

---

## 8. Security & ops notes

- Postgres password (`vibrasim`) is plain-text in `docker-compose.yml`. Acceptable for
  local dev; do not deploy as-is.
- `PGPASSWORD=***` in `Makefile`: clarify whether this is a placeholder or a real
  literal that was scrubbed for display.
- `agent/youtube_feeder.py` pulls media via yt-dlp — make sure rate limits and licence
  terms are noted in `docs/RESEARCH_GUIDE.md`.
- `tools/render_blender.py` likely shells out to Blender; if it ever runs untrusted
  config, audit the call site.

---

## 9. Prioritised recommendations

**P0 (do next sprint):**

1. Continue the flux-style decomposition of `world/physics.py`. Next targets:
   `world/plasticity/{stdp,btsp,transmission}` and `world/neurons/dynamics.py`.
2. Add a GitHub Actions workflow: `pytest -m "not slow"` on PR, full suite nightly,
   on a macOS-arm64 + ubuntu-latest matrix.
3. Add `pytest-cov` and publish a coverage badge; gate PRs on no-coverage-regression.
4. Verify `.gitignore` excludes `world/__pycache__/*.nbi` and `*.nbc`.

**P1 (this month):**

5. Write `docs/ARCHITECTURE.md` and `docs/CONTRIBUTING.md`.
6. Add an `app/README.md` clarifying canonical Streamlit entry.
7. Pin `numpy < 2.3` until Numba ships a tested matrix; add a JIT-warm-up smoke test.
8. Move root-level PNGs into `docs/assets/`.

**P2 (when convenient):**

9. Relax `requires-python` to `>=3.12` unless a 3.13-specific feature is in use.
10. Introduce `tests/amendments/g14_btsp/`, `g15_dream/`, etc., so test paths track
    the phase taxonomy instead of filenames doing it.
11. Consider extracting the agent's curriculum + library + reward into a
    `agent/training/` sub-package — the agent layer is also approaching the size at
    which a sub-package starts paying for itself.

---

## 10. One-paragraph verdict

EQMOD is the kind of repo that, from the outside, looks like a normal research
substrate simulator, and from the inside is much more disciplined than that: scope is
pre-registered, claims are retracted on contact with reality, every amendment lands
with tests, and the refactor instinct (flux sub-package) shows up at exactly the right
moment in the file-size curve. The work that remains is mostly mechanical — finish the
sub-package split, wire CI, add coverage, write the architecture and contributing docs
— and none of it is research-risk. The research-risk lives where the README says it
lives: in whether the binding-rule chain plus replay plus markers actually produces
something that passes the pre-registered negative control over long horizons. That
part is honest, and that is the most important thing about this codebase.
