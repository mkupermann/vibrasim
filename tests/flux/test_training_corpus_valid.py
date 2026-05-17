"""R-7 acceptance: corpus YAML validity + on-disk audio assets.

Pre-registered in QUEUE.yaml R-7:

    "tests/flux/test_training_corpus_valid.py PASSES (corpus YAML at
    corpus.training-EN.yaml exists, parses, all listed audio assets exist
    on disk, total Stage 1 duration >= 60 min, total Stage 2 duration >=
    120 min, sample-rate normalised to 16 kHz mono)"

Source-class / acoustic-distinction commitments from the R-6 plan
(docs/superpowers/plans/2026-05-17-flux-training-EN.md) are out of scope
for this test by design — the QUEUE.yaml acceptance is the contract.

Fail-fast: every assertion that depends on a non-empty stage / non-empty
file list raises with an explicit message. There is no
`if not_present: assert True` branch. (Charter §F3b-silent-pass rule.)
"""
from __future__ import annotations

from pathlib import Path

import pytest
import soundfile as sf
import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
CORPUS_YAML_PATH = REPO_ROOT / "corpus.training-EN.yaml"

# Floors carried verbatim from the QUEUE.yaml acceptance.
STAGE1_MIN_SECONDS = 60 * 60
STAGE2_MIN_SECONDS = 120 * 60

EXPECTED_SAMPLE_RATE_HZ = 16_000
EXPECTED_CHANNELS = 1


@pytest.fixture(scope="module")
def corpus_yaml() -> dict:
    assert CORPUS_YAML_PATH.exists(), (
        f"corpus.training-EN.yaml must exist at {CORPUS_YAML_PATH}; "
        f"R-7 has not produced the manifest yet"
    )
    text = CORPUS_YAML_PATH.read_text()
    data = yaml.safe_load(text)
    assert isinstance(data, dict), (
        f"corpus.training-EN.yaml must parse as a YAML mapping at top level; "
        f"got {type(data).__name__}"
    )
    return data


def _resolve_path(p: str) -> Path:
    path = Path(p).expanduser()
    if not path.is_absolute():
        path = REPO_ROOT / path
    return path


def test_corpus_yaml_top_level_schema(corpus_yaml: dict) -> None:
    assert corpus_yaml.get("language") == "en", (
        f"corpus.training-EN.yaml must declare language: en; "
        f"got {corpus_yaml.get('language')!r}"
    )
    assert corpus_yaml.get("sample_rate_hz") == EXPECTED_SAMPLE_RATE_HZ, (
        f"corpus.training-EN.yaml must declare sample_rate_hz: 16000; "
        f"got {corpus_yaml.get('sample_rate_hz')!r}"
    )
    assert corpus_yaml.get("channels") == EXPECTED_CHANNELS, (
        f"corpus.training-EN.yaml must declare channels: 1 (mono); "
        f"got {corpus_yaml.get('channels')!r}"
    )
    stages = corpus_yaml.get("stages")
    assert isinstance(stages, dict), (
        "corpus.training-EN.yaml must declare a 'stages' mapping"
    )
    for required_stage in ("stage1", "stage2", "stage4_substitute"):
        assert required_stage in stages, (
            f"corpus.training-EN.yaml is missing required stage {required_stage!r}; "
            f"found stages: {sorted(stages.keys())}"
        )


@pytest.mark.parametrize(
    "stage_key,min_seconds",
    [
        ("stage1", STAGE1_MIN_SECONDS),
        ("stage2", STAGE2_MIN_SECONDS),
    ],
    ids=["stage1>=60min", "stage2>=120min"],
)
def test_stage_files_exist_and_meet_duration_floor(
    corpus_yaml: dict, stage_key: str, min_seconds: int
) -> None:
    stage = corpus_yaml["stages"][stage_key]
    files = stage.get("files")
    assert isinstance(files, list) and len(files) > 0, (
        f"{stage_key}.files must be a non-empty list of fetched audio assets; "
        f"got {files!r} (R-7 fetcher likely did not run or wrote no files)"
    )

    total_seconds = 0.0
    for i, entry in enumerate(files):
        assert isinstance(entry, dict), (
            f"{stage_key}.files[{i}] must be a mapping with at least 'path'"
        )
        path_str = entry.get("path")
        assert isinstance(path_str, str) and path_str, (
            f"{stage_key}.files[{i}].path must be a non-empty string; "
            f"got {path_str!r}"
        )
        path = _resolve_path(path_str)
        assert path.exists(), (
            f"{stage_key}.files[{i}].path points at {path}, which does not "
            f"exist on disk — the YAML references a missing audio asset"
        )

        info = sf.info(str(path))
        assert info.samplerate == EXPECTED_SAMPLE_RATE_HZ, (
            f"{stage_key}.files[{i}] at {path} has sample_rate={info.samplerate}; "
            f"required {EXPECTED_SAMPLE_RATE_HZ} Hz"
        )
        assert info.channels == EXPECTED_CHANNELS, (
            f"{stage_key}.files[{i}] at {path} has channels={info.channels}; "
            f"required {EXPECTED_CHANNELS} (mono)"
        )
        assert info.frames > 0, (
            f"{stage_key}.files[{i}] at {path} has zero audio frames"
        )
        total_seconds += info.frames / info.samplerate

    assert total_seconds >= min_seconds, (
        f"{stage_key} total duration = {total_seconds:.1f}s, "
        f"pre-registered floor is {min_seconds}s "
        f"({min_seconds/60:.0f} min) — verdict NULL, not PASS"
    )


def test_stage4_substitute_present_with_files(corpus_yaml: dict) -> None:
    """Stage 4 substitute is listed in the R-6 plan and acceptance bullets.

    The duration floor (>= 30 min) is enforced via the R-6 plan's
    corpus_stage4_seconds_min = 1800 to keep R-7 honest about the substitute
    actually being present. Even though the QUEUE.yaml line only mentions
    Stage 1 and Stage 2 floors, the manifest also needs to record Stage 4.
    """
    stage4 = corpus_yaml["stages"].get("stage4_substitute")
    assert isinstance(stage4, dict), (
        "stage4_substitute must be a mapping (MIT OCW or fallback substitute)"
    )
    files = stage4.get("files")
    assert isinstance(files, list) and len(files) > 0, (
        "stage4_substitute.files must be a non-empty list — the Stage 4 "
        "substitute is part of the R-6 plan and must exist on disk"
    )
    total_seconds = 0.0
    for entry in files:
        path = _resolve_path(entry["path"])
        assert path.exists(), f"stage4_substitute file missing: {path}"
        info = sf.info(str(path))
        assert info.samplerate == EXPECTED_SAMPLE_RATE_HZ
        assert info.channels == EXPECTED_CHANNELS
        total_seconds += info.frames / info.samplerate
    assert total_seconds >= 1800, (
        f"stage4_substitute total duration = {total_seconds:.1f}s, "
        f"required >= 1800s (30 min) per R-6 plan"
    )
