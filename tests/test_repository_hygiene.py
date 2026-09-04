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
    assert "actions/checkout@v6" in workflow
    assert "astral-sh/setup-uv@v9" in workflow
    assert "uv sync --frozen --extra dev" in workflow
    assert "uv run python tools/test_safety.py" in workflow
    assert "uv run pytest" in workflow
    assert "uv build" in workflow
    assert "git diff --check" in workflow
    assert "docker compose up" not in workflow
    assert "vibrasim2-p0 run" not in workflow
