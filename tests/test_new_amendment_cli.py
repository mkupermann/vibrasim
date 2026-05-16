"""Tests for the amendment-scaffolding CLI (tools/new_amendment.py).

Spec reference: docs/amendments/G20-G23.md §8.

The CLI itself is infrastructure and ships with real (non-skipped) tests.
This is distinct from the amendment test skeletons it generates, which are
deliberately skipped until the amendment is implemented.
"""
from __future__ import annotations

import importlib
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from tools import new_amendment


# ---------------------------------------------------------------------------
# Unit-level: id normalisation and slugification
# ---------------------------------------------------------------------------

def test_normalise_id_accepts_canonical():
    assert new_amendment._normalise_id("G21") == "G21"
    assert new_amendment._normalise_id("g21") == "G21"


def test_normalise_id_accepts_prime():
    assert new_amendment._normalise_id("G21-prime") == "G21-prime"
    assert new_amendment._normalise_id("g21-prime") == "G21-prime"
    assert new_amendment._normalise_id("G21′") == "G21-prime"


def test_normalise_id_rejects_garbage():
    for bad in ["", "21", "GG21", "G", "G21x", "G21-foo"]:
        with pytest.raises(ValueError):
            new_amendment._normalise_id(bad)


def test_slugify_handles_punctuation():
    assert new_amendment._slugify("Single-letter `a` round-trip") == "single-letter-a-round-trip"
    assert new_amendment._slugify("G21") == "g21"
    assert new_amendment._slugify("   ") == "amendment"


# ---------------------------------------------------------------------------
# Integration: invoke CLI against an isolated copy of the repo
# ---------------------------------------------------------------------------

@pytest.fixture
def isolated_repo(tmp_path, monkeypatch):
    """Make a minimal repo copy under tmp_path, point the CLI at it, return paths."""
    repo = tmp_path / "EQMOD"
    repo.mkdir()
    (repo / "docs").mkdir()
    (repo / "docs" / "amendments").mkdir()
    (repo / "tests").mkdir()

    # Minimal README with the status table the CLI patches.
    readme = repo / "README.md"
    readme.write_text(
        "# EQMOD\n\n"
        "Stub README for tests.\n\n"
        "## What runs today\n\n"
        "| Phase | Mechanism | Status |\n"
        "|---|---|---|\n"
        "| Phase 1 | Vibration → atom | Reproduces from session3 |\n"
        "| G17 | Autonomous loop | Passing |\n"
        "\n"
        "## Other sections\n\n"
        "After-table content.\n",
        encoding="utf-8",
    )

    # Point the CLI's module-level paths at this isolated repo.
    monkeypatch.setattr(new_amendment, "REPO_ROOT", repo)
    monkeypatch.setattr(new_amendment, "DOCS_AMENDMENTS", repo / "docs" / "amendments")
    monkeypatch.setattr(new_amendment, "TESTS_DIR", repo / "tests")
    monkeypatch.setattr(new_amendment, "README_PATH", readme)
    monkeypatch.setattr(new_amendment, "MARKER_PROTOCOL_DIR", repo / "docs")
    return repo


