"""Static safety classification for pytest modules without importing them."""

from __future__ import annotations

import ast
import operator
from pathlib import Path

EXCLUSION_MARKERS = frozenset(
    {"experiment", "slow", "external", "resource_intensive", "gui"}
)
RESOURCE_NAMES = ("NEURON", "TICK", "STEP", "DURATION", "HOUR", "SAMPLE", "PARTICLE")
EXTERNAL_ROOTS = frozenset(
    {
        "requests",
        "httpx",
        "aiohttp",
        "urllib.request",
        "socket",
        "ftplib",
        "smtplib",
        "paramiko",
        "boto3",
        "botocore",
        "serial",
        "sounddevice",
        "pyaudio",
    }
)
EXTERNAL_CALLS = frozenset(
    {
        "os.system",
        "os.popen",
        "subprocess.run",
        "subprocess.Popen",
        "subprocess.call",
        "subprocess.check_call",
        "subprocess.check_output",
    }
)


def _numeric(node: ast.AST) -> float | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return float(node.value)
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
        value = _numeric(node.operand)
        if value is None:
            return None
        return value if isinstance(node.op, ast.UAdd) else -value
    if isinstance(node, ast.BinOp):
        left, right = _numeric(node.left), _numeric(node.right)
        if left is None or right is None:
            return None
        operation = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
        }.get(type(node.op))
        if operation is None:
            return None
        try:
            return float(operation(left, right))
        except ZeroDivisionError:
            return None
    return None


def _dotted(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent = _dotted(node.value)
        return f"{parent}.{node.attr}" if parent else None
    return None


def _aliases(tree: ast.AST) -> dict[str, str]:
    aliases: dict[str, str] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for item in node.names:
                aliases[item.asname or item.name.split(".")[0]] = item.name
        elif isinstance(node, ast.ImportFrom) and node.module:
            for item in node.names:
                aliases[item.asname or item.name] = f"{node.module}.{item.name}"
    return aliases


def _resolved_call(node: ast.Call, aliases: dict[str, str]) -> str | None:
    dotted = _dotted(node.func)
    if not dotted:
        return None
    head, separator, tail = dotted.partition(".")
    resolved = aliases.get(head, head)
    return f"{resolved}.{tail}" if separator else resolved


def detect_hazards(relative_path: str, source: str) -> frozenset[str]:
    del relative_path
    tree = ast.parse(source)
    aliases = _aliases(tree)
    hazards: set[str] = set()
    numeric_names: dict[str, float] = {}
    for node in ast.walk(tree):
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            value_node = node.value
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            value = _numeric(value_node) if value_node is not None else None
            if value is not None:
                for target in targets:
                    if isinstance(target, ast.Name):
                        numeric_names[target.id] = value
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            resolved = _resolved_call(node, aliases)
            if resolved == "pathlib.Path.home" or (
                isinstance(node.func, ast.Attribute)
                and node.func.attr == "home"
                and _dotted(node.func.value) in {"Path", "pathlib.Path"}
            ):
                hazards.add("home_output")
            if (
                isinstance(node.func, ast.Attribute)
                and node.func.attr == "expanduser"
                and not node.args
                and not node.keywords
            ):
                hazards.add("expanded_external_path")
            if resolved:
                if resolved in EXTERNAL_CALLS or any(
                    resolved == root or resolved.startswith(root + ".")
                    for root in EXTERNAL_ROOTS
                ):
                    hazards.add("external_call")
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            value_node = node.value
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            value = _numeric(value_node) if value_node is not None else None
            if value is None:
                continue
            for target in targets:
                if not isinstance(target, ast.Name):
                    continue
                name = target.id.upper()
                if "SEED" in name:
                    continue
                if value >= 1_000_000 and any(token in name for token in RESOURCE_NAMES):
                    hazards.add("large_resource")
                if value >= 3600 and any(token in name for token in ("DURATION", "HOUR")):
                    hazards.add("hour_scale_duration")
        if isinstance(node, (ast.For, ast.comprehension)):
            iterator = node.iter
            if (
                isinstance(iterator, ast.Call)
                and isinstance(iterator.func, ast.Name)
                and iterator.func.id == "range"
                and iterator.args
                and isinstance(iterator.args[-1], ast.Name)
            ):
                bound_name = iterator.args[-1].id
                bound = numeric_names.get(bound_name)
                upper_name = bound_name.upper()
                if (
                    bound is not None
                    and bound >= 1_000
                    and any(token in upper_name for token in ("TICK", "STEP", "SAMPLE"))
                ):
                    hazards.add("large_iteration")
    return frozenset(hazards)


def classify_test_source(relative_path: str, source: str) -> frozenset[str]:
    hazards = detect_hazards(relative_path, source)
    marks: set[str] = set()
    normalized = relative_path.replace("\\", "/")
    if normalized.startswith("tests/bet/"):
        marks.add("experiment")
    if normalized.endswith("_gui.py"):
        marks.add("gui")
    if hazards & {"home_output", "expanded_external_path", "external_call"}:
        marks.add("external")
    if hazards & {"large_resource", "hour_scale_duration", "large_iteration"}:
        marks.add("resource_intensive")
    return frozenset(marks)


def _literal_markers(tree: ast.AST) -> frozenset[str]:
    markers: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Attribute):
            continue
        dotted = _dotted(node)
        if dotted and dotted.startswith("pytest.mark."):
            marker = dotted.removeprefix("pytest.mark.").split(".", 1)[0]
            if marker in EXCLUSION_MARKERS:
                markers.add(marker)
    return frozenset(markers)


def effective_exclusion_markers(relative_path: str, source: str) -> frozenset[str]:
    tree = ast.parse(source)
    return classify_test_source(relative_path, source) | _literal_markers(tree)


def find_unclassified_hazards(tests_root: Path) -> list[str]:
    violations: list[str] = []
    repository_root = tests_root.resolve().parent
    for path in sorted(tests_root.rglob("test_*.py")):
        text = path.read_text(encoding="utf-8")
        relative = path.resolve().relative_to(repository_root).as_posix()
        hazards = detect_hazards(relative, text)
        if hazards and not effective_exclusion_markers(relative, text):
            violations.extend(f"{relative}: {hazard}" for hazard in sorted(hazards))
    return violations


def main() -> int:
    root = Path(__file__).resolve().parents[1] / "tests"
    violations = find_unclassified_hazards(root)
    if violations:
        print("\n".join(violations))
        return 1
    count = sum(1 for _ in root.rglob("test_*.py"))
    print(f"audited {count} modules; 0 unclassified hazards")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
