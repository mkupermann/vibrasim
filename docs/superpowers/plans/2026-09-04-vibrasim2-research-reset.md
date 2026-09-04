# Vibrasim II Research Reset Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Establish Vibrasim II/P0 as the sole active research question, implement its frozen reciprocal-channel verifier, add an observer-isolated 3D view, and present the repository honestly as Michael's public research laboratory.

**Architecture:** The work is ordered rather than parallel: governance and test safety first, an isolated deterministic P0 kernel second, a one-way observation process third, and the public README only after its commands and claims can be verified. Scientific records flow from the authoritative simulator to append-only raw artifacts, then into a pure verdict function; the viewer receives copied snapshots after persistence and has no return path.

**Tech Stack:** Python 3.13, NumPy float64, pytest 8, PyVista 0.48-compatible rendering, `multiprocessing` with `spawn`, JSON/JSONL plus NPZ artifacts, Hatchling, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-09-03-vibrasim2-research-reset-design.md`

## Global Constraints

- Treat `docs/amendments/v2_p0_reciprocal_channel.md` as frozen; its canonical SHA-256 is `28992a8b131100ed4eb2cd9147ddea7b3251921777211a63bb4b64e5524ca9e1`, its Git blob is `e5460f0b9ce837ec551bd0c3fb26d269c180f61b`, and its originating commit is `e922ef2753828535b7c3229e4ed6849015794242`.
- Do not import or modify `world/physics.py` from Vibrasim II.
- Use only IEEE-754 float64 state arrays in P0.
- Registered P0 constants are `grid_shape=(32, 32)`, `c=1.0`, `k_b=0.5`, `g=1.0`, `dt=0.05`, `sigma=2.0`, `steps=2000`, `frame_stride=10`; the convergence cells use `dt=0.025` and `steps=4000` for the same physical duration.
- Registered source centres are exactly `(4,16)`, `(16,4)`, and `(4,4)`; P0 has no RNG and no seed option.
- P0 source/test implementation, execution, and correction in Tasks 4–8 count against its frozen 5.5-hour hard ceiling; this pre-implementation plan and Blocks A, C, and D are non-experimental infrastructure and do not.
- Start a versioned machine-readable wall-clock ledger immediately before the first Task 4 edit and close its first interval only after Task 8's complete focused P0 suite passes. Task 14 may repeat the unchanged suite as release verification outside that implementation interval; any P0 code or test correction discovered there opens a new interval. The productive CLI and pre-run verifier require a closed cumulative duration strictly below 19,800 seconds. At or above that ceiling, stop before data, record the overrun, and freeze a successor registration rather than extending the budget silently.
- No implementation test may write under `archive/run-logs/`, `Path.home()`, or `~/.eqmod`; use `tmp_path` only.
- Do not start a scientific P0 run while implementing this plan.
- The viewer is optional, lossy, observer-only, and incapable of changing simulation state, records, metrics, or verdict.
- Preserve historical results and failed paths. Do not manufacture a cleaner scientific history.
- External text is written from Michael's perspective. First-person factual claims require support in his existing README, commits, or logbook.
- Do not name an AI system as author or contributor.
- Do not push, alter branch protection, publish a screenshot as evidence, or make a licensing decision without Michael's separate concrete approval.
- Before Task 4, commit `docs/vibrasim2/P0_OUTPUT_BASELINE.json` with the exact pre-implementation filesystem inventory under `archive/run-logs/v2-p0`; the current expected inventory is empty. Final verification compares the real tree, including ignored and untracked files, against this baseline.

## Scope Check and Delivery Order

The four blocks share contracts and are therefore one ordered plan rather than four independent plans: Block B supplies snapshots to Block C, and Block D may document only commands and behavior verified in Blocks A through C. Every numbered task is nevertheless a separate review and commit boundary.

## File Responsibility Map

- `docs/amendments/v2_p0_scope_addendum.md`: pre-data scope exception for supplied P0 coupling edges; no threshold changes.
- `AGENTS.md`, `CLAUDE.md`, `FRONTIER.md`, `LOGBOOK.md`: current programme authority and append-only transition record.
- `tools/test_safety.py`, `tests/conftest.py`, `pyproject.toml`: central safe-test classification and default deselection.
- `vibrasim2/p0/types.py`: immutable P0 configurations, cells, states, records, and result types.
- `vibrasim2/p0/budget.py` and `docs/vibrasim2/P0_BUDGET_LEDGER.json`: pure validation and versioned evidence for the frozen implementation budget.
- `vibrasim2/p0/fixtures.py`: registered sites, topologies, cell matrix, and initial field.
- `vibrasim2/p0/dynamics.py`: Hamiltonian forces and velocity-Verlet step only.
- `vibrasim2/p0/energy.py`: exact energies, coupling powers, integrals, and trace metrics.
- `vibrasim2/p0/artifacts.py`: raw JSONL/NPZ journal, atomic JSON, reload, and canonical scientific digest.
- `vibrasim2/p0/verdict.py`: threshold constants, evidence construction, Stage-A gate, and pure ordered verdict.
- `vibrasim2/p0/runner.py`: registered cell execution and stage orchestration.
- `vibrasim2/p0/cli.py`: guarded CLI with no unregistered scientific axes.
- `vibrasim2/observation.py`: process-safe neutral frame and envelope contracts.
- `vibrasim2/p0/observation.py`: deterministic 2D-state-to-3D-observation projection.
- `vibrasim2/observation_transport.py`: non-blocking latest-only publisher.
- `vibrasim2/viewer_process.py`: pure controller, spawn entry point, replay, and bounded shutdown.
- `vibrasim2/wireframe.py`: PyVista rendering only; no simulator callback.
- `README.md`: concise public-laboratory entrance after implementation verification.

## Spec Traceability

- Spec §§1–4: Tasks 1 and 13 establish the sole active programme, historical status, and pre-data scope addendum.
- Spec §5: Tasks 6–8 and 12 enforce raw-record-first flow, pure verdict, atomic result, and one-way observation.
- Spec §6: Tasks 9 and 10 define neutral supplied edges and the exact 3D observation embedding.
- Spec §§7–8: Tasks 2, 5–8, and 10–12 cover safe tests, numerical gates, operational aborts, replay, and shutdown.
- Spec §9: Tasks 3 and 13 repair local exposure, links, commands, status, and unsupported claims.
- Spec §§10–11: Task 14 verifies acceptance criteria and reports observer, platform, scope, and historical-rewrite risks.
- Spec §§12–13: the global budget rule and Task 14 preserve the no-data implementation boundary and explicit external decision gates.

---

### Task 1: Freeze the Programme Transition and P0 Scope

**Files:**
- Create: `docs/amendments/v2_p0_scope_addendum.md`
- Create: `docs/archive/vibrasim_i/FRONTIER_2026-08-13.md`
- Create: `docs/vibrasim2/P0_OUTPUT_BASELINE.json`
- Create: `tests/vibrasim2/test_program_authority.py`
- Modify: `docs/vibrasim2/CHARTER.md`
- Modify: `docs/vibrasim2/P0_IMPLEMENTATION_PLAN.md`
- Modify: `AGENTS.md`
- Modify: `CLAUDE.md`
- Modify: `FRONTIER.md`
- Modify: `LOGBOOK.md`
- Modify: `docs/BELIEF_PATH.md`
- Modify: `docs/DISCIPLINE_SHARP.md`
- Modify: `docs/amendments/bp_c6c_transverse_readability.md`
- Do not modify: `docs/amendments/v2_p0_reciprocal_channel.md`

**Interfaces:**
- Consumes: frozen P0 pre-registration and the approved design spec.
- Produces: one authoritative current programme, a frozen scope addendum, and machine-checked historical labels used by every later task.

- [ ] **Step 1: Write the failing programme-authority tests**

```python
# tests/vibrasim2/test_program_authority.py
import re
from hashlib import sha256
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ACTIVE_QUESTION = "V2-P0 reciprocal field–matter channel"


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def canonical_lf_bytes(path: str) -> bytes:
    text = (ROOT / path).read_bytes().decode("utf-8")
    return text.replace("\r\n", "\n").encode("utf-8")


def test_vibrasim2_is_the_only_active_programme():
    assert "## Active programme (2026-09-04) — Vibrasim II" in read("AGENTS.md")
    assert "## Active programme (2026-09-04) — Vibrasim II" in read("CLAUDE.md")
    assert read("AGENTS.md") == read("CLAUDE.md")
    frontier = read("FRONTIER.md")
    assert "## Active programme: Vibrasim II / P0" in frontier
    assert "one active question" in frontier.lower()
    assert "reciprocal" in frontier.lower()
    for path in ("AGENTS.md", "CLAUDE.md", "FRONTIER.md", "LOGBOOK.md"):
        assert ACTIVE_QUESTION in read(path), path
    for path in ("AGENTS.md", "CLAUDE.md", "FRONTIER.md"):
        current = read(path)
        assert "Active programme: belief path" not in current
        assert "active programme (belief path)" not in current.lower()
        assert not re.search(
            r"active programme[^\n]{0,100}belief path", current, flags=re.IGNORECASE
        )


def test_vibrasim1_authorities_are_visibly_historical():
    assert "historical programme charter — frozen" in read("docs/BELIEF_PATH.md")
    assert "historical operating doctrine — frozen" in read("docs/DISCIPLINE_SHARP.md")
    assert "UNEXECUTED DRAFT — ARCHIVED" in read(
        "docs/amendments/bp_c6c_transverse_readability.md"
    )
    assert (ROOT / "docs/archive/vibrasim_i/FRONTIER_2026-08-13.md").is_file()


def test_frozen_p0_preregistration_is_unchanged():
    digest = sha256(canonical_lf_bytes("docs/amendments/v2_p0_reciprocal_channel.md")).hexdigest()
    assert digest == "28992a8b131100ed4eb2cd9147ddea7b3251921777211a63bb4b64e5524ca9e1"


def test_scope_addendum_changes_no_registered_bar():
    addendum = read("docs/amendments/v2_p0_scope_addendum.md")
    assert "FROZEN ADDENDUM — BEFORE IMPLEMENTATION OR DATA" in addendum
    assert "supplied coupling edges" in addendum
    assert "No model, fixture, constant, threshold, verdict predicate, or budget changes" in addendum
    assert "no scientific verdict" in addendum.lower()
    digest = sha256(canonical_lf_bytes("docs/amendments/v2_p0_scope_addendum.md")).hexdigest()
    assert digest == "f0c20858ffaf3750320bd05cc1b120222264e7bd3e84109406f7b4a3cb7d9cb0"


def test_p0_output_baseline_is_empty_before_implementation():
    assert read("docs/vibrasim2/P0_OUTPUT_BASELINE.json") == (
        '{"files":[],"root":"archive/run-logs/v2-p0","schema_version":1}\n'
    )
```

- [ ] **Step 2: Run the tests and confirm the current authority conflict**

Run: `uv run pytest -o addopts="-v --strict-markers" tests/vibrasim2/test_program_authority.py -q`

Expected: FAIL because the addendum/archive files do not exist and the active-programme labels still conflict.

- [ ] **Step 3: Add the exact pre-data scope addendum**

Write these exact UTF-8/LF bytes, including one trailing newline. Their canonical
SHA-256 is `f0c20858ffaf3750320bd05cc1b120222264e7bd3e84109406f7b4a3cb7d9cb0`
and Git blob is `ff77a39fb5f9ac9f895d23a96ea9ff3f3b423b37`:

```markdown
# V2-P0 scope addendum — supplied coupling edges

**Status:** FROZEN ADDENDUM — BEFORE IMPLEMENTATION OR DATA.

This addendum scopes `docs/amendments/v2_p0_reciprocal_channel.md`, originating
at commit `e922ef2753828535b7c3229e4ed6849015794242` with Git blob
`e5460f0b9ce837ec551bd0c3fb26d269c180f61b`. The original remains unchanged.

P0's six edges are supplied coupling edges: a deterministic verifier fixture,
not formed, maintained, or persistent bonds. P0 alone exempts these supplied
edges from formation energy and finite lifetime. P1 and every later rung remain
subject to the charter's bond-formation, turnover, and persistence constraints.

A P0 PASS establishes only an energy-consistent, reciprocal,
topology-sensitive channel in this engineered fixture. It says nothing about
bond formation, turnover, persistence, individuation, memory, talent, or life.

No model, fixture, constant, threshold, verdict predicate, or budget changes.
If required raw data or `result.json` cannot be written atomically and read
back, the run is operationally incomplete and has no scientific verdict.
```

- [ ] **Step 4: Make current and historical programme status unambiguous**

Perform these exact document operations:

- copy the pre-edit `FRONTIER.md` verbatim to `docs/archive/vibrasim_i/FRONTIER_2026-08-13.md`;
- replace the live `FRONTIER.md` with a one-screen P0 board naming the charter, frozen pre-registration, scope addendum, latest logbook entry, and G174's historical `INVARIANT (NULL)`;
- change both `AGENTS.md` and `CLAUDE.md` to the same Vibrasim-II reading order: charter, frozen P0 contract, scope addendum, live frontier, newest logbook entry;
- add `**Status:** historical programme charter — frozen; superseded by Vibrasim II.` to `docs/BELIEF_PATH.md`;
- add `**Status:** historical operating doctrine — frozen; retained as method history.` to `docs/DISCIPLINE_SHARP.md`;
- change only the status line of `bp_c6c_transverse_readability.md` to `**Status: UNEXECUTED DRAFT — ARCHIVED.**`; retain both `k_h=8` and `k_h=40` so the unresolved draft inconsistency remains visible;
- add the P0 supplied-edge exception and neutral observation terminology to the charter;
- replace `docs/vibrasim2/P0_IMPLEMENTATION_PLAN.md` with a pointer to this plan and label the old nine-line sequence superseded;
- append, without editing earlier entries, a `2026-09-04 — Vibrasim II programme transition` entry to `LOGBOOK.md` naming the decision, the preserved G174 NULL, archived unexecuted G175 draft, frozen addendum, and the fact that no P0 data were generated.
- use the canonical active-question label `V2-P0 reciprocal field–matter channel` verbatim in `AGENTS.md`, `CLAUDE.md`, live `FRONTIER.md`, and the appended `LOGBOOK.md` transition; Task 13 adds the same label to README.
- create `docs/vibrasim2/P0_OUTPUT_BASELINE.json` with exactly `{"files":[],"root":"archive/run-logs/v2-p0","schema_version":1}` plus a trailing newline; first verify that the directory is absent or contains no files, including hidden and ignored files. If it is not empty, stop and document the existing inventory instead of deleting it.

- [ ] **Step 5: Run the authority tests and immutable-document checks**

Run: `uv run pytest -o addopts="-v --strict-markers" tests/vibrasim2/test_program_authority.py -q`

Expected: PASS.

Run: `git diff --exit-code 51efc975 -- docs/amendments/v2_p0_reciprocal_channel.md`

Expected: exit 0 and no output.

Run: `git hash-object --path=docs/amendments/v2_p0_scope_addendum.md docs/amendments/v2_p0_scope_addendum.md`

Expected: exactly `ff77a39fb5f9ac9f895d23a96ea9ff3f3b423b37`.

Run: `git diff --check`

Expected: exit 0 and no whitespace errors.

- [ ] **Step 6: Commit the programme transition atomically**

```powershell
git add AGENTS.md CLAUDE.md FRONTIER.md LOGBOOK.md docs/BELIEF_PATH.md docs/DISCIPLINE_SHARP.md docs/amendments/bp_c6c_transverse_readability.md docs/amendments/v2_p0_scope_addendum.md docs/archive/vibrasim_i/FRONTIER_2026-08-13.md docs/vibrasim2/CHARTER.md docs/vibrasim2/P0_IMPLEMENTATION_PLAN.md docs/vibrasim2/P0_OUTPUT_BASELINE.json tests/vibrasim2/test_program_authority.py
git commit -m "docs: freeze Vibrasim II programme transition"
```

---

### Task 2: Make Bare Pytest Safe by Construction

**Files:**
- Create: `tools/test_safety.py`
- Create: `tests/test_audit_test_safety.py`
- Modify: `tests/conftest.py`
- Modify: `pyproject.toml`

**Interfaces:**
- Consumes: Python source paths and source text only; never imports audited tests.
- Produces: `detect_hazards(relative_path: str, source: str) -> frozenset[str]`, `classify_test_source(relative_path: str, source: str) -> frozenset[str]`, pre-import default quarantine, a default-runtime socket guard, and effective pytest marks for deliberate opt-in collection.

- [ ] **Step 1: Write failing classifier and known-hazard tests**

```python
# tests/test_audit_test_safety.py
from pathlib import Path

from tools.test_safety import classify_test_source, find_unclassified_hazards

pytest_plugins = ("pytester",)

ROOT = Path(__file__).resolve().parents[1]


