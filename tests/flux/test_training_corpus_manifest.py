"""R-7 acceptance: manifest.json schema at ~/.eqmod/training/EN/.

Pre-registered in QUEUE.yaml R-7:

    "tests/flux/test_training_corpus_manifest.py PASSES (manifest written
    at ~/.eqmod/training/EN/manifest.json with: per-stage durations,
    source URLs, sha256 of each file)"

Fail-fast: every assertion that depends on non-empty stage / file lists
raises with an explicit message. No silent-pass branches.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import pytest


MANIFEST_PATH = Path.home() / ".eqmod" / "training" / "EN" / "manifest.json"

REQUIRED_STAGES = ("stage1", "stage2", "stage4_substitute")

# Stage duration floors (seconds) carried from R-6 plan thresholds.
STAGE_MIN_SECONDS = {
    "stage1": 3600,
    "stage2": 7200,
    "stage4_substitute": 1800,
}

SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


@pytest.fixture(scope="module")
def manifest() -> dict:
    assert MANIFEST_PATH.exists(), (
        f"R-7 manifest must exist at {MANIFEST_PATH}; "
        f"the R-7 fetcher did not run or did not complete"
    )
    data = json.loads(MANIFEST_PATH.read_text())
    assert isinstance(data, dict), "manifest must be a JSON object at top level"
    return data


def test_manifest_top_level(manifest: dict) -> None:
    assert manifest.get("language") == "en"
    assert manifest.get("sample_rate_hz") == 16_000
    assert manifest.get("channels") == 1
    assert isinstance(manifest.get("stages"), dict), (
        "manifest must contain a 'stages' mapping"
    )


@pytest.mark.parametrize("stage_key", REQUIRED_STAGES)
def test_manifest_stage_has_required_fields(manifest: dict, stage_key: str) -> None:
    stages = manifest["stages"]
    assert stage_key in stages, (
        f"manifest missing required stage {stage_key!r}; "
        f"found: {sorted(stages.keys())}"
    )
    stage = stages[stage_key]
    assert isinstance(stage, dict)

    files = stage.get("files")
    assert isinstance(files, list) and len(files) > 0, (
        f"manifest stage {stage_key!r} must have a non-empty 'files' list"
    )

    # Acceptance bullet: per-stage durations
    duration = stage.get("duration_seconds")
    assert isinstance(duration, (int, float)), (
        f"manifest {stage_key!r} must declare 'duration_seconds' (int/float); "
        f"got {duration!r}"
    )
    assert duration >= STAGE_MIN_SECONDS[stage_key], (
        f"manifest {stage_key!r} duration_seconds = {duration:.1f}s, "
        f"required >= {STAGE_MIN_SECONDS[stage_key]}s — verdict NULL not PASS"
    )

    for i, entry in enumerate(files):
        assert isinstance(entry, dict), f"{stage_key}.files[{i}] must be a mapping"

        # Acceptance bullet: source URLs
        source_url = entry.get("source_url")
        assert isinstance(source_url, str) and source_url, (
            f"{stage_key}.files[{i}].source_url must be a non-empty string; "
            f"got {source_url!r}"
        )

        # Acceptance bullet: sha256 of each file
        sha = entry.get("sha256")
        assert isinstance(sha, str) and SHA256_RE.match(sha), (
            f"{stage_key}.files[{i}].sha256 must be a 64-hex string; "
            f"got {sha!r}"
        )

        # Verify the path field is present (paired with sha256).
        path_str = entry.get("path")
        assert isinstance(path_str, str) and path_str, (
            f"{stage_key}.files[{i}].path must be a non-empty string"
        )
        path = Path(path_str).expanduser()
        assert path.exists(), (
            f"{stage_key}.files[{i}].path = {path} does not exist on disk"
        )

        # Per-file duration recorded.
        f_dur = entry.get("duration_seconds")
        assert isinstance(f_dur, (int, float)) and f_dur > 0, (
            f"{stage_key}.files[{i}].duration_seconds must be > 0; got {f_dur!r}"
        )


@pytest.mark.parametrize("stage_key", REQUIRED_STAGES)
def test_manifest_sha256_matches_file_content(manifest: dict, stage_key: str) -> None:
    """Every recorded sha256 must equal the live hash of the file on disk.

    This guards against a stale manifest after a swap / partial re-fetch.
    """
    stage = manifest["stages"][stage_key]
    for i, entry in enumerate(stage["files"]):
        path = Path(entry["path"]).expanduser()
        assert path.exists(), f"{stage_key}.files[{i}].path missing on disk: {path}"
        h = hashlib.sha256()
        with path.open("rb") as fh:
            for chunk in iter(lambda: fh.read(1024 * 1024), b""):
                h.update(chunk)
        assert h.hexdigest() == entry["sha256"], (
            f"{stage_key}.files[{i}] sha256 mismatch — manifest says "
            f"{entry['sha256']}, live file at {path} hashes to {h.hexdigest()} "
            f"(stale manifest, partial re-fetch, or corrupt file)"
        )


def test_manifest_total_duration_meets_combined_floor(manifest: dict) -> None:
    """Sum of stage durations must meet the combined floor (>= 12 600s)."""
    total = sum(
        manifest["stages"][k]["duration_seconds"] for k in REQUIRED_STAGES
    )
    floor = sum(STAGE_MIN_SECONDS[k] for k in REQUIRED_STAGES)
    assert total >= floor, (
        f"total corpus duration = {total:.1f}s, pre-registered floor = {floor}s"
    )
