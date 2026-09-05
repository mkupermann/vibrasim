# V2-P1 Mechanism Audit Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a deterministic, read-only audit that classifies the existing P0 topology traces without rerunning or reinterpreting P0.

**Architecture:** A new `vibrasim2.p1` package separates registration, trace loading, pure measurement, ordered classification, artifact persistence, and CLI orchestration. The CLI validates the frozen P0 digest and an empty confined output path before analysis, writes one canonical `audit.json`, then verifies its content digest. P1 never imports the P0 simulator or viewer.

**Tech Stack:** Python 3.13, NumPy, pytest, stdlib argparse/json/hashlib/pathlib.

**Spec:** `docs/superpowers/specs/2026-09-04-v2-p1-mechanism-audit-design.md`

## Global Constraints

- P0 remains `NULL`; P1 has diagnostic outcomes only.
- Input scientific digest is exactly `bdf94735ba80fb719ac7f8e5c78b75705f706b9e5d8a179f09c199b6d838826e`.
- P1 reads existing `energy.jsonl` records only and never calls a simulator or viewer.
- Required sources are `(4,16)`, `(16,4)`, and `(4,4)` at `dt=0.05` and `dt=0.025` for CYCLE and BRANCH.
- Correlation search is restricted to integer lags covering `[-10,+10]` simulation time units.
- Strict diagnostic boundaries remain `0.02`, `0.01`, `0.10`, and `0.05` exactly as specified.
- Implementation plus review has a hard wall-clock ceiling of 18,000 seconds; every interval is recorded honestly in `docs/vibrasim2/P1_BUDGET_LEDGER.json`.
- Existing `uv.lock` changes and untracked P0 raw data are user state and must not be modified or committed accidentally.

---

### Task 1: Registration identity and budget guard

**Files:**
- Create: `vibrasim2/p1/__init__.py`
- Create: `vibrasim2/p1/registration.py`
- Create: `vibrasim2/p1/budget.py`
- Create: `tests/vibrasim2/test_p1_registration.py`
- Create: `tests/vibrasim2/test_p1_budget.py`
- Modify: `tests/vibrasim2/test_program_authority.py`

**Interfaces:**
- Consumes: the committed design document and `docs/vibrasim2/P1_BUDGET_LEDGER.json`.
- Produces: `P1_DESIGN_SHA256`, `P0_INPUT_DIGEST`, `P1_BUDGET_PATH`, `start_p1_interval(...)`, `finish_p1_interval(...)`, and `assert_p1_budget_allows_audit(...)`.

- [ ] **Step 1: Write failing authority and budget tests**

```python
def test_p1_design_identity_is_current():
    assert sha256(canonical_lf_bytes(P1_DESIGN_PATH)).hexdigest() == P1_DESIGN_SHA256

def test_p1_budget_rejects_elapsed_ceiling(tmp_path):
    ledger = valid_p1_ledger(hard_ceiling_seconds=10, cumulative_elapsed_seconds=10)
    path = write_ledger(tmp_path, ledger)
    with pytest.raises(P1BudgetError, match="hard ceiling"):
        assert_p1_budget_allows_audit(path, repository_root=tmp_path)

def test_p1_budget_rejects_design_digest_mismatch(tmp_path):
    ledger = valid_p1_ledger(registration_sha256="0" * 64)
    path = write_ledger(tmp_path, ledger)
    with pytest.raises(P1BudgetError, match="registration"):
        assert_p1_budget_allows_audit(path, repository_root=tmp_path)
```

- [ ] **Step 2: Run the new tests and verify RED**

Run: `.venv\\Scripts\\python.exe -m pytest tests/vibrasim2/test_p1_registration.py tests/vibrasim2/test_p1_budget.py tests/vibrasim2/test_program_authority.py -q`

Expected: collection fails because `vibrasim2.p1.registration` and `vibrasim2.p1.budget` do not exist.

- [ ] **Step 3: Implement immutable registration constants and lease-based budget accounting**