def source(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_home_output_is_external():
    marks = classify_test_source(
        "tests/test_probe.py",
        "from pathlib import Path\nOUT = Path.home() / '.eqmod'\n",
    )
    assert "external" in marks


def test_large_named_resource_is_resource_intensive():
    marks = classify_test_source(
        "tests/test_probe.py",
        "N_NEURONS = 1_000_000\nRUN_DURATION_SECONDS = 4 * 3600.0\n",
    )
    assert "resource_intensive" in marks


def test_large_seed_offset_is_not_a_resource_claim():
    marks = classify_test_source(
        "tests/test_probe.py",
        "child_seed = seed + 1_000_000\n",
    )
    assert "resource_intensive" not in marks


def test_bet_tree_is_always_an_experiment():
    assert "experiment" in classify_test_source("tests/bet/test_x.py", "def test_x(): pass\n")


def test_gui_module_is_always_quarantined():
    assert "gui" in classify_test_source("tests/test_wireframe_gui.py", "def test_x(): pass\n")


def test_network_process_and_hardware_calls_are_external():
    probes = (
        "import requests\ndef test_x(): requests.get('https://example.invalid')\n",
        "import subprocess\ndef test_x(): subprocess.run(['curl', 'https://example.invalid'])\n",
        "import serial\ndef test_x(): serial.Serial('COM1')\n",
    )
    for probe in probes:
        assert "external" in classify_test_source("tests/test_probe.py", probe)


def test_known_dangerous_modules_are_quarantined():
    paths = (
        "tests/bet/test_bet_008_lr_validation_beta_zero.py",
        "tests/bet/test_bet_076_brian2_1m_ceiling.py",
        "tests/bet/test_bet_079_long_run_4h.py",
        "tests/bet/test_bet_080_long_run_12h.py",
        "tests/bet/test_bet_081_audio_cortex.py",
        "tests/flux/test_training_corpus_manifest.py",
    )
    for path in paths:
        marks = classify_test_source(path, source(path))
        assert marks & {"experiment", "external", "resource_intensive", "slow"}, path


def test_real_suite_has_no_unclassified_hazard():
    assert find_unclassified_hazards(ROOT / "tests") == []
```

- [ ] **Step 2: Run the focused audit test and verify it fails**

Run: `uv run pytest -o addopts="-v --strict-markers" tests/test_audit_test_safety.py -q`

Expected: FAIL because `tools.test_safety` does not exist.

- [ ] **Step 3: Implement the AST-only classifier and CLI audit**

Implement these exact rules in `tools/test_safety.py`:

```python
EXCLUSION_MARKERS = frozenset({"experiment", "slow", "external", "resource_intensive", "gui"})
RESOURCE_NAMES = ("NEURON", "TICK", "STEP", "DURATION", "HOUR", "SAMPLE", "PARTICLE")


def classify_test_source(relative_path: str, source: str) -> frozenset[str]:
    hazards = detect_hazards(relative_path, source)
    marks: set[str] = set()
    normalized = relative_path.replace("\\", "/")
    if normalized.startswith("tests/bet/"):
        marks.add("experiment")
    if normalized.endswith("_gui.py"):
        marks.add("gui")
    if "home_output" in hazards or "expanded_external_path" in hazards or "external_call" in hazards:
        marks.add("external")
    if "large_resource" in hazards or "hour_scale_duration" in hazards:
        marks.add("resource_intensive")
    return frozenset(marks)
```

`detect_hazards` must parse with `ast.parse`, flag executable `Path.home()` and zero-argument `.expanduser()` calls, evaluate numeric assignment expressions made only from numeric constants and `+`, `-`, `*`, `/`, and flag values at least `1_000_000` only when the assignment name contains a `RESOURCE_NAMES` token. It must flag duration assignments of at least `3600` seconds when the name contains `DURATION` or `HOUR`. Resolve imported aliases and flag calls rooted at `requests`, `httpx`, `aiohttp`, `urllib.request`, `socket`, `ftplib`, `smtplib`, `paramiko`, `boto3`, `botocore`, `serial`, `sounddevice`, or `pyaudio`, plus `os.system`, `os.popen`, and `subprocess.run`, `Popen`, `call`, `check_call`, or `check_output`, as `external_call`. Ignore docstrings, comments, and arithmetic assigned to names containing `SEED`.

`find_unclassified_hazards(tests_root)` walks `test_*.py` recursively, combines source-derived marks with literal `pytest.mark.<name>` attributes found by AST, and returns `path: hazard` strings only when hazards exist without any effective exclusion marker. Its `main()` prints the violations and returns 1, otherwise prints the number of audited modules and returns 0.

`gui` is inferred only from the explicit `_gui.py` filename convention; Task 12
also places literal `gui` and `external` markers on every real-display test.

In `tests/conftest.py`, the default path also installs a process-wide Python
socket guard in `pytest_configure`, before test-module collection. Replace
`socket.socket` with a subclass whose `connect` and `connect_ex` raise
`RuntimeError("network disabled in safe pytest; use --include-quarantined")`,
and replace `socket.create_connection` and `socket.getaddrinfo` with the same
guard. Restore all four originals in `pytest_unconfigure`. Do not install this
guard when `--include-quarantined` is present. Expose small idempotent
`install_socket_guard(socket_module)` and `restore_socket_guard(socket_module,
originals)` helpers so a fake socket namespace can prove all four replacements
and exact restoration without touching the parent pytest process. Add a
`pytester` module that deliberately evades the static alias resolver via
`importlib.import_module("so" + "cket")`; inside its test, assert that guarded
`socket().connect`, `socket().connect_ex`, `create_connection`, and `getaddrinfo`
each raise the declared runtime error. This module must be collected by default,
which proves the runtime guard rather than the AST quarantine. Separately prove
that an explicitly marked external module is collectable only with
`--include-quarantined -m external`.

- [ ] **Step 4: Quarantine classified files before module import**

Add these hooks to `tests/conftest.py` without changing existing fixtures:

```python
from pathlib import Path

from tools.test_safety import classify_test_source

REPO_ROOT = Path(__file__).resolve().parent.parent


def pytest_addoption(parser):
    parser.addoption(
        "--include-quarantined",
        action="store_true",
        default=False,
        help="collect tests classified as experiment, external, resource-intensive, slow, or GUI",
    )


def pytest_ignore_collect(collection_path, config):
    path = Path(str(collection_path)).resolve()
    if config.getoption("--include-quarantined") or not path.name.startswith("test_"):
        return None
    if path.suffix != ".py" or REPO_ROOT not in path.parents:
        return None
    relative = path.relative_to(REPO_ROOT).as_posix()
    source_text = path.read_text(encoding="utf-8")
    effective = effective_exclusion_markers(relative, source_text)
    return bool(effective)


def pytest_itemcollected(item):
    path = Path(str(item.path)).resolve()
    relative = path.relative_to(REPO_ROOT).as_posix()
    source_text = path.read_text(encoding="utf-8")
    for marker_name in sorted(effective_exclusion_markers(relative, source_text)):
        item.add_marker(getattr(pytest.mark, marker_name))
```

`effective_exclusion_markers` is an AST-only union of inferred classifications
and literal module/class/function `pytest.mark.<name>` decorators. The default
hook therefore skips quarantined modules before importing them. Deliberate runs
must supply `--include-quarantined`; `-m` then selects the requested marked
items. Returning `None` leaves safe files to pytest's normal collection.

Register these markers in `pyproject.toml` and make the exclusion expression part of `addopts`:

```toml
addopts = "-v --strict-markers -m 'not experiment and not slow and not external and not resource_intensive and not gui'"
markers = [
    "slow: unsuitable for the fast feedback loop",
    "experiment: executes or evaluates a scientific research run",
    "external: requires network, hardware, a user data set, notification service, or home-directory state",
    "resource_intensive: requests hour-scale runtime or unusually large memory/CPU resources",
    "gui: requires a real display and graphics stack",
]
```

- [ ] **Step 5: Prove the auditor and default collection are safe**

Run: `uv run pytest -o addopts="-v --strict-markers" tests/test_audit_test_safety.py tests/test_audit_silent_pass.py -q`

Expected: PASS.

Run: `uv run python tools/test_safety.py`

Expected: exit 0 and `0 unclassified hazards`.

Run: `uv run pytest --collect-only -q`

Expected: exit 0; every effectively marked research or hazard module is quarantined before import. Report the measured ignored/deselected counts from this run; do not hard-code them in documentation. In `test_audit_test_safety.py`, use `pytester` with a temporary `_gui.py` module to prove default non-import and deliberate `--include-quarantined -m gui` collection.

Run: `uv run pytest -q`

Expected: PASS without experiment data, home-directory writes, Python-socket network access, directly declared external-process or hardware probes, real GUI, hour-scale runs, or million-element resource probes. The verifier reports these concrete controls rather than claiming an operating-system network sandbox.

- [ ] **Step 6: Commit the safety boundary**

```powershell
git add pyproject.toml tests/conftest.py tests/test_audit_test_safety.py tools/test_safety.py
git commit -m "test: quarantine research and unsafe pytest paths"
```

---

### Task 3: Add Safe Default CI and Local-Service Boundaries

**Files:**
- Create: `.github/workflows/ci.yml`
- Create: `tests/test_repository_hygiene.py`
- Modify: `docker-compose.yml`
- Modify: `db/README.md`

**Interfaces:**
- Consumes: the safe default pytest policy from Task 2.
- Produces: a lockfile-based safe-default CI recipe and loopback-only host ports; it does not claim a hermetic runner or enable GitHub branch protection.

- [ ] **Step 1: Write failing repository-hygiene tests**

```python
# tests/test_repository_hygiene.py
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_compose_ports_are_loopback_only():
    compose = read("docker-compose.yml")
    assert '"127.0.0.1:5433:5432"' in compose
    assert '"127.0.0.1:8502:8501"' in compose
    assert '\n      - "5433:5432"' not in compose
    assert '\n      - "8502:8501"' not in compose


def test_ci_uses_only_the_safe_default_suite():
    workflow = read(".github/workflows/ci.yml")
    assert "uv sync --frozen --extra dev" in workflow
    assert "uv run python tools/test_safety.py" in workflow
    assert "uv run pytest" in workflow
    assert "uv build" in workflow
    assert "git diff --check" in workflow
    assert "docker compose up" not in workflow
    assert "vibrasim2-p0 run" not in workflow
```

- [ ] **Step 2: Run the focused test and verify it fails**

Run: `uv run pytest -o addopts="-v --strict-markers" tests/test_repository_hygiene.py -q`

Expected: FAIL because the workflow does not exist and the ports are not loopback-bound.

- [ ] **Step 3: Bind both host-facing development services to loopback**

Change only the host bindings in `docker-compose.yml`:

```yaml
ports:
  - "127.0.0.1:5433:5432"
```

and:

```yaml
ports:
  - "127.0.0.1:8502:8501"
```

Document in `db/README.md` that PostgreSQL and the dashboard are intentionally reachable only from the local host. Do not change the container-internal Streamlit bind address.

- [ ] **Step 4: Add a lockfile-based minimal two-platform workflow**

Create this workflow and retain the committed `uv.lock` as the dependency authority:

```yaml
name: safe-default

on:
  push:
  pull_request:

jobs:
  test:
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, windows-latest]
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v6
        with:
          python-version: "3.13"
          enable-cache: true
      - run: uv sync --frozen --extra dev
      - run: uv run python tools/test_safety.py
      - run: uv run pytest
      - run: uv build
      - run: git diff --check
```

Record in the implementation review that the action versions are conventional major tags, not locally executable proof, and verify the supported current majors against their official repositories before implementation. The workflow becomes confirmed for this repository only after an authorized push runs GitHub Actions. Do not call it hermetic: action tags and runner images remain moving external inputs.

- [ ] **Step 5: Verify locally without starting services**

Run: `uv run pytest -o addopts="-v --strict-markers" tests/test_repository_hygiene.py -q`

Expected: PASS.

Run: `docker compose config --quiet`

Expected: exit 0; do not run `docker compose up`.

Run: `uv build`

Expected: source distribution and wheel created successfully under `dist/`.

Run: `git diff --check`

Expected: exit 0.

- [ ] **Step 6: Commit CI and host-boundary changes**

```powershell
git add .github/workflows/ci.yml docker-compose.yml db/README.md tests/test_repository_hygiene.py
git commit -m "ci: add safe default workflow and local bindings"
```

---

### Task 4: Add Immutable P0 Types and Registered Fixtures

**Files:**
- Create: `docs/vibrasim2/P0_BUDGET_LEDGER.json`
- Create: `vibrasim2/p0/__init__.py`
- Create: `vibrasim2/p0/budget.py`
- Create: `vibrasim2/p0/types.py`
- Create: `vibrasim2/p0/fixtures.py`
- Create: `tests/vibrasim2/test_p0_budget.py`
- Create: `tests/vibrasim2/test_p0_types.py`
- Create: `tests/vibrasim2/test_p0_fixtures.py`

**Interfaces:**
- Consumes: the frozen P0 constants, topology definitions, and 19,800-second hard ceiling.
- Produces: `BudgetError`, `BudgetLedger`, `BudgetLease`, `load_budget_ledger`, `assert_budget_allows_run`, `start_budget_interval`, `finish_budget_interval`, `P0Config`, `RunCell`, `P0State`, `P0StateSnapshot`, `Topology`, `ChannelMode`, `RunPurpose`, `Verdict`, and deterministic fixture constructors used by all P0 and viewer tasks.

- [ ] **Step 1: Start the registered budget ledger and write failing immutable-type and fixture tests**

Immediately before the first edit in this step, record the wall-clock start in
`docs/vibrasim2/P0_BUDGET_LEDGER.json`. The first Task 4–8 interval, including
red/green tests and corrections, is the registered implementation-and-test
budget. Use schema version `1`, registration SHA-256
`28992a8b131100ed4eb2cd9147ddea7b3251921777211a63bb4b64e5524ca9e1`,
`hard_ceiling_seconds=19800`, `status="active"`,
`cumulative_elapsed_seconds=0`, `scientific_core_sha256=null`, and a
`budgeted_paths` array containing exactly these production files:
`vibrasim2/p0/__init__.py`, `vibrasim2/p0/budget.py`,
`vibrasim2/p0/types.py`, `vibrasim2/p0/fixtures.py`,
`vibrasim2/p0/dynamics.py`, `vibrasim2/p0/energy.py`,
`vibrasim2/p0/artifacts.py`, `vibrasim2/p0/verdict.py`,
`vibrasim2/p0/runner.py`, and `vibrasim2/p0/cli.py`; plus the
nine same-purpose files `tests/vibrasim2/test_p0_budget.py`,
`test_p0_types.py`, `test_p0_fixtures.py`, `test_p0_dynamics.py`,
`test_p0_energy.py`, `test_p0_artifacts.py`, `test_p0_verdict.py`,
`test_p0_runner.py`, and `test_p0_cli.py`. Store every entry as its full
repository-relative path, sorted lexically. Add one interval with the actual RFC3339 UTC
`started_at_utc`, `ended_at_utc=null`, `elapsed_seconds=null`,
`phase="implementation"`, `owner="work/vibrasim2-research-reset"`, and
`outcome=null`. Record
the timestamp before editing any P0 source or test. Do not backdate or remove
an interval.

In `test_p0_budget.py`, use temporary ledgers to prove that
`assert_budget_allows_run` accepts only a schema-valid ledger with the exact
registration identity, no open interval, `status="within_cap"`, integer interval
durations equal to the ceiling-rounded UTC differences, a cumulative value equal
to their sum, cumulative duration strictly below `19800`, and at least the
registered 2,700-second run-plus-review reserve remaining. Add named rejection
tests for `active`, exactly `19800`, `phase_reserve_breached`, `overrun_registration_required`, wrong
registration identity, backward timestamps, inconsistent arithmetic, a stale
sibling lock, fewer than `2700` seconds remaining, an aborted implementation
correction, a changed budgeted file, and a mismatched path inventory. The
production helper accepts the ledger path explicitly so unit tests never read or
modify the repository ledger.

Add atomic lease tests with temporary ledgers: `start_budget_interval` must,
under a sibling exclusive lock, revalidate a closed within-cap ledger and append
one open interval with exact `phase`, `owner`, and start time; a concurrent or
second open must fail. `finish_budget_interval` must require the same lease owner,
close only the last interval, ceiling-round its elapsed seconds, recompute the
cumulative sum, record `outcome` as `completed` or `aborted`, and set
`within_cap`, `phase_reserve_breached`, or
`overrun_registration_required` by the exact rules below. An
abandoned open interval or stale lock blocks another start pending explicit
manual audit; no recovery path invents an end time.

```python
# tests/vibrasim2/test_p0_fixtures.py
from dataclasses import replace

import numpy as np

from vibrasim2.p0.fixtures import (
    coupling_sites,
    edges_for,
    initial_state,
    omega_upper,
    reproduction_cells,
    registered_stage_a_cells,
)
from vibrasim2.p0.types import ChannelMode, P0Config, RunCell, RunPurpose, Topology


def test_registered_sites_and_edges_are_exact():
    np.testing.assert_array_equal(
        coupling_sites(),
        np.array(((13, 16), (14, 13), (18, 13), (19, 16), (18, 19), (14, 19))),
    )
    np.testing.assert_array_equal(
        edges_for(Topology.CYCLE),
        np.array(((0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 0))),
    )
    np.testing.assert_array_equal(
        edges_for(Topology.BRANCH),
        np.array(((0, 1), (1, 2), (2, 0), (2, 3), (3, 4), (4, 5))),
    )


