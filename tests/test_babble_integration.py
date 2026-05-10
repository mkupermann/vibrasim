"""Integration tests for ``agent/run_babble_experiment.py`` (iter-5b).

THIS IS THE PIPELINE-CONTRACT TEST for the predictive-babble build.
It exercises the full mini-mode path that the autonomous-build's success
contract gates on:

    Contract = `python -m agent.run_babble_experiment --mini`
               produces 4 wav files in ``~/.eqmod/babble/mini/``
               AND tests/test_babble_integration.py exits 0.

Each test calls ``run_mini`` against its own ``tmp_path`` so the tests
do not collide with each other or with the real ``~/.eqmod`` dir on the
developer's machine.

No silent-pass paths: every conditional uses ``pytest.fail`` on the
unreachable branch, mirroring the iteration-4b/5a tests
(cf. project memory's F3b silent-pass class of bugs).
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from unittest import mock

import numpy as np
import pytest
import scipy.io.wavfile

from agent.evaluate_babble import EvaluationResult
from agent.run_babble_experiment import SUBSTRATE_NAMES, run_mini


# ---------------------------------------------------------------------
# 1. Four wav files exist and are readable.


def test_run_mini_produces_4_wav_files(tmp_path: Path) -> None:
    out_dir = tmp_path / "mini"
    run_mini(out_dir=out_dir)

    if len(SUBSTRATE_NAMES) != 4:
        pytest.fail(
            f"SUBSTRATE_NAMES has {len(SUBSTRATE_NAMES)} entries, "
            "expected 4 (trained_de + 3 controls)"
        )

    for name in SUBSTRATE_NAMES:
        wav_path = out_dir / name / "babble.wav"
        if not wav_path.exists():
            pytest.fail(f"missing wav file at {wav_path}")
        sr, data = scipy.io.wavfile.read(str(wav_path))
        if sr != 16000:
            pytest.fail(f"{name}: wav sample rate is {sr}, expected 16000")
        if data.size == 0:
            pytest.fail(f"{name}: wav has zero samples")
        duration_s = float(data.shape[0] / sr)
        # Mini runs target 1.0 sec; ISTFT padding can shave a few
        # samples — accept >= 0.9 sec.
        if duration_s < 0.9:
            pytest.fail(
                f"{name}: wav duration {duration_s:.3f}s is below "
                "the 0.9s minimum (target 1.0s)"
            )


# ---------------------------------------------------------------------
# 2. result.json is well-formed.


def test_run_mini_writes_result_json(tmp_path: Path) -> None:
    out_dir = tmp_path / "mini"
    run_mini(out_dir=out_dir)

    result_path = out_dir / "result.json"
    if not result_path.exists():
        pytest.fail(f"result.json missing at {result_path}")

    parsed = json.loads(result_path.read_text())
    for key in ("verdict", "trained_kl_mean", "control_kl", "z_scores"):
        if key not in parsed:
            pytest.fail(f"result.json missing top-level key {key!r}")

    if parsed["verdict"] not in ("PASS", "FAIL", "NULL"):
        pytest.fail(
            f"result.json verdict is {parsed['verdict']!r}, "
            "expected one of PASS/FAIL/NULL"
        )
    if not isinstance(parsed["control_kl"], dict):
        pytest.fail(
            f"control_kl must be a dict; got {type(parsed['control_kl'])}"
        )
    if not isinstance(parsed["z_scores"], dict):
        pytest.fail(
            f"z_scores must be a dict; got {type(parsed['z_scores'])}"
        )


# ---------------------------------------------------------------------
# 3. Return type is EvaluationResult with a valid verdict.


def test_run_mini_returns_evaluation_result(tmp_path: Path) -> None:
    out_dir = tmp_path / "mini"
    result = run_mini(out_dir=out_dir)

    if not isinstance(result, EvaluationResult):
        pytest.fail(
            f"run_mini returned {type(result).__name__}, "
            "expected EvaluationResult"
        )
    if result.verdict not in ("PASS", "FAIL", "NULL"):
        pytest.fail(
            f"verdict is {result.verdict!r}, expected PASS/FAIL/NULL"
        )
    # n_bootstrap mirrors the run_mini default (20). If it changes here
    # without the spec moving, the test informs the developer.
    if result.n_bootstrap <= 0:
        pytest.fail(
            f"n_bootstrap is {result.n_bootstrap}, expected positive"
        )


# ---------------------------------------------------------------------
# 4. Mini mode does not call CorpusBuilder (offline contract).


def test_run_mini_does_not_block_on_network(tmp_path: Path) -> None:
    """If mini mode hits the network, the developer running pytest in
    a CI sandbox or on a flight will see a hang. The contract is
    explicit per the iteration-5b brief: mini mode is offline.

    We patch ``agent.corpus_builder.CorpusBuilder`` to raise on any
    instantiation. ``run_mini`` must complete without hitting it.
    """
    out_dir = tmp_path / "mini"
    with mock.patch(
        "agent.corpus_builder.CorpusBuilder",
        side_effect=AssertionError(
            "CorpusBuilder must not be invoked from --mini mode"
        ),
    ):
        # If the patched class is touched, the AssertionError surfaces.
        run_mini(out_dir=out_dir)

    # Sanity: we still produced the 4 wavs (i.e. the test is not
    # silently passing because run_mini bailed before doing work).
    for name in SUBSTRATE_NAMES:
        wav_path = out_dir / name / "babble.wav"
        if not wav_path.exists():
            pytest.fail(
                f"run_mini under CorpusBuilder mock did not write "
                f"{wav_path} — mini mode might be silently degrading"
            )


# ---------------------------------------------------------------------
# 5. Wall-clock under 60 seconds.


def test_run_mini_completes_in_under_60_seconds(tmp_path: Path) -> None:
    """Pipeline correctness, not a scientific evaluation. If this
    fails, mini mode is doing too much."""
    out_dir = tmp_path / "mini"
    start = time.time()
    run_mini(out_dir=out_dir)
    elapsed = time.time() - start

    if elapsed >= 60.0:
        pytest.fail(
            f"run_mini took {elapsed:.1f}s, exceeded the 60s budget "
            "for the integration-test contract"
        )
    # The fast-path check: explicitly confirm the wavs are present
    # so a silent-fail (run_mini returns early without writing) does
    # not slip past this test.
    for name in SUBSTRATE_NAMES:
        wav_path = out_dir / name / "babble.wav"
        if not wav_path.exists():
            pytest.fail(
                f"run_mini completed in {elapsed:.1f}s but did not "
                f"write {wav_path} — early-exit silent-fail"
            )