```python
P1_DESIGN_PATH = Path("docs/superpowers/specs/2026-09-04-v2-p1-mechanism-audit-design.md")
P1_DESIGN_SHA256 = "5276f7fb81b257ef865d4aad9dbdee5712e7dc3a26b3ca354dc030422a3438d8"
P0_INPUT_DIGEST = "bdf94735ba80fb719ac7f8e5c78b75705f706b9e5d8a179f09c199b6d838826e"
P1_BUDGET_PATH = Path("docs/vibrasim2/P1_BUDGET_LEDGER.json")
P1_OUTPUT_ROOT = Path("archive/run-logs/v2-p1")
```

Use frozen `P1BudgetLease(started_at_utc, phase, owner, registration_sha256)` records. Reject an open interval, mismatched registration digest, negative or inconsistent elapsed time, a cumulative value at or above 18,000 seconds, and any unrecognized phase. Use ceiling-rounded elapsed seconds and atomic ledger replacement.

- [ ] **Step 4: Run registration and budget tests and verify GREEN**

Run: `.venv\\Scripts\\python.exe -m pytest tests/vibrasim2/test_p1_registration.py tests/vibrasim2/test_p1_budget.py tests/vibrasim2/test_program_authority.py -q`

Expected: all tests pass.

- [ ] **Step 5: Commit Task 1 without unrelated files**

```text
git add vibrasim2/p1/__init__.py vibrasim2/p1/registration.py vibrasim2/p1/budget.py tests/vibrasim2/test_p1_registration.py tests/vibrasim2/test_p1_budget.py tests/vibrasim2/test_program_authority.py docs/vibrasim2/P1_BUDGET_LEDGER.json
git commit -m "feat(v2-p1): bind audit registration and budget"
```

---

### Task 2: Pure trace metrics

**Files:**
- Create: `vibrasim2/p1/types.py`
- Create: `vibrasim2/p1/metrics.py`
- Create: `tests/vibrasim2/test_p1_metrics.py`

**Interfaces:**
- Consumes: immutable NumPy float64 time and matter-ratio arrays.
- Produces: `Trace`, `TraceMetrics`, `PairMetrics`, `measure_pair(cycle, branch, max_lag_time)`.

- [ ] **Step 1: Write failing hand-calculated metric tests**

```python
def test_measure_pair_reports_signed_and_rms_contrast():
    cycle = Trace(times=np.array([0., 1., 2.]), values=np.array([0., 3., 0.]))
    branch = Trace(times=np.array([0., 1., 2.]), values=np.array([0., 1., 0.]))
    measured = measure_pair(cycle, branch, max_lag_time=1.0)
    assert measured.signed_peak_contrast == 2.0
    assert measured.max_abs_contrast == 2.0
    assert measured.rms_contrast == pytest.approx(np.sqrt(4.0 / 3.0))
    assert measured.max_abs_time == 1.0
    assert measured.max_abs_sign == 1

def test_cross_correlation_tie_prefers_absolute_then_negative_lag():
    cycle = Trace(times=np.arange(4, dtype=float), values=np.array([1., -1., 1., -1.]))
    branch = Trace(times=np.arange(4, dtype=float), values=np.array([-1., 1., -1., 1.]))
    measured = measure_pair(cycle, branch, max_lag_time=2.0)
    assert measured.best_lag == -1.0

def test_zero_variance_trace_is_invalid():
    flat = Trace(times=np.arange(3, dtype=float), values=np.ones(3))
    with pytest.raises(MetricError, match="zero variance"):
        measure_pair(flat, flat, max_lag_time=1.0)
```

- [ ] **Step 2: Run metric tests and verify RED**

Run: `.venv\\Scripts\\python.exe -m pytest tests/vibrasim2/test_p1_metrics.py -q`

Expected: collection fails because `vibrasim2.p1.metrics` does not exist.

- [ ] **Step 3: Implement the minimal pure metric layer**

```python
@dataclass(frozen=True)
class Trace:
    times: np.ndarray
    values: np.ndarray

@dataclass(frozen=True)
class PairMetrics:
    signed_peak_contrast: float
    max_abs_contrast: float
    rms_contrast: float
    max_abs_time: float
    max_abs_sign: int
    cycle_peak_time: float
    branch_peak_time: float
    best_lag: float
    zero_lag_correlation: float
    best_lag_correlation: float
```