def test_stage_a_matrix_contains_only_registered_cells():
    config = P0Config.registered()
    cells = registered_stage_a_cells(config)
    expected = []
    for source in config.source_centres:
        expected.extend(
            (
                RunCell(Topology.CYCLE, ChannelMode.FULL, RunPurpose.PRIMARY, source, 0.05, 2000),
                RunCell(Topology.BRANCH, ChannelMode.FULL, RunPurpose.PRIMARY, source, 0.05, 2000),
                RunCell(Topology.CYCLE, ChannelMode.NO_BONDS, RunPurpose.PRIMARY, source, 0.05, 2000),
                RunCell(Topology.CYCLE, ChannelMode.DECOUPLED, RunPurpose.PRIMARY, source, 0.05, 2000),
                RunCell(Topology.CYCLE, ChannelMode.BROKEN_PAIR, RunPurpose.SENSITIVITY, source, 0.05, 2000),
                RunCell(Topology.BRANCH, ChannelMode.BROKEN_PAIR, RunPurpose.SENSITIVITY, source, 0.05, 2000),
                RunCell(Topology.CYCLE, ChannelMode.FULL, RunPurpose.CONVERGENCE, source, 0.025, 4000),
                RunCell(Topology.BRANCH, ChannelMode.FULL, RunPurpose.CONVERGENCE, source, 0.025, 4000),
            )
        )
    assert cells == tuple(expected)


def test_reproduction_matrix_is_exact():
    config = P0Config.registered()
    assert reproduction_cells(config) == tuple(
        RunCell(topology, ChannelMode.FULL, RunPurpose.REPRODUCTION, source, 0.05, 2000)
        for source in config.source_centres
        for topology in (Topology.CYCLE, Topology.BRANCH)
    )


def test_initial_state_is_deterministic_mean_zero_and_read_only():
    config = P0Config.registered()
    first = initial_state(config, (4, 16))
    second = initial_state(config, (4, 16))
    np.testing.assert_array_equal(first.u, second.u)
    assert abs(float(first.u.mean())) < 1e-15
    assert first.u.dtype == np.float64
    assert not first.u.flags.writeable
    with np.testing.assert_raises(ValueError):
        first.u[0, 0] = 3.0


def test_registered_stability_bound_holds_and_invalid_config_is_rejected():
    config = P0Config.registered()
    assert config.dt * omega_upper(config, Topology.BRANCH) < 0.25
    with np.testing.assert_raises_regex(ValueError, "registered P0 configuration"):
        replace(config, g=1.1).assert_registered()
```

In `test_p0_types.py`, implement `test_registered_state_shapes_are_exact`, `test_state_defensively_copies_and_freezes_all_arrays`, `test_registered_config_rejects_source_override`, `test_slug_contains_no_seed_dimension`, `test_arm_labels_are_unambiguous`, and `test_state_preserves_nonfinite_values_for_verdict`. Their assertions are respectively `(32,32)/(32,32)/(6,)/(6,)`, caller mutation isolation plus `writeable=False`, `replace(P0Config.registered(), source_centres=((5,5),)).assert_registered()` raising, absence of `seed` in the slug and dataclass fields, exact arm labels `cycle`, `branch`, `no_bonds`, `decoupled`, `cycle:broken_pair`, and `branch:broken_pair`, and preservation of one deliberate NaN for the registered `FAIL` gate.

- [ ] **Step 2: Run the focused tests and verify import failure**

Run: `uv run pytest -o addopts="-v --strict-markers" tests/vibrasim2/test_p0_budget.py tests/vibrasim2/test_p0_types.py tests/vibrasim2/test_p0_fixtures.py -q`

Expected: FAIL because `vibrasim2.p0` does not exist.

- [ ] **Step 3: Define the exact domain types**

Use these public declarations in `types.py`:

```python
class Topology(str, Enum):
    CYCLE = "cycle"
    BRANCH = "branch"


class ChannelMode(str, Enum):
    FULL = "full"
    NO_BONDS = "no_bonds"
    DECOUPLED = "decoupled"
    BROKEN_PAIR = "broken_pair"


class RunPurpose(str, Enum):
    PRIMARY = "primary"
    CONVERGENCE = "convergence"
    SENSITIVITY = "sensitivity"
    REPRODUCTION = "reproduction"


class Verdict(str, Enum):
    PASS = "PASS"
    NULL = "NULL"
    INCONCLUSIVE = "INCONCLUSIVE"
    FAIL = "FAIL"


@dataclass(frozen=True)
class P0Config:
    grid_shape: tuple[int, int]
    c: float
    k_b: float
    g: float
    dt: float
    sigma: float
    steps: int
    frame_stride: int
    source_centres: tuple[tuple[int, int], ...]

    @classmethod
    def registered(cls) -> "P0Config":
        return cls(
            grid_shape=(32, 32), c=1.0, k_b=0.5, g=1.0,
            dt=0.05, sigma=2.0, steps=2000, frame_stride=10,
            source_centres=((4, 16), (16, 4), (4, 4)),
        )

    def assert_registered(self) -> None:
        if self != type(self).registered():
            raise ValueError("registered P0 configuration is immutable")


@dataclass(frozen=True)
class RunCell:
    topology: Topology
    mode: ChannelMode
    purpose: RunPurpose
    source_centre: tuple[int, int]
    dt: float
    steps: int

    @property
    def slug(self) -> str:
        x, y = self.source_centre
        return f"{self.purpose.value}-{self.mode.value}-{self.topology.value}-x{x}-y{y}-dt{self.dt:g}"

    @property
    def arm_label(self) -> str:
        if self.mode is ChannelMode.FULL:
            return self.topology.value
        if self.mode is ChannelMode.BROKEN_PAIR:
            return f"{self.topology.value}:broken_pair"
        return self.mode.value


@dataclass(frozen=True)
class P0State:
    u: NDArray[np.float64]
    p: NDArray[np.float64]
    q: NDArray[np.float64]
    r: NDArray[np.float64]


@dataclass(frozen=True)
class P0StateSnapshot:
    tick: int
    simulation_time: float
    state: P0State
```

`P0State.__post_init__` must coerce to `np.float64`, require matching two-dimensional `u/p` shapes and matching one-dimensional `q/r` shapes, reject empty arrays, copy every array, and call `setflags(write=False)` before assignment with `object.__setattr__`. It deliberately preserves NaN/Inf values: non-finiteness is a registered scientific `FAIL` input, not an artifact-schema error. Registered-run shape validation separately requires `(32,32)` field arrays and six matter values; this separation permits tiny unit fixtures without weakening the registered CLI.

In `budget.py`, define immutable `BudgetInterval` and `BudgetLedger` values plus
`BudgetLease` and the public functions named above. Parse timestamps as timezone-aware UTC and
round every closed interval upward to the next whole second before comparison;
the stored integer must match that value exactly. Schema validation rejects
unknown or missing keys, booleans masquerading as integers, more than one open
interval, overlapping intervals, non-monotonic ordering, and inconsistent sums.
`assert_budget_allows_run` additionally rejects any open interval, any status
other than `within_cap`, and any cumulative value greater than or equal to the
ceiling. For a scientific-run start it also requires at least `2700` seconds
remaining: the frozen registration's expected maximum of 15 minutes for the run
plus 30 minutes for verdict review. It returns no advisory Boolean and raises a domain error on every
invalid or non-runnable state.

Require `hard_ceiling_seconds == 19800`, the exact registration hash, the exact
budgeted-path inventory, and at least one interval. The first interval is always
`phase="implementation"` with owner `work/vibrasim2-research-reset`; later phase
values are only `implementation_correction`, `scientific_run`, or `review`.
An open interval has both end and outcome null; a closed interval has a UTC end,
integer elapsed seconds, and outcome `completed` or `aborted`. Status is
`active` if and only if the last interval is open, is `within_cap` only for a
closed ledger below the fixed cap with the next registered phase reserve intact,
and is `overrun_registration_required` only for a closed ledger at or above it.
A closed interval with outcome `aborted` is never runnable and has
`status="phase_reserve_breached"` pending an explicit audit and new recorded
decision. A closed implementation interval that leaves fewer than 2,700 seconds, or any
closed `scientific_run` that took at least 900 seconds or leaves fewer than 1,801
seconds below the cap, instead has
`status="phase_reserve_breached"`; this is an operational budget stop, not a
scientific verdict. A closed review longer than 1,800 seconds has the same
phase-reserve status even when total time remains below the hard cap. For a runnable ledger, the initial
implementation interval must be closed with outcome `completed`.

Phase order is part of schema validity: zero or more completed
`implementation_correction` intervals may follow implementation only before
data; at most one `scientific_run` may follow them; and at most one `review` may
follow a completed scientific run. A scientific-run interval with outcome
`aborted` blocks retry pending an explicit audit and new recorded decision, as
does an aborted `implementation_correction`; neither state may validate as
`within_cap` merely because total elapsed time remains below the ceiling.
`assert_budget_allows_run` requires the pre-run phase state with no prior
scientific-run interval, while a review lease requires exactly one completed
scientific run and no prior review.

The low-level parser may load `active` and overrun ledgers for diagnostics;
`assert_budget_allows_run` is the stricter pre-start gate. Atomic updates write a
sibling temporary file, flush and fsync, replace, read back, and release the
exclusive lock in `finally`. `start_budget_interval` accepts only phases
`implementation_correction`, `scientific_run`, and `review` after the initial implementation interval; its
caller supplies an immutable owner ID. It performs the same gate while holding
the lock, so the check cannot race another process. `finish_budget_interval`
accepts only the returned lease, an actual UTC end time, and exact outcome
`completed` or `aborted`; it never edits an earlier interval.

`start_budget_interval` repeats the 2,700-second reserve check atomically for
`scientific_run`; `review` requires at least 1,801 seconds remaining, and
`implementation_correction` requires only positive remaining budget. These are
operational phase reservations derived from the frozen budget paragraph, not
scientific verdict thresholds. An atomic fixed-cell run is not killed midway to
manufacture a cleaner time record: if actual elapsed time consumes the reserve
or crosses the cap, closure records the real duration, sets
`phase_reserve_breached` or `overrun_registration_required` as applicable, and
returns the post-run budget stop described in Task 8.

For a closed implementation ledger, `scientific_core_sha256` is the SHA-256 of
the exact sorted `budgeted_paths` inventory, feeding for each file its UTF-8 path,
a NUL byte, its canonical-LF byte length, another NUL, and its canonical-LF
bytes. Missing, extra, reordered, duplicate, or changed entries fail validation.
`assert_budget_allows_run(ledger_path, expected_registration_sha256,
repository_root)` also refuses an existing sibling `.lock` before it checks the
closed status and recomputes this digest. `start_budget_interval` acquires that
same lock first and invokes an internal equivalent that recognizes its own lock,
so there is no check/start race. `finish_budget_interval` updates the core digest
only when closing `implementation_correction`; scientific-run and review leases
require it to remain unchanged.

- [ ] **Step 4: Implement only the registered fixtures**

In `fixtures.py`, expose these signatures:

```text
def coupling_sites() -> NDArray[np.int64]
def edges_for(topology: Topology) -> NDArray[np.int64]
def initial_state(config: P0Config, source_centre: tuple[int, int]) -> P0State
def registered_stage_a_cells(config: P0Config) -> tuple[RunCell, ...]
def reproduction_cells(config: P0Config) -> tuple[RunCell, ...]
def omega_upper(config: P0Config, topology: Topology) -> float
```

`initial_state` computes periodic squared distance in each dimension, forms `exp(-d²/(2*sigma²))`, subtracts its spatial mean, and scales the array by `a = sqrt(1.0 / unscaled_total_energy)`. For this all-zero matter state, `unscaled_total_energy` is the field-gradient energy plus the full coupling energy at the six registered sites. Reuse the returned `u` unchanged across CYCLE, BRANCH, and control cells for the same source centre.

`registered_stage_a_cells` returns, in source-centre order, primary FULL CYCLE and BRANCH, primary NO_BONDS with the canonical-but-dynamically-ignored CYCLE label, primary DECOUPLED with CYCLE bonds present but unexcited, SENSITIVITY BROKEN_PAIR for CYCLE and BRANCH, and CONVERGENCE FULL CYCLE and BRANCH. The convergence cells use `dt=0.025`, `steps=4000`; every other cell uses `dt=0.05`, `steps=2000`. `reproduction_cells` returns exactly six FULL cells, ordered by source then CYCLE/BRANCH, with `purpose=REPRODUCTION`, `dt=0.05`, and `steps=2000`. No `Topology | None` state or implicit topology fallback exists.

`omega_upper` computes `sqrt(8*c*c + 2*g + 2*k_b*d_max)` where `d_max` comes from the supplied edge array.

- [ ] **Step 5: Run fixture tests and confirm isolation from Vibrasim I**

Run: `uv run pytest -o addopts="-v --strict-markers" tests/vibrasim2/test_p0_budget.py tests/vibrasim2/test_p0_types.py tests/vibrasim2/test_p0_fixtures.py -q`

Expected: PASS.

Run: `rg -n "from world|import world" vibrasim2/p0`

Expected: no matches.

- [ ] **Step 6: Commit the P0 domain contract**

```powershell
git add docs/vibrasim2/P0_BUDGET_LEDGER.json vibrasim2/p0/__init__.py vibrasim2/p0/budget.py vibrasim2/p0/types.py vibrasim2/p0/fixtures.py tests/vibrasim2/test_p0_budget.py tests/vibrasim2/test_p0_types.py tests/vibrasim2/test_p0_fixtures.py
git commit -m "feat(v2-p0): add registered types and fixtures"
```

---

### Task 5: Implement Hamiltonian Dynamics and the Energy Ledger

**Files:**
- Create: `vibrasim2/p0/dynamics.py`
- Create: `vibrasim2/p0/energy.py`
- Create: `tests/vibrasim2/test_p0_dynamics.py`
- Create: `tests/vibrasim2/test_p0_energy.py`

**Interfaces:**
- Consumes: `P0Config`, `P0State`, `RunCell`, sites, and supplied edges from Task 4.
- Produces: `Forces`, `EnergyRecord`, `Trajectory`, `forces`, `velocity_verlet_step`, `energy_record`, `run_trajectory`, and registered trace metrics.

- [ ] **Step 1: Write failing force, integration, and energy tests**

```python
# tests/vibrasim2/test_p0_dynamics.py
import numpy as np

from vibrasim2.p0.dynamics import forces, periodic_laplacian, velocity_verlet_step
from vibrasim2.p0.fixtures import initial_state
from vibrasim2.p0.types import ChannelMode, P0Config, P0State, RunCell, RunPurpose, Topology


def test_periodic_laplacian_wraps_both_axes():
    u = np.zeros((4, 4), dtype=np.float64)
    u[0, 0] = 1.0
    expected = np.zeros((4, 4), dtype=np.float64)
    expected[0, 0] = -4.0
    expected[1, 0] = expected[3, 0] = 1.0
    expected[0, 1] = expected[0, 3] = 1.0
    np.testing.assert_array_equal(periodic_laplacian(u), expected)


def test_zero_state_is_a_fixed_point():
    config = P0Config.registered()
    zero = P0State(
        np.zeros((32, 32)), np.zeros((32, 32)), np.zeros(6), np.zeros(6)
    )
    cell = RunCell(Topology.CYCLE, ChannelMode.FULL, RunPurpose.PRIMARY, (4, 16), 0.05, 2000)
    stepped = velocity_verlet_step(zero, cell, config)
    np.testing.assert_array_equal(stepped.u, zero.u)
    np.testing.assert_array_equal(stepped.q, zero.q)


def test_broken_pair_omits_only_the_field_reaction():
    config = P0Config.registered()
    state = initial_state(config, (4, 16))
    full = RunCell(Topology.CYCLE, ChannelMode.FULL, RunPurpose.PRIMARY, (4, 16), 0.05, 2000)
    broken = RunCell(Topology.CYCLE, ChannelMode.BROKEN_PAIR, RunPurpose.SENSITIVITY, (4, 16), 0.05, 2000)
    full_force = forces(state, full, config)
    broken_force = forces(state, broken, config)
    np.testing.assert_array_equal(full_force.matter, broken_force.matter)
    assert not np.array_equal(full_force.field, broken_force.field)
```

Implement `test_field_force_matches_finite_difference_h_f_and_h_c` and `test_matter_force_matches_finite_difference_h_m_and_h_c`: perturb one fixed coordinate by `epsilon=1e-7` and assert `force == -dH/dx` with `rtol=1e-6`, `atol=1e-8`. Implement `test_decoupled_matter_energy_stays_zero`, `test_cycle_and_branch_initial_totals_are_one`, `test_record_and_snapshot_ticks_are_exact`, and `test_coupling_integral_uses_trapezoidal_endpoints`; the expected values are respectively exact zero, `abs(H0-1) <= 1e-12`, records `0..20` plus snapshots `(0,10,20)`, and `0.5*dt*(power_0+power_1)` for the first interval.

- [ ] **Step 2: Run the focused tests and verify missing modules**

Run: `uv run pytest -o addopts="-v --strict-markers" tests/vibrasim2/test_p0_dynamics.py tests/vibrasim2/test_p0_energy.py -q`

Expected: FAIL because `dynamics.py` and `energy.py` do not exist.

- [ ] **Step 3: Implement the exact force equations and velocity Verlet**

Use this force structure in `dynamics.py`:

```python
def periodic_laplacian(u: NDArray[np.float64]) -> NDArray[np.float64]:
    return (
        np.roll(u, 1, axis=0) + np.roll(u, -1, axis=0)
        + np.roll(u, 1, axis=1) + np.roll(u, -1, axis=1)
        - 4.0 * u
    )


