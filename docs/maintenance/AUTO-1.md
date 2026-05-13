# AUTO-1 — Silent-pass test-pattern auditor

**Status: pre-registered. Not implemented.**
**Frozen: 2026-05-13. Author (pre-registration): Claude (autopilot setup session).**
**Reviewer at return: Michael Kupermann.**

## Why this exists

`CLAUDE.md` calls out a class of test bug:

> F3b-Test has silent-pass bug: `if n_strong_before == 0: persistence_fractions.append(1.0)` — test can never fail when no strong structures were formed.

The pattern is general: a precondition that *should* be a failure is silently rewritten as a success. The test passes; the project's pre-registration discipline is undermined; nobody notices because the test is green.

`tests/test_substrate_growth_e2e.py::test_F3b_strong_structures_persist` is currently a stub (`raise NotImplementedError`), so the specific instance does not yet exist. But the trap is real, and it will land the next time a test author writes a precondition-on-zero branch without thinking through what "zero" means.

AUTO-1 ships a generic auditor that detects this class of bug across all test files — written once, run forever as part of the test suite.

## What is built

A new test file `tests/test_audit_silent_pass.py` that:

1. Walks `tests/*.py` via `pathlib.Path` glob.
2. AST-parses each file (`ast.parse`).
3. Scans every `ast.If` node for the suspicious pattern:
   - The `If.test` is a comparison whose form is `<identifier> == 0` or `0 == <identifier>` or `len(<expr>) == 0` or `not <expr>` where `<expr>` is a list/array reference.
   - The `If.body` contains exactly one statement that calls `.append(...)` on some list, where the appended value is a "success-looking" literal: `1.0`, `True`, the string `"pass"`, or `1`.
4. Reports any match with `file:line: pattern detected`.
5. Asserts that the match list is empty, using a snapshot whitelist:
   - The whitelist file `tests/silent_pass_whitelist.txt` may contain lines of the form `path:line` for false-positives that have been audited and approved.
   - The auditor reads the whitelist on each run; matches in the whitelist do not fail the assertion.
   - If the whitelist contains a stale entry (path+line no longer exists, or no longer matches the pattern), the auditor fails. Whitelist must stay tight.

A second test in the same file is a meta-meta-test: it loads two synthetic fixture files (under `tests/fixtures/silent_pass/`) — one with a known silent-pass instance, one clean — and asserts the auditor correctly flags the bad one and clears the clean one.

## Acceptance — pre-registered

Test target: `tests/test_audit_silent_pass.py`. The autopilot session implements this file.

All three pytest items below must hold for AUTO-1 to be marked **passed**. The postflight script reads these from `QUEUE.yaml` and runs them.

1. `tests/test_audit_silent_pass.py::test_auditor_finds_silent_pass_in_fixture PASSES`: the auditor flags `tests/fixtures/silent_pass/bad_example.py:N` where the silent-pass pattern is deliberately written.
2. `tests/test_audit_silent_pass.py::test_auditor_clears_clean_fixture PASSES`: the auditor does NOT flag `tests/fixtures/silent_pass/clean_example.py`, which contains a precondition that correctly raises `pytest.fail()`.
3. `tests/test_audit_silent_pass.py::test_auditor_scans_real_test_suite PASSES`: the auditor runs against `tests/test_*.py` (excluding `test_audit_silent_pass.py` and `tests/fixtures/`), and either reports zero matches OR every match is in the whitelist. The whitelist must be empty or contain only entries with a 1-line `# justified: <reason>` comment on the preceding line.

## Negative control

Conceptually, the silent-pass auditor IS the negative control for the project's testing discipline. A separate matched-wallclock no-engram run is not meaningful — this is a static analysis pass over source files, not a substrate experiment. The negative control is built into acceptance item 1: the auditor must flag a deliberately broken fixture. If it can't, it's a state detector, not a meaningful audit.

## What this does NOT claim

- Does not detect every possible bad test. The pattern is narrow by design (compare-to-zero + append-success). False-negatives are expected and fine — Michael writes the test, he sees the test, the auditor catches the one specific trap that already burned us once.
- Does not modify any substrate or test code outside its own fixture files. The auditor is read-only.
- Does not require any subscription, network, or external dependency.

## Implementation hints (for the autopilot)

- AST primitives: `ast.parse(source)`, walk via `ast.walk`, isinstance checks for `ast.If`, `ast.Compare`, `ast.Eq`, `ast.Num` / `ast.Constant`.
- The fixture files MUST be under `tests/fixtures/silent_pass/` and MUST NOT be picked up by pytest collection — name them with a leading underscore (`_bad_example.py`, `_clean_example.py`) so pytest skips them, OR add a `conftest.py` in that fixture dir with `collect_ignore = ["bad_example.py", "clean_example.py"]`.
- Keep the auditor fast: <5 seconds for the full repo scan. Cache nothing; read each file once.
- Do not use regex on source. Use AST. Regex on Python is the trap this very item exists to prevent another instance of.

## Out of scope for AUTO-1

- Detection of other anti-patterns (e.g., `assert True`, no-op tests, swallowed exceptions). Future autopilot items may extend the same auditor file; AUTO-1 ships the silent-pass detector only.
- Modifying the existing F3b stub. That work belongs to Plan A Task 10 and is gated on substrate performance, not on the auditor.

## Budget

- **Realistic**: 1 day of session work (one autopilot tick should complete it).
- **Hard ceiling**: 3 attempts × 4h each = 12h compute. If not passed after 3 attempts, AUTO-1 is `failed` and Michael reviews on return.

## What FAILED looks like

- The auditor either misses a deliberate silent-pass fixture, OR
- The auditor false-positives on legitimate test code that the whitelist cannot reasonably suppress, OR
- The auditor breaks pytest collection of the rest of the suite.

Any of these → `null` after attempt 1, `null` again at attempt 2, `failed` at attempt 3. Postmortem appended to LOGBOOK.md by the Opus path.