Validate one-dimensional equal-length finite arrays, strictly increasing uniform timestamps, equal timestamps between arms, and nonzero demeaned norms. At every candidate lag correlate only the overlapping samples. Rank correlation candidates by `(-correlation, abs(lag_steps), lag_steps)` so equal correlations choose the smaller absolute lag and then the negative lag.

- [ ] **Step 4: Run metric and full P0 tests and verify GREEN**

Run: `.venv\\Scripts\\python.exe -m pytest tests/vibrasim2/test_p1_metrics.py tests/vibrasim2/test_p0_energy.py -q`

Expected: all tests pass.

- [ ] **Step 5: Commit Task 2**

```text
git add vibrasim2/p1/types.py vibrasim2/p1/metrics.py tests/vibrasim2/test_p1_metrics.py
git commit -m "feat(v2-p1): add frozen trace measurements"
```

---

### Task 3: P0 artifact loading and integrity gates

**Files:**
- Create: `vibrasim2/p1/input.py`
- Create: `tests/vibrasim2/test_p1_input.py`

**Interfaces:**
- Consumes: `Path` to the fixed P0 run, the declared digest in `result.json`, and `vibrasim2.p0.artifacts.iter_energy_records`.
- Produces: `load_registered_pairs(p0_root: Path) -> tuple[SourcePairs, ...]` and `InputValidationError`.

- [ ] **Step 1: Write failing loader and integrity tests**

```python
def test_loader_rejects_wrong_scientific_digest(p0_fixture):
    p0_fixture.result["scientific_digest"] = "0" * 64
    with pytest.raises(InputValidationError, match="digest"):
        load_registered_pairs(p0_fixture.root)

def test_loader_recomputes_p0_peaks(p0_fixture):
    pairs = load_registered_pairs(p0_fixture.root)
    assert len(pairs) == 3
    assert pairs[0].coarse.cycle.values.max() == pytest.approx(
        p0_fixture.result_a_b("primary-full-cycle-x4-y16-dt0.05"), abs=1e-12
    )

def test_loader_does_not_import_simulation_entry_points(monkeypatch, p0_fixture):
    monkeypatch.setitem(sys.modules, "vibrasim2.p0.dynamics", ExplodingModule())
    assert len(load_registered_pairs(p0_fixture.root)) == 3
```

- [ ] **Step 2: Run loader tests and verify RED**

Run: `.venv\\Scripts\\python.exe -m pytest tests/vibrasim2/test_p1_input.py -q`

Expected: collection fails because `vibrasim2.p1.input` does not exist.

- [ ] **Step 3: Implement exact registered-cell selection**

Map only these slug families: `primary-full-{cycle,branch}-xX-yY-dt0.05` and `convergence-full-{cycle,branch}-xX-yY-dt0.025`. Build `m(t)` from each record's `h_matter / first.h_total`. Require ticks `0..2000` for coarse and `0..4000` for convergence, exact physical timestamps, finite values, and `A_B` equality to the fixed result within `1e-12`. Downsample convergence by taking every second record for cross-resolution comparison; do not interpolate.

- [ ] **Step 4: Run input, metric, and P0 artifact tests and verify GREEN**

Run: `.venv\\Scripts\\python.exe -m pytest tests/vibrasim2/test_p1_input.py tests/vibrasim2/test_p1_metrics.py tests/vibrasim2/test_p0_artifacts.py -q`

Expected: all tests pass.

- [ ] **Step 5: Commit Task 3**

```text
git add vibrasim2/p1/input.py tests/vibrasim2/test_p1_input.py
git commit -m "feat(v2-p1): validate fixed P0 trace input"
```

---

### Task 4: Ordered audit classification

**Files:**
- Create: `vibrasim2/p1/audit.py`
- Create: `tests/vibrasim2/test_p1_audit.py`