@dataclass(frozen=True)
class Forces:
    field: NDArray[np.float64]
    matter: NDArray[np.float64]


def forces(state: P0State, cell: RunCell, config: P0Config) -> Forces:
    sites = coupling_sites()
    field = config.c**2 * periodic_laplacian(state.u)
    matter = np.zeros(6, dtype=np.float64)
    if cell.mode is not ChannelMode.NO_BONDS:
        for left, right in edges_for(cell.topology):
            delta = state.q[left] - state.q[right]
            matter[left] -= config.k_b * delta
            matter[right] += config.k_b * delta
    coupling_g = 0.0 if cell.mode is ChannelMode.DECOUPLED else config.g
    mismatch = state.u[sites[:, 0], sites[:, 1]] - state.q
    matter += coupling_g * mismatch
    if cell.mode is not ChannelMode.BROKEN_PAIR:
        np.add.at(field, (sites[:, 0], sites[:, 1]), -coupling_g * mismatch)
    return Forces(field=field, matter=matter)
```

`velocity_verlet_step` performs half momentum, full position, force recomputation, half momentum. It uses `cell.dt`, creates a new validated `P0State`, and mutates no input.

- [ ] **Step 4: Implement exact energies, powers, traces, and registered metrics**

Define:

```python
@dataclass(frozen=True)
class EnergyRecord:
    tick: int
    simulation_time: float
    h_field: float | None
    h_matter: float | None
    h_coupling: float | None
    h_total: float | None
    p_field_from_coupling: float | None
    p_matter_from_coupling: float | None
    integral_field_power: float | None
    integral_matter_power: float | None
    finite: bool


@dataclass(frozen=True)
class Trajectory:
    cell: RunCell
    records: tuple[EnergyRecord, ...]
    snapshots: tuple[P0StateSnapshot, ...]
```

Compute `H_f` using kinetic energy plus horizontal and vertical periodic differences counted once with `np.roll(u, -1, axis=0/1)`. Compute `H_m` once per supplied edge, or with `k_b=0` for NO_BONDS. Compute `H_c` with effective `g=0` only for DECOUPLED. Coupling powers are the two registered signed force-power products. Initialize both integrals to zero at tick 0; every later finite record adds `0.5*dt*(previous_power+current_power)`. If a state or derived scalar is non-finite, set `finite=False`, encode the affected JSON scalar fields as `null`, persist the raw NPZ state, stop that cell after the failure record, and allow verdict construction to set `all_values_finite=False`.

`run_trajectory(cell, config, initial)` stores energy at tick 0 and every full step, snapshots at tick 0 and every `frame_stride` ticks, and returns only after exactly `cell.steps` steps. Expose pure functions `max_relative_energy_drift`, `coupling_identity_residual`, `max_material_energy_ratio`, and `a_b`; `a_b` excludes tick 0 and uses ticks 1 through 2000 for primary cells.

- [ ] **Step 5: Run numerical unit tests without running P0**

Run: `uv run pytest -o addopts="-v --strict-markers" tests/vibrasim2/test_p0_dynamics.py tests/vibrasim2/test_p0_energy.py -q`

Expected: PASS using only tiny deterministic test trajectories.

Run: `rg -n "random|rng|seed|from world|import world" vibrasim2/p0`

Expected: no implementation matches other than an assertion message explicitly saying P0 has no seed.

- [ ] **Step 6: Commit the mechanics**

```powershell
git add vibrasim2/p0/dynamics.py vibrasim2/p0/energy.py tests/vibrasim2/test_p0_dynamics.py tests/vibrasim2/test_p0_energy.py
git commit -m "feat(v2-p0): implement Hamiltonian dynamics and ledger"
```

---

### Task 6: Persist Append-Only Scientific Artifacts

**Files:**
- Create: `vibrasim2/p0/artifacts.py`
- Create: `tests/vibrasim2/test_p0_artifacts.py`

**Interfaces:**
- Consumes: `RunCell`, `EnergyRecord`, `P0StateSnapshot`, and `Trajectory`.
- Produces: `CellJournal`, `write_run_manifest`, `iter_energy_records`, `iter_snapshots`, `atomic_write_json`, `read_json`, and `scientific_digest`.

- [ ] **Step 1: Write failing round-trip, ordering, and failure tests**

```python
# tests/vibrasim2/test_p0_artifacts.py
import json

import numpy as np
import pytest

from vibrasim2.p0.artifacts import (
    ArtifactError,
    CellJournal,
    atomic_write_json,
    iter_snapshots,
    read_json,
    scientific_digest,
)
from vibrasim2.p0.energy import EnergyRecord
from vibrasim2.p0.types import ChannelMode, P0Config, P0State, P0StateSnapshot, RunCell, RunPurpose, Topology


def tiny_config() -> P0Config:
    return P0Config((2, 2), 1.0, 0.5, 1.0, 0.05, 2.0, 20, 10, ((0, 0),))


def make_snapshot(tick: int) -> P0StateSnapshot:
    state = P0State(
        np.arange(4, dtype=np.float64).reshape(2, 2),
        np.zeros((2, 2), dtype=np.float64),
        np.array((0.25,), dtype=np.float64),
        np.zeros(1, dtype=np.float64),
    )
    return P0StateSnapshot(tick=tick, simulation_time=tick * 0.05, state=state)


def make_journal(path) -> CellJournal:
    cell = RunCell(Topology.CYCLE, ChannelMode.FULL, RunPurpose.PRIMARY, (0, 0), 0.05, 20)
    return CellJournal(
        path,
        stage="A",
        cell=cell,
        config=tiny_config(),
        coupling_sites=np.array(((0, 0),), dtype=np.int64),
        supplied_edges=np.empty((0, 2), dtype=np.int64),
    )


def build_minimal_scientific_tree(root) -> None:
    atomic_write_json(
        root / "run.json",
        {
            "schema_version": 1,
            "run_id": "digest-fixture",
            "preregistration_sha256": "fixture",
            "addendum_sha256": "fixture",
            "observation_schema_version": 1,
            "display_scale": 4.0,
        },
    )
    journal = make_journal(root / "primary-full-cycle-x0-y0-dt0.05")
    journal.append_energy(
        EnergyRecord(0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, True)
    )
    journal.append_snapshot(make_snapshot(tick=0))


def test_snapshot_file_precedes_manifest_entry(tmp_path):
    journal = make_journal(tmp_path / "cell")
    snapshot = make_snapshot(tick=10)
    journal.append_snapshot(snapshot)
    entry = json.loads((tmp_path / "cell/snapshots/manifest.jsonl").read_text().splitlines()[0])
    assert (tmp_path / "cell/snapshots" / entry["file"]).is_file()
    loaded = tuple(iter_snapshots(tmp_path / "cell"))
    np.testing.assert_array_equal(loaded[0].state.u, snapshot.state.u)


def test_snapshot_journal_rejects_duplicate_or_decreasing_ticks(tmp_path):
    journal = make_journal(tmp_path / "cell")
    journal.append_snapshot(make_snapshot(tick=10))
    with pytest.raises(ArtifactError, match="strictly increasing"):
        journal.append_snapshot(make_snapshot(tick=10))


def test_atomic_result_must_survive_readback(tmp_path, monkeypatch):
    target = tmp_path / "result.json"
    atomic_write_json(target, {"verdict": "NULL"})
    assert read_json(target) == {"verdict": "NULL"}
    monkeypatch.setattr("vibrasim2.p0.artifacts.os.replace", lambda left, right: None)
    with pytest.raises(ArtifactError):
        atomic_write_json(target, {"verdict": "PASS"})


def test_digest_ignores_view_events_and_wallclock(tmp_path):
    build_minimal_scientific_tree(tmp_path)
    first = scientific_digest(tmp_path)
    (tmp_path / "view-events.jsonl").write_text('{"dropped": 9, "wallclock": 22}\n')
    assert scientific_digest(tmp_path) == first
```

The helpers above are the complete tiny fixture; do not import a real P0 runner.

- [ ] **Step 2: Run the artifact tests and verify import failure**

Run: `uv run pytest -o addopts="-v --strict-markers" tests/vibrasim2/test_p0_artifacts.py -q`

Expected: FAIL because `artifacts.py` does not exist.

- [ ] **Step 3: Implement durable ordering and explicit schemas**

At the run root, `write_run_manifest` atomically writes `run.json` before any cell record. It stores `schema_version`, `run_id`, both frozen document digests and Git blob IDs, the closed budget ledger's exact `scientific_core_sha256`, the complete P0 configuration, the exact ordered `RunCell.slug` list, observation schema version `1`, and fixed `display_scale=4.0`. Headless runs write the same observation metadata so observer mode cannot change scientific identity. The manifest writer receives the verified core digest captured by the scientific-run lease; it never recomputes it after the lease starts.

`CellJournal(cell_dir, *, stage, cell, config, coupling_sites, supplied_edges)` creates `<cell>/cell.json`, `<cell>/energy.jsonl`, `<cell>/snapshots/manifest.jsonl`, and `<cell>/snapshots/snapshot-<tick:010d>.npz`. `stage` accepts only `"A"` or `"B"`. The atomic `cell.json` stores the complete `RunCell` and `P0Config`, stage, topology, mode, purpose, source centre, explicit coupling-site array, and supplied-edge array needed for independent replay. `append_energy` requires contiguous ticks. `append_snapshot` requires strictly increasing ticks, writes a temporary NPZ through an already-open binary file handle in the snapshot directory, flushes and fsyncs the file, replaces the final file atomically, then appends and flushes the manifest line. Snapshot-manifest keys are exactly `schema_version`, `tick`, `simulation_time`, and `file`.

Use schema version `1`. JSON is UTF-8, sorted-key, compact, one-record-per-line and uses `null` plus `finite=false` for registered numerical non-finiteness. NPZ keys are exactly `u`, `p`, `q`, and `r`; readers obtain the expected field and matter shapes from `cell.json`, reject missing keys, wrong dtype, wrong shape, or a manifest/file mismatch, but preserve NaN/Inf arrays so the ordered verdict can classify them as `FAIL`. Production construction additionally asserts the registered `(32,32)` and `(6,)` shapes; tiny journals remain valid only against their own explicit tiny manifest.

`atomic_write_json` writes into a sibling temporary file, flushes and fsyncs it, calls `os.replace`, immediately reads the target, and raises `ArtifactError` if the readback differs from the supplied JSON value. It must not leave a scientific verdict after failed readback.

`scientific_digest` hashes canonical decoded scientific values in sorted cell/tick order: frozen document identities, the manifest's `scientific_core_sha256`, registered configuration, cell mechanics metadata, float64 shapes and C-order bytes, and energy-record JSON. It excludes `run_id`, output path, observation schema/display scale, `result.json`, `view-events.jsonl`, process IDs, wallclock values, frame-drop counters, and GUI state. This both avoids a digest/result self-reference and makes separate headless/observed directories comparable. Add a test proving that otherwise identical trees with different manifest core digests produce different scientific digests.

- [ ] **Step 4: Run artifact tests and inspect their filesystem scope**

Run: `uv run pytest -o addopts="-v --strict-markers" tests/vibrasim2/test_p0_artifacts.py -q`

Expected: PASS.

Run: `git status --short archive/run-logs`

Expected: no output.

- [ ] **Step 5: Commit the artifact boundary**

```powershell
git add vibrasim2/p0/artifacts.py tests/vibrasim2/test_p0_artifacts.py
git commit -m "feat(v2-p0): add append-only scientific artifacts"
```

---

### Task 7: Implement Registered Gates and the Pure Ordered Verdict

**Files:**
- Create: `vibrasim2/p0/verdict.py`
- Create: `tests/vibrasim2/test_p0_verdict.py`

**Interfaces:**
- Consumes: reloaded trajectories and configuration manifests; accepts no caller-supplied thresholds.
- Produces: `CellMetrics`, `P0Evidence`, `StageAGate`, `validate_registered_artifacts`, `build_evidence`, `evaluate_stage_a`, and `decide_verdict`.

- [ ] **Step 1: Write the table-driven precedence tests**

```python
# tests/vibrasim2/test_p0_verdict.py
from dataclasses import replace

import numpy as np
import pytest

from vibrasim2.p0.types import Verdict
from vibrasim2.p0.verdict import REGISTERED_PREDICATES, P0Evidence, decide_verdict


def passing_evidence() -> P0Evidence:
    return P0Evidence(
        configuration_matches=True,
        all_values_finite=True,
        initial_energy_matches=True,
        stability_bound_holds=True,
        valid_arm_energy_gates_hold=True,
        valid_arm_identity_gates_hold=True,
        exercised_channel_holds=True,
        timestep_convergence_holds=True,
        broken_pair_sensitivity_holds=True,
        topology_difference_holds=True,
        topology_sign_holds=True,
        decoupled_zero_holds=True,
        deterministic_rerun_holds=True,
    )


@pytest.mark.parametrize(
    "field",
    ("configuration_matches", "all_values_finite", "initial_energy_matches", "stability_bound_holds"),
)
def test_fail_precedes_every_other_outcome(field):
    assert decide_verdict(replace(passing_evidence(), **{field: False})) is Verdict.FAIL


@pytest.mark.parametrize(
    "field",
    (
        "valid_arm_energy_gates_hold",
        "valid_arm_identity_gates_hold",
        "exercised_channel_holds",
        "timestep_convergence_holds",
        "broken_pair_sensitivity_holds",
    ),
)
def test_inconclusive_precedes_stage_b_effect(field):
    assert decide_verdict(replace(passing_evidence(), **{field: False})) is Verdict.INCONCLUSIVE


def test_every_registered_effect_passes():
    assert decide_verdict(passing_evidence()) is Verdict.PASS


@pytest.mark.parametrize(
    "field",
    ("topology_difference_holds", "topology_sign_holds", "decoupled_zero_holds", "deterministic_rerun_holds"),
)
def test_clean_valid_run_without_stage_b_effect_is_null(field):
    assert decide_verdict(replace(passing_evidence(), **{field: False})) is Verdict.NULL


@pytest.mark.parametrize(
    ("predicate", "boundary", "expected"),
    (
        ("initial_energy", 1e-12, True),
        ("stability", 0.25, False),
        ("energy_drift", 0.005, False),
        ("identity_residual", 0.005, False),
        ("exercised_channel", 0.01, False),
        ("timestep_delta", 0.002, False),
        ("broken_pair_drift", 0.05, False),
        ("topology_contrast", 0.02, False),
        ("decoupled_matter", 1e-12, False),
        ("rerun_delta", 1e-12, False),
    ),
)
def test_exact_registered_boundaries(predicate, boundary, expected):
    assert REGISTERED_PREDICATES[predicate](boundary) is expected
