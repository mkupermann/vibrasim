from pathlib import Path
from types import SimpleNamespace

import pytest

from tools.test_safety import (
    classify_test_source,
    effective_exclusion_markers,
    find_unclassified_hazards,
)
from tests.conftest import install_socket_guard, restore_socket_guard

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


def test_thousand_step_loop_is_resource_intensive():
    marks = classify_test_source(
        "tests/test_probe.py",
        "N_TICKS = 5000\nfor tick in range(N_TICKS):\n    pass\n",
    )
    assert "resource_intensive" in marks


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


def test_literal_exclusion_mark_is_effective():
    text = "import pytest\n@pytest.mark.external\ndef test_x(): pass\n"
    assert effective_exclusion_markers("tests/test_x.py", text) == frozenset({"external"})


def test_socket_guard_replaces_and_restores_every_entrypoint():
    class Socket:
        def connect(self, address):
            return address

        def connect_ex(self, address):
            return 0

    original_create = lambda *args, **kwargs: None
    original_info = lambda *args, **kwargs: []
    namespace = SimpleNamespace(
        socket=Socket,
        create_connection=original_create,
        getaddrinfo=original_info,
    )
    originals = install_socket_guard(namespace)
    with pytest.raises(RuntimeError, match="network disabled in safe pytest"):
        namespace.socket().connect(("localhost", 1))
    with pytest.raises(RuntimeError, match="network disabled in safe pytest"):
        namespace.socket().connect_ex(("localhost", 1))
    with pytest.raises(RuntimeError, match="network disabled in safe pytest"):
        namespace.create_connection(("localhost", 1))
    with pytest.raises(RuntimeError, match="network disabled in safe pytest"):
        namespace.getaddrinfo("localhost", 1)
    restore_socket_guard(namespace, originals)
    assert namespace.socket is Socket
    assert namespace.create_connection is original_create
    assert namespace.getaddrinfo is original_info


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