**Interfaces:**
- Consumes: three `SourceAudit` values containing coarse and convergence `PairMetrics`.
- Produces: `AuditOutcome`, `AuditResult`, `classify_audit(sources)`, and `audit_registered_run(p0_root)`.

- [ ] **Step 1: Write failing tests for all ordered outcomes and boundaries**

```python
@pytest.mark.parametrize("outcome", list(AuditOutcome))
def test_ordered_outcomes(outcome, audit_fixture_for):
    assert classify_audit(audit_fixture_for(outcome)).outcome is outcome

def test_exact_candidate_boundary_is_unresolved():
    sources = three_valid_sources(max_abs=0.02, rms=0.01, lag=0.10, gain=0.05)
    assert classify_audit(sources).outcome is AuditOutcome.UNRESOLVED

def test_integrity_failure_precedes_candidate():
    sources = list(three_valid_sources(max_abs=0.03, rms=0.02, lag=0.20, gain=0.10))
    first = sources[0]
    sources[0] = replace(
        first,
        convergence=replace(
            first.convergence,
            max_abs_contrast=first.coarse.max_abs_contrast + 0.002,
        ),
    )
    assert classify_audit(tuple(sources)).outcome is AuditOutcome.INVALID
```

- [ ] **Step 2: Run audit tests and verify RED**

Run: `.venv\\Scripts\\python.exe -m pytest tests/vibrasim2/test_p1_audit.py -q`

Expected: collection fails because `vibrasim2.p1.audit` does not exist.

- [ ] **Step 3: Implement the ordered decision table literally**

```python
class AuditOutcome(str, Enum):
    INVALID = "INVALID"
    TIME_STRUCTURE_CANDIDATE = "TIME_STRUCTURE_CANDIDATE"
    WEAK_CHANNEL = "WEAK_CHANNEL"
    UNRESOLVED = "UNRESOLVED"

def classify_audit(sources: tuple[SourceAudit, ...]) -> AuditResult:
    if not all(source.integrity_holds for source in sources):
        return AuditResult(AuditOutcome.INVALID, sources)
    candidates = sum(source.is_time_structure_candidate for source in sources)
    if candidates >= 2:
        return AuditResult(AuditOutcome.TIME_STRUCTURE_CANDIDATE, sources)
    if all(source.convergence.max_abs_contrast < 0.01 for source in sources):
        return AuditResult(AuditOutcome.WEAK_CHANNEL, sources)
    return AuditResult(AuditOutcome.UNRESOLVED, sources)
```

- [ ] **Step 4: Run audit tests and verify GREEN**

Run: `.venv\\Scripts\\python.exe -m pytest tests/vibrasim2/test_p1_audit.py tests/vibrasim2/test_p1_metrics.py tests/vibrasim2/test_p1_input.py -q`

Expected: all tests pass.

- [ ] **Step 5: Commit Task 4**

```text
git add vibrasim2/p1/audit.py tests/vibrasim2/test_p1_audit.py
git commit -m "feat(v2-p1): classify mechanism audit"
```

---

### Task 5: Canonical artifact and guarded CLI

**Files:**
- Create: `vibrasim2/p1/artifacts.py`
- Create: `vibrasim2/p1/cli.py`
- Create: `tests/vibrasim2/test_p1_artifacts.py`
- Create: `tests/vibrasim2/test_p1_cli.py`
- Modify: `pyproject.toml`

**Interfaces:**
- Consumes: `audit_registered_run`, P1 budget guard, one fixed P0 input directory, and one nonexistent direct child of `archive/run-logs/v2-p1`.
- Produces: `write_audit(output_dir, result) -> str`, `read_verified_audit(output_dir)`, and console command `vibrasim2-p1 audit --input-dir ... --output-dir ...`.

- [ ] **Step 1: Write failing artifact and CLI tests**