```

Add `write_registered_manifest_fixture(tmp_path, include_reproduction)` without
running dynamics: use Task 6's real `write_run_manifest` and `CellJournal` to
write the complete registered run declaration and exactly the expected Stage-A
cell manifests, plus the six Stage-B reproduction manifests when requested.
`test_registered_artifact_matrix_matches_exactly` must pass for both expected
stages. A table-driven `test_configuration_gate_rejects_every_readable_mutation`
must clone that tree once per case and atomically change exactly one of: every
`P0Config` field (`grid_shape`, `c`, `k_b`, `g`, `dt`, `sigma`, `steps`,
`frame_stride`, `source_centres`); a cell's `stage`, `topology`, `mode`,
`purpose`, source centre, `dt`, or steps; the ordered run cell list; coupling
sites; supplied edges; or an extra readable cell manifest. Each case must make
`configuration_matches` false and therefore produce `FAIL`. Separate tests must
show that a missing declared cell, duplicate cell slug, malformed JSON, or
unreadable required manifest raises `ArtifactError` and produces no scientific
verdict, as required by the scope addendum.

- [ ] **Step 2: Run the verdict tests and verify import failure**

Run: `uv run pytest -o addopts="-v --strict-markers" tests/vibrasim2/test_p0_verdict.py -q`

Expected: FAIL because `verdict.py` does not exist.

- [ ] **Step 3: Encode the thresholds once and expose no override path**

```python
ENERGY_DRIFT_MAX = 0.005
IDENTITY_RESIDUAL_MAX = 0.005
EXERCISED_CHANNEL_MIN = 0.01
DT_HALF_DELTA_MAX = 0.002
BROKEN_PAIR_DRIFT_MIN = 0.05
TOPOLOGY_CONTRAST_MIN = 0.02
INITIAL_ENERGY_TOL = 1e-12
DECOUPLED_MATTER_TOL = 1e-12
RERUN_A_B_TOL = 1e-12
STABILITY_PRODUCT_MAX = 0.25
```

`CellMetrics` stores `a_b`, maximum relative energy drift, coupling-identity residual, maximum material-energy ratio, initial energy, maximum matter energy, and finiteness. `P0Evidence` uses the exact Boolean fields in the test. `StageAGate` stores `proceed: bool`, `provisional_verdict: Verdict | None`, and an ordered tuple of reason strings.

Define private named predicate functions and expose only this immutable test map:

```python
REGISTERED_PREDICATES = MappingProxyType(
    {
        "initial_energy": lambda delta: delta <= INITIAL_ENERGY_TOL,
        "stability": lambda product: product < STABILITY_PRODUCT_MAX,
        "energy_drift": lambda value: value < ENERGY_DRIFT_MAX,
        "identity_residual": lambda value: value < IDENTITY_RESIDUAL_MAX,
        "exercised_channel": lambda value: value > EXERCISED_CHANNEL_MIN,
        "timestep_delta": lambda value: value < DT_HALF_DELTA_MAX,
        "broken_pair_drift": lambda value: value > BROKEN_PAIR_DRIFT_MIN,
        "topology_contrast": lambda value: abs(value) > TOPOLOGY_CONTRAST_MIN,
        "decoupled_matter": lambda value: value < DECOUPLED_MATTER_TOL,
        "rerun_delta": lambda value: value < RERUN_A_B_TOL,
    }
)
```

The mapping accepts only measured scalars; thresholds remain module constants and
cannot be supplied by the caller. Add immediately-below and immediately-above
cases with `np.nextafter` for every entry so each strict or inclusive side is
proved, then use these same predicate functions inside `build_evidence`.

- [ ] **Step 4: Implement evidence construction and verdict order**

`build_evidence` must:

- call `validate_registered_artifacts(output_dir, include_reproduction=...)` on the reloaded run before any metric gate; compare `run.json` against `P0Config.registered()` and the exact ordered 24 Stage-A plus six reproduction-cell declarations, require exactly the executed cell-directory set for the current stage, and compare every readable `cell.json` field against its registered `RunCell`, stage, full `P0Config`, `coupling_sites()`, and `edges_for(cell.topology)`;
- classify every readable deviation outside the registered arm intervention as `configuration_matches=False`; missing, duplicate, malformed, or unreadable required records remain operational `ArtifactError` with no verdict;
- compare the machine-readable primary CYCLE and BRANCH manifests and allow only their registered supplied edge arrays and topology/slug labels to differ;
- require CYCLE/BRANCH initial energy equality within `1e-12` at every source;
- apply drift and identity limits only to CYCLE, BRANCH, NO_BONDS, and DECOUPLED;
- require CYCLE and BRANCH material-energy ratio strictly greater than `0.01`;
- compare each fixture's `A_B` and the signed CYCLE-minus-BRANCH contrast between `dt=0.05` and `dt=0.025`, each strictly below `0.002` difference;
- require BROKEN_PAIR drift strictly greater than `0.05` for at least one source centre separately for CYCLE and BRANCH;
- require `abs(A_CYCLE-A_BRANCH) > 0.02` at every source and identical non-zero sign across sources;
- require DECOUPLED maximum material energy strictly below `1e-12`;
- require fresh reproduction `A_B` within absolute `1e-12` for every CYCLE and BRANCH source.

`evaluate_stage_a` returns FAIL for a fail-class problem, INCONCLUSIVE for any remaining validity or sensitivity problem, and `proceed=True` only when all Stage-A gates hold. `decide_verdict` checks FAIL fields first, INCONCLUSIVE fields second, complete PASS third, and returns NULL otherwise. It performs no file I/O and accepts no numeric threshold argument.

- [ ] **Step 5: Run all verdict boundary tests**

Run: `uv run pytest -o addopts="-v --strict-markers" tests/vibrasim2/test_p0_verdict.py -q`

Expected: PASS, including equality-at-threshold cases proving the strict inequalities.

- [ ] **Step 6: Commit the registered decision logic**

```powershell
git add vibrasim2/p0/verdict.py tests/vibrasim2/test_p0_verdict.py
git commit -m "feat(v2-p0): add registered gates and ordered verdict"
```

---

### Task 8: Orchestrate Stages, Readback, and the Guarded CLI

**Files:**
- Modify: `docs/vibrasim2/P0_BUDGET_LEDGER.json`
- Create: `vibrasim2/p0/runner.py`
- Create: `vibrasim2/p0/cli.py`
- Create: `tests/vibrasim2/test_p0_runner.py`
- Create: `tests/vibrasim2/test_p0_cli.py`
- Modify: `pyproject.toml`

**Interfaces:**
- Consumes: the exact registered cells, dynamics, artifact readers/writers, and pure verdict code.
- Produces: `ObservationSink`, `ObservationSinkFactory`, `NullObservationSink`, internal `ExecutionMatrix`/`_run_execution`/`_run_registered_p0`, public `P0RunResult`/`PostRunBudgetError`/`run_registered_p0`, and `vibrasim2-p0`.

- [ ] **Step 1: Write failing stage-order and artifact-failure tests**

```python
# tests/vibrasim2/test_p0_runner.py
from dataclasses import replace
from pathlib import Path

import pytest

from vibrasim2.p0.artifacts import ArtifactError, atomic_write_json
from vibrasim2.p0.energy import EnergyRecord, Trajectory
from vibrasim2.p0.runner import ExecutionMatrix, NullObservationSink, _run_execution
from vibrasim2.p0.types import (
    ChannelMode,
    P0Config,
    P0StateSnapshot,
    RunCell,
    RunPurpose,
    Topology,
    Verdict,
)
from vibrasim2.p0.verdict import StageAGate


def short_trajectory(cell, config, initial) -> Trajectory:
    records = (
        EnergyRecord(0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, True),
        EnergyRecord(1, cell.dt, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, True),
    )
    return Trajectory(cell, records, (P0StateSnapshot(0, 0.0, initial),))


def test_execution() -> ExecutionMatrix:
    config = replace(P0Config.registered(), steps=1, source_centres=((4, 16),))
    cell = RunCell(Topology.CYCLE, ChannelMode.FULL, RunPurpose.PRIMARY, (4, 16), 0.05, 1)
    return ExecutionMatrix(config, (cell,), (), short_trajectory)


def stage_a_fail_result(*args, **kwargs) -> StageAGate:
    return StageAGate(False, Verdict.FAIL, ("forced Stage-A test failure",))


class RecordingSink(NullObservationSink):
    def __init__(self):
        self.events: list[tuple[str, str, int]] = []

    def after_snapshot_persisted(self, stage, cell, snapshot, cell_dir):
        assert (cell_dir / "snapshots" / f"snapshot-{snapshot.tick:010d}.npz").is_file()
        self.events.append((stage, cell.slug, snapshot.tick))


def test_stage_b_never_starts_after_failed_stage_a(tmp_path, monkeypatch):
    monkeypatch.setattr("vibrasim2.p0.runner.evaluate_stage_a", stage_a_fail_result)
    monkeypatch.setattr(
        "vibrasim2.p0.runner.run_reproduction_cells",
        lambda *args, **kwargs: pytest.fail("Stage B started after a closed Stage A"),
    )
    result = _run_execution(
        tmp_path, test_execution(), observer_factory=lambda run_id: RecordingSink()
    )
    assert result.verdict.value == "FAIL"


def test_artifact_failure_produces_no_scientific_verdict(tmp_path, monkeypatch):
    monkeypatch.setattr("vibrasim2.p0.runner.evaluate_stage_a", stage_a_fail_result)
    real_atomic_write_json = atomic_write_json

    def fail_result_only(path, value):
        if path.name == "result.json":
            raise ArtifactError("readback mismatch")
        return real_atomic_write_json(path, value)

    monkeypatch.setattr(
        "vibrasim2.p0.runner.atomic_write_json",
        fail_result_only,
    )
    with pytest.raises(ArtifactError, match="readback mismatch"):
        _run_execution(tmp_path, test_execution())
    assert not (tmp_path / "result.json").exists()
```

The helpers above are the complete minimal orchestration fixture. Add named tests proving raw artifacts are reloaded before evidence construction, CYCLE/BRANCH reproduction cells run only after Stage A proceeds, the observer callback follows snapshot persistence, Stage-A FAIL and INCONCLUSIVE both pass through common result finalization, and result readback precedes `P0RunResult` construction.

Add `write_registered_repository_fixture(tmp_path, ledger_status)` that copies
the two frozen documents byte-for-byte into a temporary repository layout and
writes a schema-valid budget ledger; it creates no output root. In
`test_budget_guard_precedes_directory_creation_and_execution`, call the private
registration seam `_run_registered_p0` with that temporary root and an overrun
ledger, spy on `_run_execution`, and assert the real budget error occurs before
the requested output directory exists and before execution. In
`test_scientific_run_owns_and_closes_one_budget_interval`, start from a valid
closed ledger, make `_run_execution` raise a sentinel operational error, and
assert that exactly one `scientific_run` interval bound to the generated run ID
was persisted before the call and closed with `outcome="aborted"` in `finally`.
Do not replace the real budget parser or atomic updater with a Boolean stub.

- [ ] **Step 2: Write failing CLI boundary tests**

```python
# tests/vibrasim2/test_p0_cli.py
from pathlib import Path
from types import SimpleNamespace

import pytest

from vibrasim2.p0.cli import main

RUN_PATH = Path("archive/run-logs/v2-p0/cli-boundary-test")


def test_help_is_safe(capsys):
    with pytest.raises(SystemExit) as stopped:
        main(["--help"])
    assert stopped.value.code == 0
    assert "registered V2-P0" in capsys.readouterr().out


def test_output_directory_is_explicit(capsys):
    with pytest.raises(SystemExit) as stopped:
        main(["run"])
    assert stopped.value.code == 2
    assert "--output-dir" in capsys.readouterr().err


def test_unregistered_axes_are_rejected(capsys):
    for option in ("--seed", "--dt", "--steps", "--g", "--k-b", "--source-centre"):
        with pytest.raises(SystemExit) as stopped:
            main(["run", "--output-dir", str(RUN_PATH), option, "1"])
        assert stopped.value.code == 2


def test_run_delegates_once_without_a_seed(monkeypatch):
    calls = []
    fake = SimpleNamespace(
        verdict=SimpleNamespace(value="NULL"), scientific_digest="abc123", output_dir=RUN_PATH
    )
    monkeypatch.setattr("vibrasim2.p0.cli.run_registered_p0", lambda path: calls.append(path) or fake)
    assert main(["run", "--output-dir", str(RUN_PATH)]) == 0
    assert calls == [RUN_PATH.resolve()]


def test_observe_changes_only_the_sink_factory(monkeypatch):
    calls = []
    factory = object()
    fake = SimpleNamespace(
        verdict=SimpleNamespace(value="NULL"), scientific_digest="abc123", output_dir=RUN_PATH
    )
    monkeypatch.setattr(
        "vibrasim2.p0.cli.resolve_observer_factory",
        lambda observe, path: factory if observe else None,
    )
    monkeypatch.setattr(
        "vibrasim2.p0.cli.run_registered_p0",
        lambda path, observer_factory=None: calls.append((path, observer_factory)) or fake,
    )
    assert main(["run", "--output-dir", str(RUN_PATH), "--observe"]) == 0
    assert calls == [(RUN_PATH.resolve(), factory)]
```

- [ ] **Step 3: Run the focused runner and CLI tests and verify failure**

Run: `uv run pytest -o addopts="-v --strict-markers" tests/vibrasim2/test_p0_runner.py tests/vibrasim2/test_p0_cli.py -q`

Expected: FAIL because the runner and CLI do not exist.

- [ ] **Step 4: Implement one-way snapshot notification and stage orchestration**

Define this boundary in `runner.py`:

```python
class ObservationSink(Protocol):
    def after_snapshot_persisted(
        self, stage: str, cell: RunCell, snapshot: P0StateSnapshot, cell_dir: Path
    ) -> None:
        raise NotImplementedError

    def close(self, result_recorded: bool) -> None:
        raise NotImplementedError


class NullObservationSink:
    def after_snapshot_persisted(self, stage, cell, snapshot, cell_dir):
        return None

    def close(self, result_recorded: bool):
        return None


TrajectoryExecutor = Callable[[RunCell, P0Config, P0State], Trajectory]
ObservationSinkFactory = Callable[[str], ObservationSink]


@dataclass(frozen=True)
class ExecutionMatrix:
    config: P0Config
    stage_a_cells: tuple[RunCell, ...]
    reproduction_cells: tuple[RunCell, ...]
    trajectory_executor: TrajectoryExecutor


@dataclass(frozen=True)
class P0RunResult:
    verdict: Verdict
    evidence: P0Evidence
    output_dir: Path
    scientific_digest: str
```

`_run_execution(output_dir, matrix, observer_factory=None, run_id=None, scientific_core_sha256=None)` is the only model seam; `None` constructs `NullObservationSink`, and missing run ID or core digest values are generated only by isolated tests using an explicit fixture sentinel. It atomically writes and reads `run.json`, including the supplied core digest, then passes its verified `run_id` to a supplied factory and starts no trajectory before the sink exists.

`_run_registered_p0(output_dir, *, repository_root, observer_factory=None, utc_now=...)` is the filesystem/clock test seam and still constructs the exact registered matrix; it accepts no model, fixture, threshold, timestep, or cell override. Public `run_registered_p0(output_dir, observer_factory=None)` supplies the verified real repository root and production UTC clock, exposing neither seam. The private boundary validates the two frozen documents, `P0Config.registered()`, the intended new direct-child path, and a closed within-cap budget ledger without writing. It then generates one run ID and atomically calls `start_budget_interval(..., phase="scientific_run", owner=run_id)` immediately before any output-directory creation. The returned immutable lease includes the validated pre-run `scientific_core_sha256`. Only after the lease is durable may the runner create the fixed root and new child and call `_run_execution(..., run_id=run_id, scientific_core_sha256=lease.scientific_core_sha256)`.

In a `finally` block, `_run_registered_p0` closes that exact lease with the real UTC end and `outcome="completed"` only after `result.json` readback produced a `P0RunResult`; every earlier exception closes it as `aborted`. A process crash may leave an open interval, which blocks every later run pending an explicit audited recovery; it is never backdated automatically. If lease closure fails after a scientific result was durably recorded, raise `PostRunBudgetError` carrying the result path and recorded verdict; do not erase or relabel the result. If closure succeeds with either `phase_reserve_breached` or `overrun_registration_required`, retain the factual artifacts, return no normal success, and raise the same stop error with the exact ledger status. Add tests for an exact 900-second completed run and a hard-cap crossing; both preserve the recorded result and raise the post-run stop. Unit tests use `_run_execution(tmp_path, ...)` for mechanics and `_run_registered_p0(..., repository_root=tmp_path)` only with complete temporary registration fixtures. Operationally incomplete directories are retained and never reused.

`run_stage_a` executes the 24 registered cells in declared order. For every cell, it writes energy each tick and, at ticks divisible by 10, atomically persists the snapshot before making a best-effort `observer.after_snapshot_persisted("A", cell, snapshot, cell_dir)` call. Reproduction cells pass stage `"B"`. Catch every observer exception at this boundary, record it only through a non-scientific best-effort hook, call the failed observer's idempotent `close(False)` best effort so it releases any viewer handle, replace it with `NullObservationSink`, and continue. An observer or its logger can never raise into simulation, persistence, evidence, or verdict code. If a non-finite state appears, persist its failure record and raw state, stop that cell, and let Stage-A evidence classify it as `FAIL`; do not convert it to `ArtifactError`.

After Stage-A records close, reload them and build Stage-A evidence. If the gate closes as FAIL or INCONCLUSIVE, skip Stage B and reproduction but pass that provisional verdict through `finalize_scientific_result`. If Stage A proceeds, reuse the persisted primary CYCLE/BRANCH trajectories for Stage-B effect metrics, execute exactly the six fresh REPRODUCTION cells, persist and reload them, build final evidence, and call `decide_verdict`.

`finalize_scientific_result(output_dir, evidence, verdict, observer)` is the one exit for all four scientific verdicts. It computes the canonical digest from reloaded raw records, atomically writes and independently reads `result.json`, constructs `P0RunResult` only from that readback, then calls `observer.close(result_recorded=True)` best effort. On `ArtifactError`, it calls `observer.close(result_recorded=False)` best effort and re-raises; no synthetic verdict or result object is returned. Observer-close exceptions are view events only.

The result JSON contains schema version, exact pre-registration identifiers (`28992a8b131100ed4eb2cd9147ddea7b3251921777211a63bb4b64e5524ca9e1`, blob `e5460f0b9ce837ec551bd0c3fb26d269c180f61b`) and exact addendum identifiers (`f0c20858ffaf3750320bd05cc1b120222264e7bd3e84109406f7b4a3cb7d9cb0`, blob `ff77a39fb5f9ac9f895d23a96ea9ff3f3b423b37`), the exact `scientific_core_sha256` copied from the verified run manifest, verdict, ordered reason strings, registered constants, per-cell metrics, and canonical scientific digest. Before writing, finalization rejects any mismatch between the core digest captured in the manifest and the execution context. Add a regression test which changes the repository core after lease acquisition and proves the recorded run retains the originally leased core identity rather than being relabelled. It contains no viewer, wallclock, process, or drop-counter fields.

- [ ] **Step 5: Add the guarded entry point**

Add to `pyproject.toml`:

```toml
vibrasim2-p0 = "vibrasim2.p0.cli:main"
```

`cli.py` accepts only `run --output-dir PATH [--observe]`. The resolved output path must be one new direct child of `archive/run-logs/v2-p0`; arbitrary roots, the root itself, symlink escapes, and every existing path, including an empty directory, are rejected. `resolve_observer_factory(False, output_dir)` returns `None`; the `True` path lazily imports and calls `vibrasim2.viewer_process.make_registered_observer_factory(output_dir)`, the stable integration symbol implemented in Task 12. No import occurs for help or headless execution. The CLI performs syntax validation and delegates exactly once; `--observe` changes only the supplied sink factory, never configuration or execution matrix. The non-bypassable public runner owns frozen-document, configuration, budget-lease, and output-path enforcement. It prints the recorded verdict and digest after readback. A completed scientific NULL, PASS, INCONCLUSIVE, or FAIL returns exit 0 because all four are records; malformed invocation returns 2; a pre-result artifact, registration, or budget failure returns 1 and prints `NO SCIENTIFIC VERDICT`. `PostRunBudgetError` also returns 1 but prints `SCIENTIFIC VERDICT RECORDED — BUDGET STOP`, the durable result path, and the recorded verdict so an operational ledger failure never rewrites history. Task 8 tests monkeypatch only the lazy resolver and never execute an observed or registered run; Task 12 supplies and tests the real target before the pre-run gate can pass.

- [ ] **Step 6: Run runner and CLI tests without a registered run**

Run: `uv run pytest -o addopts="-v --strict-markers" tests/vibrasim2/test_p0_runner.py tests/vibrasim2/test_p0_cli.py -q`

Expected: PASS using temporary, tiny orchestration fixtures only.

Run: `uv run vibrasim2-p0 --help`

Expected: exit 0; help lists no seed, threshold, timestep, source, or fixture override.

Run: `uv run pytest -o addopts="-v --strict-markers" tests/vibrasim2/test_p0_*.py -q`

Expected: PASS for the complete deterministic P0 implementation suite without creating a registered run.

Immediately after that successful suite, capture the actual RFC3339 UTC end of
the open ledger interval and store `elapsed_seconds=ceil(end-start)` plus the
exact cumulative sum, `outcome="completed"`, and the canonical
`scientific_core_sha256` over the declared budgeted paths. Set
`status="within_cap"` only when the cumulative value
is strictly below `19800`; otherwise set
`status="overrun_registration_required"`, append the fact to `LOGBOOK.md`, and
stop this P0 registration before any data. Re-run `test_p0_budget.py` against the
temporary edge cases, then call `assert_budget_allows_run` once on the closed
repository ledger and frozen registration identity. If any Task 4–8 source or test changes after closure,
append a new active interval before the edit and close it by the same rule.

Run: `uv run python -c "from pathlib import Path; from vibrasim2.p0.budget import assert_budget_allows_run; root=Path('.').resolve(); assert_budget_allows_run(root/'docs/vibrasim2/P0_BUDGET_LEDGER.json', '28992a8b131100ed4eb2cd9147ddea7b3251921777211a63bb4b64e5524ca9e1', root)"`

Expected: exit 0 only for a closed, internally consistent, within-cap ledger.

- [ ] **Step 7: Commit the staged runner**

```powershell
git add docs/vibrasim2/P0_BUDGET_LEDGER.json LOGBOOK.md pyproject.toml vibrasim2/p0/runner.py vibrasim2/p0/cli.py tests/vibrasim2/test_p0_runner.py tests/vibrasim2/test_p0_cli.py
git commit -m "feat(v2-p0): add staged runner and guarded CLI"
```

---

### Task 9: Replace Bond Semantics with a Neutral Observation Contract

**Files:**
- Create: `vibrasim2/observation.py`
- Create: `tests/test_vibrasim2_observation.py`
- Modify: `vibrasim2/wireframe.py`
- Modify: `tests/test_vibrasim2_wireframe.py`
- Modify: `docs/vibrasim2/CHARTER.md`

**Interfaces:**
- Consumes: existing `WireframeFrame` validation and renderer behavior.
- Produces: process-safe `EdgeState`, descriptive `EdgeKind`, `ObservationStatus`, `WireframeFrame`, `ObservationEnvelope`, and renderer-only `WireframeGeometry`.

- [ ] **Step 1: Write failing neutral-contract tests**

```python
# tests/test_vibrasim2_observation.py
import pickle

