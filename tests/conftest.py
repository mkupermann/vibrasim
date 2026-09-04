import socket
from pathlib import Path

import numpy as np
import pytest
from tools.test_safety import effective_exclusion_markers
from world.config import WorldConfig
from world.state import World

REPO_ROOT = Path(__file__).resolve().parent.parent
SOCKET_GUARD_MESSAGE = "network disabled in safe pytest; use --include-quarantined"
_SOCKET_ORIGINALS = None


def install_socket_guard(socket_module):
    originals = (
        socket_module.socket,
        socket_module.create_connection,
        socket_module.getaddrinfo,
    )
    original_socket = socket_module.socket

    class GuardedSocket(original_socket):
        def connect(self, address):
            raise RuntimeError(SOCKET_GUARD_MESSAGE)

        def connect_ex(self, address):
            raise RuntimeError(SOCKET_GUARD_MESSAGE)

    def blocked(*args, **kwargs):
        raise RuntimeError(SOCKET_GUARD_MESSAGE)

    socket_module.socket = GuardedSocket
    socket_module.create_connection = blocked
    socket_module.getaddrinfo = blocked
    return originals


def restore_socket_guard(socket_module, originals):
    socket_module.socket, socket_module.create_connection, socket_module.getaddrinfo = originals


def pytest_addoption(parser):
    parser.addoption(
        "--include-quarantined",
        action="store_true",
        default=False,
        help="collect tests classified as experiment, external, resource-intensive, slow, or GUI",
    )


def pytest_configure(config):
    global _SOCKET_ORIGINALS
    if not config.getoption("--include-quarantined") and _SOCKET_ORIGINALS is None:
        _SOCKET_ORIGINALS = install_socket_guard(socket)


def pytest_unconfigure(config):
    del config
    global _SOCKET_ORIGINALS
    if _SOCKET_ORIGINALS is not None:
        restore_socket_guard(socket, _SOCKET_ORIGINALS)
        _SOCKET_ORIGINALS = None


def pytest_ignore_collect(collection_path, config):
    path = Path(str(collection_path)).resolve()
    if config.getoption("--include-quarantined") or not path.name.startswith("test_"):
        return None
    if path.suffix != ".py" or REPO_ROOT not in path.parents:
        return None
    relative = path.relative_to(REPO_ROOT).as_posix()
    source_text = path.read_text(encoding="utf-8")
    return bool(effective_exclusion_markers(relative, source_text))


def pytest_itemcollected(item):
    path = Path(str(item.path)).resolve()
    if REPO_ROOT not in path.parents:
        return
    relative = path.relative_to(REPO_ROOT).as_posix()
    source_text = path.read_text(encoding="utf-8")
    for marker_name in sorted(effective_exclusion_markers(relative, source_text)):
        item.add_marker(getattr(pytest.mark, marker_name))


@pytest.fixture
def default_config() -> WorldConfig:
    return WorldConfig()


@pytest.fixture
def empty_world() -> World:
    cfg = WorldConfig(
        n_initial_vibrations=0,
        box_size=(100.0, 100.0, 100.0),
        n_vibrations_max=64,
        n_nodes_max=32,
        rng_seed=42,
    )
    return World(cfg)