```python
from unittest.mock import Mock

def test_audit_json_is_byte_deterministic(tmp_path, audit_result):
    left = write_audit(tmp_path / "left", audit_result)
    right = write_audit(tmp_path / "right", audit_result)
    assert left == right
    assert (tmp_path / "left" / "audit.json").read_bytes() == (
        tmp_path / "right" / "audit.json"
    ).read_bytes()

def test_cli_rejects_existing_output_before_analysis(tmp_path, monkeypatch):
    output = tmp_path / "existing"
    output.mkdir()
    audit = Mock(side_effect=AssertionError("analysis must not start"))
    monkeypatch.setattr("vibrasim2.p1.cli.audit_registered_run", audit)
    assert main(["audit", "--input-dir", "p0", "--output-dir", str(output)]) == 1
    audit.assert_not_called()

def test_cli_prints_diagnostic_outcome(tmp_path, registered_fixture, monkeypatch):
    output_root = tmp_path / "v2-p1"
    output_root.mkdir()
    monkeypatch.setattr("vibrasim2.p1.cli.P1_OUTPUT_ROOT", output_root)
    code = main(["audit", "--input-dir", str(registered_fixture),
                 "--output-dir", str(output_root / "audit-001")])
    assert code == 0
```

- [ ] **Step 2: Run artifact and CLI tests and verify RED**

Run: `.venv\\Scripts\\python.exe -m pytest tests/vibrasim2/test_p1_artifacts.py tests/vibrasim2/test_p1_cli.py -q`

Expected: collection fails because the modules and entry point do not exist.

- [ ] **Step 3: Implement atomic canonical output and non-bypassable CLI**

Serialize with `json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)` plus one LF. Compute `audit_digest` over the same payload without its own digest field, write to a same-directory temporary file, `os.replace`, read back, recompute, and reject mismatches. Resolve paths, reject symlinks/junctions in every output-root component, require an absent direct child of the fixed output root, acquire a `scientific_audit` lease before analysis, and close it on every exit path.

Add:

```toml
vibrasim2-p1 = "vibrasim2.p1.cli:main"
```

- [ ] **Step 4: Run CLI, artifact, and all P1 tests and verify GREEN**

Run: `.venv\\Scripts\\python.exe -m pytest tests/vibrasim2/test_p1_registration.py tests/vibrasim2/test_p1_budget.py tests/vibrasim2/test_p1_metrics.py tests/vibrasim2/test_p1_input.py tests/vibrasim2/test_p1_audit.py tests/vibrasim2/test_p1_artifacts.py tests/vibrasim2/test_p1_cli.py -q`

Expected: all tests pass and no scientific P1 output exists.

- [ ] **Step 5: Commit Task 5**

```text
git add vibrasim2/p1/artifacts.py vibrasim2/p1/cli.py tests/vibrasim2/test_p1_artifacts.py tests/vibrasim2/test_p1_cli.py pyproject.toml
git commit -m "feat(v2-p1): add guarded audit command"
```

---

### Task 6: Independent verification and run gate

**Files:**
- Modify only if verification reveals a tested defect: the narrow file and its corresponding test.

**Interfaces:**
- Consumes: all committed P1 implementation tasks.
- Produces: evidence that implementation is ready for a separately approved real audit.

- [ ] **Step 1: Verify P1 and P0 suites**

Run: `.venv\\Scripts\\python.exe -m pytest tests/vibrasim2 -q`

Expected: all non-GUI, non-experiment tests pass; only an already documented privilege-dependent Windows symlink test may skip.

- [ ] **Step 2: Verify formatting and repository boundaries**

Run: `git diff --check`

Expected: no output.

Run: `git status --short`

Expected: only pre-existing `uv.lock` and local P0 raw-data paths remain outside committed P1 work.

- [ ] **Step 3: Verify the run guard without analyzing P0**

Run: `.venv\\Scripts\\python.exe -m vibrasim2.p1.cli audit --help`

Expected: help names exactly `--input-dir` and `--output-dir`; no simulation or observer option exists.

- [ ] **Step 4: Stop before the real audit**

Do not execute `vibrasim2-p1 audit` against `2026-09-04-observed-001`. Report implementation commits, test evidence, remaining budget, and the exact proposed output directory. The real audit requires Michael's explicit approval after this checkpoint.