import numpy as np
import pytest

from vibrasim2.observation import EdgeKind, EdgeState, ObservationEnvelope, ObservationStatus, WireframeFrame


def make_frame() -> WireframeFrame:
    return WireframeFrame(
        positions=np.array(((0.0, 0.0, 0.0), (1.0, 0.0, 0.5))),
        edges=np.array(((0, 1),), dtype=np.int32),
        edge_states=(EdgeState.SUPPLIED,),
        edge_kinds=(EdgeKind.MATTER,),
        field_lines=(np.array(((0.0, 0.0, 0.0), (0.0, 1.0, 0.2))),),
    )


def test_frame_defensively_copies_and_freezes_arrays():
    source = np.array(((0.0, 0.0, 0.0), (1.0, 0.0, 0.5)))
    frame = WireframeFrame(
        source, np.array(((0, 1),)), (EdgeState.SUPPLIED,), (EdgeKind.MATTER,)
    )
    source[0, 0] = 99.0
    assert frame.positions[0, 0] == 0.0
    assert not frame.positions.flags.writeable


def test_envelope_is_spawn_serializable_and_has_no_verdict():
    envelope = ObservationEnvelope(
        schema_version=1, run_id="r1", stage="A", arm="cycle",
        source_centre=(4, 16), tick=10, simulation_time=0.5, sequence=1,
        emitted_monotonic_ns=100, status=ObservationStatus.RUNNING,
        display_scale=4.0, frame=make_frame(),
    )
    restored = pickle.loads(pickle.dumps(envelope))
    np.testing.assert_array_equal(restored.frame.positions, envelope.frame.positions)
    assert not hasattr(envelope, "verdict")


def test_unknown_schema_and_invalid_geometry_are_rejected():
    with pytest.raises(ValueError, match="schema_version"):
        ObservationEnvelope(
            2, "r1", "A", "cycle", (4, 16), 10, 0.5, 1, 100,
            ObservationStatus.RUNNING, 4.0, make_frame(),
        )
```

Rename and retain the existing checks as `test_edge_endpoints_are_in_range`, `test_position_shape_is_n_by_three`, `test_edge_shape_is_m_by_two`, `test_each_edge_has_one_state`, `test_field_lines_are_finite_two_point_polylines`, and `test_supplied_edge_colour_is_fixed_neutral_rgb`; update only bond-to-edge terminology and exact expected colour `(150, 170, 185)`.

- [ ] **Step 2: Run both observation test files and verify failure**

Run: `uv run pytest -o addopts="-v --strict-markers" tests/test_vibrasim2_observation.py tests/test_vibrasim2_wireframe.py -q`

Expected: FAIL because the neutral contract does not exist and the renderer still exports bond lifecycle semantics.

- [ ] **Step 3: Move data contracts out of PyVista code**

Define in `observation.py`:

```python
class EdgeState(str, Enum):
    SUPPLIED = "supplied"


class EdgeKind(str, Enum):
    MATTER = "matter"
    RECIPROCAL_COUPLING = "reciprocal_coupling"
    MATERIAL_ONLY_CONTROL = "material_only_control"


class ObservationStatus(str, Enum):
    RUNNING = "running"
    COMPLETE = "complete"


@dataclass(frozen=True)
class WireframeFrame:
    positions: NDArray[np.float64]
    edges: NDArray[np.int32]
    edge_states: tuple[EdgeState, ...]
    edge_kinds: tuple[EdgeKind, ...]
    field_lines: tuple[NDArray[np.float64], ...] = ()


@dataclass(frozen=True)
class ObservationEnvelope:
    schema_version: int
    run_id: str
    stage: str
    arm: str
    source_centre: tuple[int, int]
    tick: int
    simulation_time: float
    sequence: int
    emitted_monotonic_ns: int
    status: ObservationStatus
    display_scale: float
    frame: WireframeFrame
```

Validate schema version exactly 1, non-empty neutral metadata, non-negative tick/time/sequence, finite positive display scale, defensive array copies, immutable arrays, and exactly one state and one kind per edge. `EdgeKind` reports which declared equation term the line represents; it is not a lifecycle or success state. Do not add a seed, metric, progress percentage, or verdict field.

- [ ] **Step 4: Make `wireframe.py` a renderer only**

Import contracts from `vibrasim2.observation`. Rename `BOND_COLORS`, `bond_segments`, `bond_states`, actor name `bonds`, and all argument names to `EDGE_COLORS`, `edge_segments`, `edge_states`, and `edges`. Define only one value-neutral colour:

```python
EDGE_COLORS = {EdgeState.SUPPLIED: (150, 170, 185)}
```

The engineering demo uses `SUPPLIED` edges only and displays `ENGINEERING SMOKE — NOT SIMULATION DATA`. Matter, reciprocal-coupling, and material-only-control kinds may use fixed line widths or labels but share the same neutral colour; no kind implies progress or success. Remove stable/forming/breaking colors from the active charter; those terms remain available only in historical files describing mechanisms that actually computed them.

- [ ] **Step 5: Run contract and renderer tests**

Run: `uv run pytest -o addopts="-v --strict-markers" tests/test_vibrasim2_observation.py tests/test_vibrasim2_wireframe.py -q`

Expected: PASS without importing PyVista in the pure geometry tests.

- [ ] **Step 6: Commit the neutral renderer contract**

```powershell
git add vibrasim2/observation.py vibrasim2/wireframe.py tests/test_vibrasim2_observation.py tests/test_vibrasim2_wireframe.py docs/vibrasim2/CHARTER.md
git commit -m "refactor(v2-view): use neutral supplied-edge frames"
```

---

### Task 10: Project Persisted P0 State into Honest 3D Geometry

**Files:**
- Create: `vibrasim2/p0/observation.py`
- Create: `vibrasim2/observation_transport.py`
- Create: `tests/vibrasim2/test_p0_observation.py`
- Create: `tests/test_vibrasim2_observation_transport.py`

**Interfaces:**
- Consumes: persisted `P0StateSnapshot`, registered grid/sites/edges, and neutral envelopes.
- Produces: `ProjectionTopology`, `ObservationMetadata`, `ObservationProjectionConfig`, `project_p0_observation`, `PublishOutcome`, and `LatestOnlyPublisher`.

- [ ] **Step 1: Write failing projection tests over a tiny declared fixture**

```python
# tests/vibrasim2/test_p0_observation.py
import numpy as np

from vibrasim2.observation import EdgeKind, ObservationStatus
from vibrasim2.p0.observation import (
    ObservationMetadata,
    ObservationProjectionConfig,
    ProjectionTopology,
    project_p0_observation,
)
from vibrasim2.p0.types import P0State, P0StateSnapshot


def three_by_three_snapshot_and_topology():
    u = np.arange(1, 10, dtype=np.float64).reshape(3, 3)
    state = P0State(
        u,
        np.zeros((3, 3), dtype=np.float64),
        np.array((0.25, 0.2501), dtype=np.float64),
        np.zeros(2, dtype=np.float64),
    )
    topology = ProjectionTopology(
        grid_shape=(3, 3),
        coupling_sites=np.array(((0, 0), (0, 1)), dtype=np.int64),
        matter_edges=np.array(((0, 1),), dtype=np.int64),
        vertical_coupling_kind=EdgeKind.RECIPROCAL_COUPLING,
    )
    return P0StateSnapshot(10, 0.5, state), topology


def metadata(sequence: int = 1) -> ObservationMetadata:
    return ObservationMetadata(
        run_id="r1", stage="A", arm="cycle", source_centre=(0, 0),
        sequence=sequence, emitted_monotonic_ns=2_000_000_000,
        status=ObservationStatus.RUNNING,
    )


def expected_declared_edges():
    return {(9, 10), (0, 9), (1, 10)}


def test_projection_uses_only_declared_coordinates_and_scale():
    snapshot, topology = three_by_three_snapshot_and_topology()
    envelope = project_p0_observation(
        snapshot,
        topology,
        metadata(),
        ObservationProjectionConfig(display_scale=4.0),
    )
    np.testing.assert_array_equal(
        envelope.frame.positions[:9],
        np.array(
            [(x, y, 4.0 * snapshot.state.u[x, y]) for x in range(3) for y in range(3)],
            dtype=np.float64,
        ),
    )
    np.testing.assert_array_equal(envelope.frame.positions[9:, 2], np.array((1.0, 1.0004)))
    assert set(map(tuple, envelope.frame.edges)) == expected_declared_edges()
    assert envelope.frame.edge_kinds == (
        EdgeKind.MATTER,
        EdgeKind.RECIPROCAL_COUPLING,
        EdgeKind.RECIPROCAL_COUPLING,
    )
    before = snapshot.state.u.copy()
    project_p0_observation(
        snapshot,
        topology,
        metadata(sequence=2),
        ObservationProjectionConfig(display_scale=8.0),
    )
    np.testing.assert_array_equal(snapshot.state.u, before)


def test_spatial_proximity_never_creates_an_edge():
    snapshot, topology = three_by_three_snapshot_and_topology()
    frame = project_p0_observation(
        snapshot,
        topology,
        metadata(),
        ObservationProjectionConfig(display_scale=4.0),
    ).frame
    assert set(map(tuple, frame.edges)) == expected_declared_edges()


def test_field_lines_are_exact_declared_periodic_neighbours():
    snapshot, topology = three_by_three_snapshot_and_topology()
    frame = project_p0_observation(snapshot, topology, metadata(), ObservationProjectionConfig(4.0)).frame
    actual = {
        (tuple(line[0, :2].astype(int)), tuple(line[1, :2].astype(int)))
        for line in frame.field_lines
    }
    expected = {
        ((x, y), neighbour)
        for x in range(3)
        for y in range(3)
        for neighbour in (((x + 1) % 3, y), (x, (y + 1) % 3))
    }
    assert actual == expected
```

The complete 3×3 fixture above avoids the duplicate undirected edges inherent in a 2×2 periodic lattice. Add one bit-identical repeated-projection assertion and one assertion that changing `display_scale` changes only copied Z coordinates and envelope metadata, never the source snapshot or journal bytes. Implement `test_mode_projection_contains_only_active_terms` over four exact cases: FULL has registered matter edges plus six `RECIPROCAL_COUPLING` verticals; NO_BONDS has no matter edges plus six reciprocal verticals; DECOUPLED has registered matter edges and no verticals; BROKEN_PAIR has registered matter edges plus six `MATERIAL_ONLY_CONTROL` verticals. The BROKEN_PAIR HUD says `NON-RECIPROCAL SENSITIVITY CONTROL`, never Hamiltonian or reciprocal.

- [ ] **Step 2: Write failing latest-only queue tests**

```python
# tests/test_vibrasim2_observation_transport.py
from queue import Full

from vibrasim2.observation_transport import LatestOnlyPublisher


class ScriptedQueue:
    def __init__(self, puts, current=None):
        self.puts = iter(puts)
        self.current = current
        self.seen = []

    def put_nowait(self, item):
        self.seen.append(item)
        outcome = next(self.puts)
        if outcome == "full":
            raise Full

    def get_nowait(self):
        value, self.current = self.current, None
        return value


def test_full_queue_evicts_one_old_frame_and_retries_once():
    queue = ScriptedQueue(["full", "ok"], current="old")
    outcome = LatestOnlyPublisher(queue).publish("new")
    assert outcome.published
    assert outcome.evicted_previous
    assert len(queue.seen) == 2


def test_second_full_drops_only_new_frame():
    queue = ScriptedQueue(["full", "full"], current="old")
    outcome = LatestOnlyPublisher(queue).publish("new")
    assert outcome.dropped_new
    assert not outcome.published
```

Add cases for `Empty` during best-effort eviction and closed/broken queue errors; every case returns an outcome and never blocks or raises into the simulator.

- [ ] **Step 3: Run the projection and transport tests and verify failure**

Run: `uv run pytest -o addopts="-v --strict-markers" tests/vibrasim2/test_p0_observation.py tests/test_vibrasim2_observation_transport.py -q`

Expected: FAIL because projection and transport modules do not exist.

- [ ] **Step 4: Implement the producer-side observation embedding**

Define immutable `ProjectionTopology(grid_shape, coupling_sites, matter_edges, vertical_coupling_kind)`. Its generic validator requires a positive two-dimensional grid; `coupling_sites.shape == (n,2)` with every site inside the grid; `matter_edges.shape == (m,2)` with endpoints in `[0,n)`; no self-edge; `vertical_coupling_kind` either `None`, `RECIPROCAL_COUPLING`, or `MATERIAL_ONLY_CONTROL`; and `q.shape == (n,)`. Its production constructor accepts a registered `P0Config` and `RunCell`, requires exactly six coupling sites, and derives visible terms from `ChannelMode` exactly as tested above. Tiny tests construct it directly.

Define immutable `ObservationMetadata(run_id, stage, arm, source_centre, sequence, emitted_monotonic_ns, status)`. `project_p0_observation` reads no clock: live code injects `time.monotonic_ns()` after persistence, and replay injects a fresh enqueue timestamp. Use `ObservationProjectionConfig(display_scale=4.0, schema_version=1)` with no CLI override. Flatten the field grid in C order and create field points `(x1, x2, 4*u[x1,x2])`. Append matter points `(site_x, site_y, 4*q[i])`. `matter_edges` remains in local oscillator indices until projection offsets it by `grid_size`; append vertical edges only when `vertical_coupling_kind` is not `None`. Give every edge `EdgeState.SUPPLIED` and its declared `EdgeKind`; never infer an edge from proximity.

Create each field line from exactly one registered right or down periodic neighbour pair. The renderer receives those two-point polylines even where the periodic wrap appears long; it must not infer a shorter spatial route. Axis labels are `grid x`, `grid y`, and `model displacement × S`; the HUD states `S=4`.

- [ ] **Step 5: Implement non-blocking latest-only publication**

`LatestOnlyPublisher.publish` performs one `put_nowait`; on `queue.Full`, one best-effort `get_nowait`, then one final `put_nowait`. It catches `Full`, `Empty`, `EOFError`, `OSError`, `ValueError`, and `BrokenPipeError`, updates local counters, and returns:

```python
@dataclass(frozen=True)
class PublishOutcome:
    published: bool
    evicted_previous: bool
    dropped_new: bool