def test_scaffold_writes_all_four_files(isolated_repo, capsys):
    rc = new_amendment.main(["G99", "--title", "Test amendment"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "WROTE" in out

    repo = isolated_repo
    assert (repo / "docs" / "amendments" / "G99.md").exists()
    assert (repo / "docs" / "amendments" / "G99-postmortem.md").exists()
    assert (repo / "docs" / "marker_protocol_G99_addendum.md").exists()

    # Test file slug derives from title.
    test_files = list((repo / "tests").glob("test_amendment_G99_*.py"))
    assert len(test_files) == 1
    assert test_files[0].name == "test_amendment_G99_test-amendment.py"


def test_scaffold_inserts_readme_row(isolated_repo):
    new_amendment.main(["G99", "--title", "Test amendment"])
    readme = (isolated_repo / "README.md").read_text(encoding="utf-8")
    assert "**G99**" in readme
    assert "Test amendment" in readme
    assert "PRE-REGISTERED" in readme
    # Row landed inside the status table, before "## Other sections".
    idx_row = readme.index("**G99**")
    idx_other = readme.index("## Other sections")
    assert idx_row < idx_other


def test_scaffold_readme_insertion_is_idempotent(isolated_repo):
    new_amendment.main(["G99", "--title", "Test amendment"])
    readme_first = (isolated_repo / "README.md").read_text(encoding="utf-8")
    # Re-run with --force so the file writes don't block; README must NOT
    # gain a second row.
    new_amendment.main(["G99", "--title", "Test amendment", "--force"])
    readme_second = (isolated_repo / "README.md").read_text(encoding="utf-8")
    assert readme_first.count("**G99**") == 1
    assert readme_second.count("**G99**") == 1


def test_scaffold_refuses_overwrite_without_force(isolated_repo, capsys):
    rc1 = new_amendment.main(["G99", "--title", "First"])
    assert rc1 == 0
    rc2 = new_amendment.main(["G99", "--title", "Second"])
    assert rc2 == 2
    err = capsys.readouterr().err
    assert "already exist" in err


def test_scaffold_force_overwrites_non_failed(isolated_repo):
    new_amendment.main(["G99", "--title", "First"])
    spec = isolated_repo / "docs" / "amendments" / "G99.md"
    assert "First" in spec.read_text(encoding="utf-8")
    rc = new_amendment.main(["G99", "--title", "Second", "--force"])
    assert rc == 0
    assert "Second" in spec.read_text(encoding="utf-8")


def test_scaffold_refuses_to_overwrite_failed_even_with_force(isolated_repo, capsys):
    """The retry rule (docs/amendments/G20-G23.md §2.6) makes FAILED specs
    permanent. A retry must use a new id (e.g. G99-prime)."""
    new_amendment.main(["G99", "--title", "First"])
    spec = isolated_repo / "docs" / "amendments" / "G99.md"
    text = spec.read_text(encoding="utf-8")
    # Flip the status to FAILED to simulate a sealed FAILED amendment.
    text = text.replace("**Status: PRE-REGISTERED", "**Status: FAILED")
    spec.write_text(text, encoding="utf-8")

    rc = new_amendment.main(["G99", "--title", "Second", "--force"])
    assert rc == 3
    err = capsys.readouterr().err
    assert "FAILED" in err
    assert "prime" in err  # nudges the user toward the retry id pattern


def test_retry_of_renders_retry_line(isolated_repo):
    new_amendment.main([
        "G99-prime", "--title", "Retry of G99",
        "--retry-of", "G99",
    ])
    spec = (isolated_repo / "docs" / "amendments" / "G99-prime.md").read_text(encoding="utf-8")
    assert "Retry of: G99" in spec
    assert "G99-postmortem.md" in spec


def test_dry_run_writes_nothing(isolated_repo, capsys):
    rc = new_amendment.main(["G99", "--title", "Test amendment", "--dry-run"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "[dry-run]" in out
    assert not (isolated_repo / "docs" / "amendments" / "G99.md").exists()
    assert not (isolated_repo / "tests" / "test_amendment_G99_test-amendment.py").exists()
    readme = (isolated_repo / "README.md").read_text(encoding="utf-8")
    assert "**G99**" not in readme


def test_generated_test_file_is_syntactically_valid(isolated_repo):
    new_amendment.main(["G99", "--title", "Test amendment"])
    test_path = isolated_repo / "tests" / "test_amendment_G99_test-amendment.py"
    code = test_path.read_text(encoding="utf-8")
    # py_compile would write a pyc; ast.parse is enough.
    import ast
    ast.parse(code)


def test_generated_test_file_uses_pytest_skip(isolated_repo):
    """The skeleton tests must be SKIPPED, not silently passing — otherwise
    a fresh amendment would appear to PASS before implementation."""
    new_amendment.main(["G99", "--title", "Test amendment"])
    test_path = isolated_repo / "tests" / "test_amendment_G99_test-amendment.py"
    code = test_path.read_text(encoding="utf-8")
    assert "@pytest.mark.skip" in code
    assert "not yet implemented" in code


def test_spec_contains_required_sections(isolated_repo):
    new_amendment.main(["G99", "--title", "Test amendment"])
    spec = (isolated_repo / "docs" / "amendments" / "G99.md").read_text(encoding="utf-8")
    for header in ["## 1. Background", "## 3. Acceptance", "## 4. Budget",
                   "## 5. Negative control", "## 6. Out of scope"]:
        assert header in spec, f"missing section: {header}"


def test_marker_addendum_contains_acceptance_table(isolated_repo):
    new_amendment.main(["G99", "--title", "Test amendment"])
    addendum = (isolated_repo / "docs" / "marker_protocol_G99_addendum.md").read_text(encoding="utf-8")
    assert "## G99 acceptance" in addendum
    assert "| PASS |" in addendum
    assert "| NULL |" in addendum
    assert "| FAIL |" in addendum
    assert "Negative control" in addendum
    assert "Retry record" in addendum