```

It exposes no `put`, timeout, sleep, viewer-status read, or callback into the runner.

- [ ] **Step 6: Run projection and transport tests**

Run: `uv run pytest -o addopts="-v --strict-markers" tests/vibrasim2/test_p0_observation.py tests/test_vibrasim2_observation_transport.py -q`

Expected: PASS.

- [ ] **Step 7: Commit projection and transport**

```powershell
git add vibrasim2/p0/observation.py vibrasim2/observation_transport.py tests/vibrasim2/test_p0_observation.py tests/test_vibrasim2_observation_transport.py
git commit -m "feat(v2-view): project and publish persisted P0 frames"
```

---

### Task 11: Add a Pure Viewer Controller and Spawn-Safe Process

**Files:**
- Create: `vibrasim2/viewer_process.py`
- Create: `tests/test_vibrasim2_viewer_controller.py`
- Modify: `vibrasim2/wireframe.py`

**Interfaces:**
- Consumes: `ObservationEnvelope` from a queue and a stop event only.
- Produces: `ViewerProcessConfig`, `viewer_config_for_registered_p0`, `ViewerController`, `viewer_process_main`, and a PyVista adapter with no simulator function.

- [ ] **Step 1: Write failing controller and HUD tests**

```python
# tests/test_vibrasim2_viewer_controller.py
import numpy as np

from vibrasim2.observation import ObservationEnvelope, ObservationStatus, WireframeFrame
from vibrasim2.viewer_process import ViewerController


def envelopes_at_ticks(*ticks: int) -> tuple[ObservationEnvelope, ...]:
    frame = WireframeFrame(
        positions=np.array(((0.0, 0.0, 0.0), (1.0, 0.0, 0.5))),
        edges=np.empty((0, 2), dtype=np.int32),
        edge_states=(),
        edge_kinds=(),
    )
    return tuple(
        ObservationEnvelope(
            schema_version=1, run_id="r1", stage="A", arm="cycle",
            source_centre=(4, 16), tick=tick, simulation_time=tick * 0.05,
            sequence=sequence, emitted_monotonic_ns=2_000_000_000,
            status=ObservationStatus.RUNNING, display_scale=4.0, frame=frame,
        )
        for sequence, tick in enumerate(ticks, start=1)
    )


def test_freeze_holds_display_while_pending_advances():
    controller = ViewerController()
    first, second, third = envelopes_at_ticks(10, 20, 30)
    controller.accept(first)
    assert controller.next_drawable() == first
    controller.set_frozen(True)
    controller.accept(second)
    controller.accept(third)
    assert controller.next_drawable() is None
    controller.set_frozen(False)
    assert controller.next_drawable() == third


def test_hud_is_neutral_and_reports_frame_age():
    controller = ViewerController()
    controller.accept(envelopes_at_ticks(10)[0])
    hud = controller.hud(now_ns=2_100_000_000)
    assert "RAW SIMULATION STATE" in hud
    assert "OBSERVATION ONLY" in hud
    assert "VERDICT PENDING" in hud
    assert "S=4" in hud
    assert "PASS" not in hud and "NULL" not in hud
```

Implement `test_complete_changes_only_the_neutral_footer`, `test_broken_pair_hud_labels_nonreciprocal_sensitivity_control`, `test_controller_exposes_no_simulation_callback`, `test_draw_cadence_never_limits_queue_polling`, and `test_unfreeze_draws_only_the_newest_envelope`. The first compares RUNNING and COMPLETE HUD lines except for the footer. The BROKEN_PAIR case supplies `EdgeKind.MATERIAL_ONLY_CONTROL`, requires the exact label `NON-RECIPROCAL SENSITIVITY CONTROL`, and forbids `HAMILTONIAN` plus any separate `RECIPROCAL COUPLING` label. The third rejects `step`, `play`, `pause`, and callable source attributes; the fourth proves three queue drains during one draw interval; the fifth uses ticks 10/20/30 and expects only tick 30 after unfreeze.

- [ ] **Step 2: Run controller tests and verify import failure**

Run: `uv run pytest -o addopts="-v --strict-markers" tests/test_vibrasim2_viewer_controller.py -q`

Expected: FAIL because `viewer_process.py` does not exist.

- [ ] **Step 3: Implement the pure controller and process configuration**

```python
@dataclass(frozen=True)
class ViewerProcessConfig:
    grid_shape: tuple[int, int] = (32, 32)
    display_scale: float = 4.0
    camera_position: tuple[float, float, float] = (48.0, -48.0, 32.0)
    camera_focal_point: tuple[float, float, float] = (15.5, 15.5, 0.0)
    draw_interval_seconds: float = 0.1
    shutdown_timeout_seconds: float = 2.0


@dataclass
class ViewerController:
    frozen: bool = False
    displayed: ObservationEnvelope | None = None
    pending: ObservationEnvelope | None = None

    def accept(self, envelope: ObservationEnvelope) -> None:
        self.pending = envelope

    def set_frozen(self, frozen: bool) -> None:
        self.frozen = frozen

    def next_drawable(self) -> ObservationEnvelope | None:
        if self.frozen or self.pending is None:
            return None
        self.displayed, self.pending = self.pending, None
        return self.displayed
```

`viewer_config_for_registered_p0()` returns the exact values above. The viewer uses the fixed camera and scale for the entire live or replay session; it does not derive bounds, colour, size, or camera distance from frame amplitude. It may update clipping planes only to keep the supplied geometry visible and shows no amplitude-normalized cage. `c` restores the declared camera.

`hud(now_ns)` derives non-negative frame age from `emitted_monotonic_ns`, prints run ID, Stage, Arm, source centre, tick, simulation time, frame age, status, and `S=4`. It never accepts a metric or verdict value.

- [ ] **Step 4: Replace the synchronous pull viewer with a queue consumer**

Define a module-level, importable function:

```python
def viewer_process_main(frame_queue, stop_event, config: ViewerProcessConfig) -> None:
    from vibrasim2.wireframe import WireframeViewer

    WireframeViewer(frame_queue, stop_event, config).run()
```

The PyVista loop polls window events continuously, drains the queue with `get_nowait` to the most recent envelope, feeds the controller, and limits only drawing. When `stop_event` becomes set, it performs a final drain for at most `0.25` seconds, renders the newest envelope if one arrives, processes one final window-event cycle, and exits. This improves but does not guarantee delivery of the deliberately lossy COMPLETE frame. `space` toggles visible freeze; `c` resets the camera. Remove the current `s` binding and all play/step simulator semantics. PyVista is imported only inside rendering functions or process entry points.

The viewer process receives no `P0Config`, runner callable, seed, output writer, or writable journal handle. Its only inputs are the copied envelope queue, stop event, and display config.

- [ ] **Step 5: Run controller and renderer tests**

Run: `uv run pytest -o addopts="-v --strict-markers" tests/test_vibrasim2_viewer_controller.py tests/test_vibrasim2_wireframe.py -q`

Expected: PASS without opening a window.

- [ ] **Step 6: Commit the spawn-safe viewer**

```powershell
git add vibrasim2/viewer_process.py vibrasim2/wireframe.py tests/test_vibrasim2_viewer_controller.py
git commit -m "feat(v2-view): add observer-only viewer process"
```

---

### Task 12: Integrate Live Observation, Replay, and Bounded Shutdown

**Files:**
- Create: `tests/vibrasim2/test_p0_runner_observer.py`
- Create: `tests/test_vibrasim2_spawn_transport.py`
- Create: `tests/test_vibrasim2_wireframe_gui.py`
- Modify: `vibrasim2/viewer_process.py`
- Modify: `vibrasim2/wireframe.py`
- Modify: `pyproject.toml`

**Interfaces:**
- Consumes: persisted P0 snapshots, pure projection, latest-only publisher, and spawn-safe viewer.
- Produces: `ViewerHandle`, `P0ObservationSink`, `append_view_event_best_effort`, `start_viewer`, `shutdown_viewer`, `iter_replay_envelopes`, live `--observe`, and a read-only `vibrasim2-view --replay PATH` mode.

- [ ] **Step 1: Write failing observer-isolation tests**

```python
# tests/vibrasim2/test_p0_runner_observer.py
def test_persistence_precedes_publication(tmp_path):
    calls = []
    sink = recording_observation_sink(calls)
    run_tiny_execution(tmp_path, observer=sink, calls=calls)
    assert calls.index("snapshot:10:persisted") < calls.index("snapshot:10:published")


def test_headless_and_lossy_observation_have_identical_science(tmp_path):
    headless = run_tiny_execution(tmp_path / "headless")
    observed = run_tiny_execution(
        tmp_path / "observed", observer=always_dropping_observation_sink()
    )
    assert canonical_raw_records(tmp_path / "headless") == canonical_raw_records(tmp_path / "observed")
    assert headless.scientific_digest == observed.scientific_digest
    assert headless.verdict == observed.verdict


def test_replay_never_calls_dynamics(tmp_path, monkeypatch):
    write_two_snapshot_journal(tmp_path)
    monkeypatch.setattr(
        "vibrasim2.p0.dynamics.velocity_verlet_step",
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("replay simulated")),
    )
    assert [item.tick for item in iter_replay_envelopes(tmp_path)] == [10, 20]
```

Define the helper bodies in this test module, not as placeholders: `run_tiny_execution` calls Task 8's `_run_execution` with one CYCLE/FULL cell configured for 10 steps; its deterministic executor returns finite energy records for ticks `0..10` and snapshots at ticks `0` and `10`. `recording_observation_sink` appends `published` only after it sees the tick-10 NPZ; `always_dropping_observation_sink` returns a `PublishOutcome(False, False, True)` without raising; `canonical_raw_records` returns the sorted decoded cell/energy/snapshot values while excluding run ID and view metadata; and `write_two_snapshot_journal` uses Task 6's `CellJournal` to write ticks 10 and 20 plus complete `run.json`/`cell.json` replay metadata.

Add named tests for a full queue, a closed queue, invalid envelope construction, view-event log failure, viewer start failure, viewer crash, no-snapshot completion, idempotent sink close, and exact shutdown ownership/order: last raw record, verdict, atomic `result.json` readback, one best-effort COMPLETE publish, stop event, bounded healthy join, viewer-only termination plus bounded second join if still alive, then queue cancel/close. Assert that `P0ObservationSink.close()` owns shutdown and invokes it exactly once for both `close(True)` and `close(False)`; repeated calls are no-ops.

In `tests/test_vibrasim2_spawn_transport.py`, define a module-level PyVista-free worker that reads one envelope with a bounded timeout, reports its tick through a second queue, observes the stop event, performs the same bounded final drain, and exits. Start it with `multiprocessing.get_context("spawn")`; assert normal envelope delivery, best-effort delivery of a queued COMPLETE frame during shutdown, and bounded clean exit. This is the mandatory cross-process contract test. The real OpenGL test remains optional; neither test promotes best-effort live delivery into scientific evidence.

- [ ] **Step 2: Run isolation tests and verify missing integration**

Run: `uv run pytest -o addopts="-v --strict-markers" tests/vibrasim2/test_p0_runner_observer.py -q`

Expected: FAIL because the observation sink and replay integration do not exist.

- [ ] **Step 3: Implement lifecycle helpers with `spawn` and `maxsize=1`**

Define these concrete boundaries:

```python
@dataclass
class ViewerHandle:
    process: multiprocessing.Process | None
    queue: object | None
    stop_event: object | None
    publisher: LatestOnlyPublisher | None
    config: ViewerProcessConfig
    shutdown_started: bool = False
```

Implement `P0ObservationSink(handle: ViewerHandle, output_dir: Path, run_id: str)`, `P0ObservationSink.after_snapshot_persisted(stage: str, cell: RunCell, snapshot: P0StateSnapshot, cell_dir: Path) -> None`, `P0ObservationSink.close(result_recorded: bool) -> None`, `start_viewer(output_dir: Path, config: ViewerProcessConfig) -> ViewerHandle`, `shutdown_viewer(handle: ViewerHandle) -> None`, and `append_view_event_best_effort(output_dir: Path, event: Mapping[str, object]) -> None` with the behavior below. `start_viewer` calls `multiprocessing.get_context("spawn")`, creates `Queue(maxsize=1)` and `Event`, and starts a process whose target is module-level `viewer_process_main`. If start fails, return a disabled handle whose sink implements the same API and append `viewer_start_failed` only through `append_view_event_best_effort`. The sink is the sole owner of a successfully constructed live handle; construction failure closes the handle before re-raising, and the sink's first `close` call always transfers to bounded shutdown in a `finally` block.

Construct `P0ObservationSink(handle, output_dir, run_id)` only through the runner's `ObservationSinkFactory`, after `run.json` has survived readback. `after_snapshot_persisted(stage, cell, snapshot, cell_dir)` reads no simulator state: the runner supplies the explicit Stage A/B value, while the sink takes `cell.arm_label` and `cell.source_centre` from `RunCell`, injects its verified `run_id` and `time.monotonic_ns()` into `ObservationMetadata`, projects with fixed `S=4`, and calls `LatestOnlyPublisher.publish`. It keeps only the last successfully persisted-and-projected envelope copy. Projection, queue, payload, and event-log failures are caught; display failures are recorded best effort in `view-events.jsonl` outside the scientific digest and never escape to the runner. Cap that log at 256 compact records and 64 KiB, with later counts aggregated in memory, so observation diagnostics have a fixed small disk budget.

On the first `close(True)`, if a last envelope exists, the sink best-effort publishes a copy with `status=COMPLETE`, a fresh non-scientific sequence and enqueue timestamp, and no verdict field. With no envelope, it synthesizes no frame. `close(False)` never publishes COMPLETE. Both paths call `shutdown_viewer(handle)` exactly once in `finally`; later calls return without touching process or queue state.

`shutdown_viewer` is idempotent. It performs best-effort `stop_event.set()`, then `process.join(2.0)` so a healthy viewer can perform its final bounded drain. Only if `process.is_alive()` does it call `process.terminate()` and join again with the same bound. After the viewer has exited or the second bound has elapsed, it calls `queue.cancel_join_thread()` and `queue.close()`. It never calls `queue.join_thread()` and never terminates the simulator process. Every failure in this sequence is a view event only; live COMPLETE remains best effort and cannot delay scientific finalization beyond the fixed observer-shutdown bound.

- [ ] **Step 4: Fulfil the frozen live-observer seam and add replay**

Implement `vibrasim2.viewer_process.make_registered_observer_factory(output_dir)` with the exact symbol and `ObservationSinkFactory` behavior already consumed by Task 8's lazy `--observe` path; do not edit the now-digested P0 CLI or runner. Headless remains the default. Add mutually exclusive `--demo` and `--replay PATH` to `vibrasim2-view`. Demo HUD always says `ENGINEERING SMOKE — NOT SIMULATION DATA`; replay opens either one cell-journal directory or a run root read-only. A run root follows the exact cell order stored in `run.json` and snapshots in tick order, rejecting missing, duplicate, or extra cell directories. It reconstructs exact topology from `run.json` plus `cell.json`, uses their frozen observation schema and `S=4`, injects a new enqueue timestamp, and never imports or calls runner functions.

If `result.json` readback succeeds, `observer.close(True)` triggers the best-effort last-envelope COMPLETE behavior above; its footer says only `VERDICT RECORDED IN result.json`. If no result was recorded, never publish COMPLETE. COMPLETE is a non-journaled viewer state and is excluded from the scientific digest. Replay does not trust that live frame: it reads `result.json` itself, validates its schema and recomputed scientific digest, and marks only the final replay envelope COMPLETE. With missing or invalid result metadata it never shows the recorded-verdict footer. Thus replay status is reliable while live completion display remains explicitly lossy.

- [ ] **Step 5: Add display-independent integration tests and optional GUI smoke**

Register `gui` in `pyproject.toml`; mark every test in `test_vibrasim2_wireframe_gui.py` with both `@pytest.mark.gui` and `@pytest.mark.external`. The opt-in file must cover process start/close, one supplied edge, field lines, one vertical coupling line, freeze behavior, and two-frame replay. It must use a temporary journal and must not execute P0 dynamics.

Run: `uv run pytest -o addopts="-v --strict-markers" tests/vibrasim2/test_p0_runner_observer.py tests/test_vibrasim2_observation_transport.py tests/test_vibrasim2_viewer_controller.py tests/test_vibrasim2_spawn_transport.py -q`

Expected: PASS without a display.

Run on Windows with a real desktop: `uv run pytest -o addopts="-v --strict-markers" --include-quarantined -m gui tests/test_vibrasim2_wireframe_gui.py -q`

Expected: PASS. Record the result as Windows-only evidence; macOS remains **uncertainty: medium** until the same command is run there.

- [ ] **Step 6: Commit observer integration**

```powershell
git add pyproject.toml vibrasim2/viewer_process.py vibrasim2/wireframe.py tests/vibrasim2/test_p0_runner_observer.py tests/test_vibrasim2_spawn_transport.py tests/test_vibrasim2_wireframe_gui.py
git commit -m "feat(v2-view): integrate live observation and replay"
```

---

### Task 13: Rewrite the README as a Public Research Laboratory

**Files:**
- Create: `tests/test_readme_contract.py`
- Modify: `README.md`

**Interfaces:**
- Consumes: only behavior and commands verified by Tasks 1 through 12 plus the recorded G174 result.
- Produces: one concise public entrance that distinguishes active question, evidence, history, hope, engineering smoke, and unresolved licensing.

- [ ] **Step 1: Write failing README truth and local-link tests**

```python
# tests/test_readme_contract.py
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = (ROOT / "README.md").read_text(encoding="utf-8")
ACTIVE_QUESTION = "V2-P0 reciprocal field–matter channel"


def test_readme_states_purpose_and_epistemic_limits():
    required = (
        "public research laboratory",
        "nomenclature, not ontology",
        "deadlocks are part of the material",
        "Vibrasim II",
        "V2-P0",
        "BP-C6 (G174)",
        "INVARIANT (NULL)",
        "approximately `1e-15`",
        "observation instrument",
    )
    for phrase in required:
        assert phrase in README, phrase
    for path in ("AGENTS.md", "FRONTIER.md", "README.md", "LOGBOOK.md"):
        assert ACTIVE_QUESTION in (ROOT / path).read_text(encoding="utf-8"), path


def test_g174_number_is_unambiguously_historical():
    opening = README.split("## Current question", 1)[0]
    assert "latest recorded result is historical" in opening.lower()
    assert "BP-C6 (G174)" in opening
    assert "INVARIANT (NULL)" in opening
    history = README.split("## What Vibrasim I established", 1)[1].split("\n## ", 1)[0]
    assert "BP-C6 (G174)" in history
    assert "INVARIANT (NULL)" in history
    assert "approximately `1e-15`" in history
    current = README.split("## Current question", 1)[1].split("\n## ", 1)[0]
    assert "1e-15" not in current


def test_readme_contains_no_stale_test_or_license_claim():
    forbidden = (
        "313 non-slow tests",
        "313 + 22 slow",
        "Code under MIT",
        "Documentation under CC-BY-SA",
        "Active programme: belief path",
    )
    for phrase in forbidden:
        assert phrase not in README, phrase
    assert not re.search(r"active programme[^\n]{0,100}belief path", README, flags=re.IGNORECASE)
    assert "[Belief Path (historical/frozen)](docs/BELIEF_PATH.md)" in README
    assert "[Discipline Sharp (historical/frozen)](docs/DISCIPLINE_SHARP.md)" in README
    assert "License status: pending project-owner decision" in README


def test_every_relative_markdown_link_exists():
    targets = re.findall(r"\[[^]]+\]\(([^)]+)\)", README)
    missing = []
    for target in targets:
        clean = target.split("#", 1)[0]
        if not clean or "://" in clean or clean.startswith("mailto:"):
            continue
        if not (ROOT / clean).exists():
            missing.append(target)
    assert missing == []


def test_quickstart_separates_safe_checks_from_data_creating_runs():
    assert "uv run pytest" in README
    assert "uv run vibrasim2-p0 --help" in README
    assert "uv run vibrasim2-p0 run --output-dir archive/run-logs/v2-p0/manual-p0-run-001" in README
    assert "uv run vibrasim2-p0 run --output-dir archive/run-logs/v2-p0/manual-p0-observed-001 --observe" in README
    assert "creates scientific data" in README.lower()
    assert "fresh direct child" in README.lower()
    assert "ENGINEERING SMOKE — NOT SIMULATION DATA" in README
```

- [ ] **Step 2: Run the README contract and confirm current failures**

Run: `uv run pytest -o addopts="-v --strict-markers" tests/test_readme_contract.py -q`

Expected: FAIL on stale programme, test-count, license, and missing-link claims.

- [ ] **Step 3: Replace the opening with Michael's supported voice**

Use this as the editorial draft. Its direction is supported by Michael's existing
README and by his explicit statement that the repository is a public signal of
how he works, with a small hope that something may emerge. Do not machine-lock
the exact personal sentences; Michael reviews the final wording before push:

```markdown
# Vibrasim

Vibrasim is my public research laboratory for a question I cannot bluff my way
through: can organisation acquire function through an explicit physical loop,
rather than through labels, targets, or a trained model?

I do not know whether Vibrasim will become anything. I keep the work public
because the method matters to me: make one claim precise, define what would
falsify it before the run, keep the failures visible, and change direction when
the substrate says no.

The names in this repository are nomenclature, not ontology. "Matter",
"memory", and "bonds" name model variables and scoped tests; they do not make
claims about nature. The deadlocks are part of the material.

The latest recorded result is historical: BP-C6 (G174) returned INVARIANT
(NULL), with treatment contrast approximately `1e-15` across its registered
cells. It closed that Vibrasim-I route; it is not evidence for the current P0.
```

Implementation and run statements remain neutral: `the repository implements`, `the record shows`, and `the run returned`. The local README commit is a reviewable draft, not an inferred authorization to publish personal wording.

- [ ] **Step 4: Build the remaining README around one current question**

Use this order and factual scope:

1. `Current question` — V2-P0 asks only whether an energy-consistent reciprocal field–matter channel produces topology-sensitive transfer in the registered oscillator fixture.
2. `What this is / is not` — state no claim for life, cognition, individuation, persistence, memory, or talent; no neural network, pretrained component, reward, or trained readout in P0.
3. `Current status` — P0 is pre-registered and, at this reset, has no recorded result. Link the charter, frozen pre-registration, scope addendum, frontier, and logbook.
4. `What Vibrasim I established` — include exactly one quantitative anchor: BP-C6 (G174) returned `INVARIANT (NULL)` with treatment contrast approximately `1e-15` across its registered cells, closing the axial linear-compliance route. Link historical Belief Path and Discipline documents as `historical/frozen`.
5. `How I work` — one question, frozen bars, controls, ordered verdict, append-only record, no post-hoc threshold repair.
6. `Run the safe development checks` — `uv sync --frozen --extra dev`, `uv run pytest`, `uv build`. Do not publish a test count.
7. `P0 runner` — show `uv run vibrasim2-p0 --help`, then the functional headless example `uv run vibrasim2-p0 run --output-dir archive/run-logs/v2-p0/manual-p0-run-001`. Label it explicitly `CREATES SCIENTIFIC DATA`; require a fresh direct child for each run and instruct the reader to inspect the frozen registration first. Task 14 adds the exact pre-run verifier command only after that tool exists. Documenting the run command does not authorize executing it during this implementation.
8. `3D observation` — open with `The 3D view is an observation instrument, not evidence.` Then describe the fixed `S=4` embedding, observer-only process, no feedback, no live verdict, and replay from persisted snapshots. Label `uv run vibrasim2-view --demo` as `ENGINEERING SMOKE — NOT SIMULATION DATA`. Show the functional observed-run example `uv run vibrasim2-p0 run --output-dir archive/run-logs/v2-p0/manual-p0-observed-001 --observe` under the same data-creation warning.
9. `Repository map` — current V2 links first, historical V1 links second.
10. `License` — state only `License status: pending project-owner decision.` until Michael separately chooses terms.

Remove obsolete active Belief-Path framing, old test counts, missing document links, product-style phase claims, long dashboard/autonomous runbooks, and the false `LICENSE` link. Do not delete the underlying historical documents, figures, archive data, or bibliography. Keep `docs/vibrasim2/figures/morphodynamic_progress_concept.png` only with an explicit `DESIGN VISION — NOT RUN OUTPUT` caption; do not place it beside a result.

- [ ] **Step 5: Verify links and every documented command that does not create P0 data**

Run: `uv run pytest -o addopts="-v --strict-markers" tests/test_readme_contract.py -q`

Expected: PASS.

Run: `uv run vibrasim2-p0 --help`

Expected: exit 0.

Run: `uv run vibrasim2-view --help`

Expected: exit 0 and explicit demo/replay distinction.

Run: `uv build`

Expected: PASS. The two guarded P0 run examples are documented but not executed.

- [ ] **Step 6: Commit the public-laboratory entrance**

```powershell
git add README.md tests/test_readme_contract.py
git commit -m "docs: present Vibrasim as a public research laboratory"
```

---

### Task 14: Add and Execute the Pre-Run Verification Gate

**Files:**
- Create: `tools/verify_vibrasim2_reset.py`
- Create: `tests/vibrasim2/test_reset_verifier.py`
- Modify: `README.md`
- Modify: `tests/test_readme_contract.py`

**Interfaces:**
- Consumes: repository root, the pre-implementation P0-output baseline, the closed implementation-budget ledger, and completed Tasks 1 through 13.
- Produces: a repository-state-preserving JSON verification report, an exit status, and the final exact README pre-run command. It may create ignored caches or temporary build artifacts, verifies repository state before/after, and never starts P0, opens a GUI, pushes, or changes GitHub settings.

- [ ] **Step 1: Write failing tests for the state-preserving gate and its README entry**

```python
# tests/vibrasim2/test_reset_verifier.py
from vibrasim2.p0.budget import BudgetError
from tools.verify_vibrasim2_reset import Check, check_budget_ledger, compare_output_tree, summarize


def test_summary_fails_if_any_required_check_fails():
    report = summarize((Check("one", True, "ok"), Check("two", False, "broken")))
    assert not report["ready_for_run_review"]
    assert report["failed"] == ["two"]


def test_summary_separates_platform_uncertainty():
    report = summarize(
        (Check("unit", True, "ok"),),
        platform_notes={"windows_gui": "passed", "macos_gui": "unverified"},
    )
    assert report["ready_for_run_review"]
    assert report["platform_notes"]["macos_gui"] == "unverified"


def test_output_tree_comparison_includes_untracked_and_ignored_files(tmp_path):
    assert compare_output_tree(tmp_path / "absent", expected_files=())
    root = tmp_path / "v2-p0"
    root.mkdir()
    assert compare_output_tree(root, expected_files=())
    (root / "ignored-looking.npz").write_bytes(b"data")
    assert not compare_output_tree(root, expected_files=())


def test_budget_rejection_blocks_run_review(tmp_path, monkeypatch):
    def reject(*args, **kwargs):
        raise BudgetError("hard ceiling reached")

    monkeypatch.setattr("tools.verify_vibrasim2_reset.assert_budget_allows_run", reject)
    check = check_budget_ledger(
        tmp_path / "ledger.json",
        expected_registration_sha256="registered",
        repository_root=tmp_path,
    )
    assert not check.passed
    assert "hard ceiling reached" in check.detail
    assert not summarize((check,))["ready_for_run_review"]
```

Append this contract only in Task 14, so it fails until the verifier exists and
the README can truthfully name it:

```python
# append to tests/test_readme_contract.py
def test_readme_names_exact_pre_run_gate_before_data_commands():
    gate = "uv run python -B tools/verify_vibrasim2_reset.py"
    headless = "uv run vibrasim2-p0 run --output-dir archive/run-logs/v2-p0/manual-p0-run-001"
    observed = "uv run vibrasim2-p0 run --output-dir archive/run-logs/v2-p0/manual-p0-observed-001 --observe"
    assert gate in README
    assert README.index(gate) < README.index(headless)
    assert README.index(gate) < README.index(observed)
    assert "does not create scientific data" in README.lower()
```

- [ ] **Step 2: Run the verifier tests and confirm import failure**

Run: `uv run pytest -o addopts="-v --strict-markers" tests/vibrasim2/test_reset_verifier.py tests/test_readme_contract.py -q`

Expected: FAIL because the verifier and its exact README gate entry do not exist.

- [ ] **Step 3: Implement state-preserving checks and command evidence**

Define:

```python
@dataclass(frozen=True)
class Check:
    name: str
    passed: bool
    detail: str


def summarize(checks: tuple[Check, ...], platform_notes: dict[str, str] | None = None) -> dict:
    failed = [check.name for check in checks if not check.passed]
    return {
        "schema_version": 1,
        "ready_for_run_review": not failed,
        "failed": failed,
        "checks": [asdict(check) for check in checks],
        "platform_notes": platform_notes or {},
    }
```

`check_budget_ledger(path, expected_registration_sha256, repository_root)` wraps the production
`assert_budget_allows_run` parser and returns a failed `Check` with the concrete
domain error instead of raising. It must not reimplement or weaken the ledger
rules.

`main()` first captures `git status --porcelain=v1 -uall` and a recursive path/hash inventory of `archive/run-logs/v2-p0`, including hidden, ignored, and untracked files. A missing P0 root is defined as the empty inventory. It then checks: both frozen-document hashes and blobs; `docs/vibrasim2/P0_BUDGET_LEDGER.json` through the production `assert_budget_allows_run` parser; programme-authority markers; no `world` imports under `vibrasim2/p0`; safe-test auditor; default pytest; P0/V2 focused tests; README local links; package build to a temporary output directory; `git diff --check`; exact equality with `docs/vibrasim2/P0_OUTPUT_BASELINE.json`; and no P0 CLI option matching seed, threshold, timestep, source-centre, fixture, or model constants. Use `sys.executable -B -m pytest` with a temporary pytest cache and run the build into a temporary directory; after all commands, require tracked and untracked repository status to equal the captured status. Git status is not claimed to enumerate ignored files; the independent P0 tree walk is the authority for ignored scientific artifacts. A budget check that is active, over cap, arithmetically inconsistent, or bound to another registration always makes `ready_for_run_review` false.

Write the report only when `--output PATH` is explicitly supplied; otherwise print JSON to stdout. Resolve a requested report path before any command and reject it unless it is outside the repository root; it is then the sole intentional persistent write. Describe this tool as state-preserving, not read-only.

After the tool exists, add `uv run python -B tools/verify_vibrasim2_reset.py`
to the README immediately before both P0 data-creating examples. Label it
`PRE-RUN GATE — DOES NOT CREATE SCIENTIFIC DATA`, explain that it must report
`ready_for_run_review: true`, and do not claim that this check itself authorizes
a run.

Do not include the opt-in real GUI smoke as a readiness requirement. Report Windows and macOS GUI evidence separately, with an unverified platform never presented as passed.

- [ ] **Step 4: Run focused verifier tests**

Run: `uv run pytest -o addopts="-v --strict-markers" tests/vibrasim2/test_reset_verifier.py tests/test_readme_contract.py -q`

Expected: PASS.

- [ ] **Step 5: Commit the reusable verification gate**

```powershell
git add README.md tests/test_readme_contract.py tools/verify_vibrasim2_reset.py tests/vibrasim2/test_reset_verifier.py
git commit -m "chore: add Vibrasim II pre-run verification gate"
```

- [ ] **Step 6: Run the complete safe verification sequence**

Run: `uv run python tools/test_safety.py`

Expected: exit 0 and no unclassified hazards.

Run: `uv run pytest -q`

Expected: PASS for the safe default selection.

Run: `uv run pytest -o addopts="-v --strict-markers" tests/vibrasim2 tests/test_vibrasim2_*.py tests/test_readme_contract.py tests/test_repository_hygiene.py -q`

Expected: PASS for the exact P0, observer, README, and repository-hygiene paths.

Run: `uv build`

Expected: PASS.

Run: `git diff --check`

Expected: exit 0.

Run: `git status --porcelain=v1 -uall -- archive/run-logs/v2-p0`

Expected: no output.

Run: `uv run python -B tools/verify_vibrasim2_reset.py`

Expected: JSON with `"ready_for_run_review": true`, a closed within-cap budget ledger with at least 2,700 seconds remaining, an exact empty-baseline match for the P0 output tree, and unchanged repository status before/after the verifier.

- [ ] **Step 7: Stop at the two external/scientific decision gates**

Present Michael with the exact commit list, safe-test output, build output, verifier JSON, closed implementation-ledger duration and remaining hard-cap budget, known platform evidence, and remaining uncertainty. The later approved run/review procedure must append its own wall-clock intervals to the same ledger; this implementation plan opens none. Request separate concrete decisions for:

1. whether to execute the first registered P0 scientific run, with or without `--observe`;
2. whether to push the branch and, independently, what license terms to adopt.

Do not infer either decision from approval of this implementation plan. Before a public push, also request Michael's explicit editorial acceptance of the final README first-person wording.

---

## Completion Definition

Local implementation is complete only when Tasks 1 through 14 are committed locally, the machine-readable implementation ledger is closed strictly below 19,800 seconds, the safe default and focused suites pass, package construction succeeds, the pre-run verifier reports ready, no P0 data were generated, and the worktree contains no unrelated changes. This does not make the branch publication-ready by itself: final README first-person wording still needs Michael's editorial acceptance, license terms remain undecided, and a push requires separate approval. GitHub CI remains **unverified externally** until an authorized push runs it. Real GUI behavior remains **uncertainty: medium** on every target platform not practically tested.
