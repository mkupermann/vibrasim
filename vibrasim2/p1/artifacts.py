"""Canonical single-artifact persistence for P1."""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .audit import AuditResult
from .registration import P0_INPUT_DIGEST, P1_DESIGN_SHA256


class ArtifactError(RuntimeError):
    """Raised when a P1 artifact cannot be written or verified."""


def _canonical(value: Any) -> bytes:
    try:
        return json.dumps(
            value, sort_keys=True, separators=(",", ":"), allow_nan=False
        ).encode("utf-8")
    except (TypeError, ValueError) as error:
        raise ArtifactError("P1 result is not canonical JSON") from error


def _payload(result: AuditResult) -> dict[str, Any]:
    sources = json.loads(_canonical(asdict(result)["sources"]))
    return {
        "schema_version": 1,
        "registration_sha256": P1_DESIGN_SHA256,
        "p0_input_scientific_digest": P0_INPUT_DIGEST,
        "outcome": result.outcome.value,
        "reasons": list(result.reasons),
        "sources": sources,
    }


def _digest(payload: dict[str, Any]) -> str:
    return hashlib.sha256(_canonical(payload)).hexdigest()


def write_audit(output_dir: str | Path, result: AuditResult) -> str:
    root = Path(output_dir)
    payload = _payload(result)
    digest = _digest(payload)
    value = {**payload, "audit_digest": digest}
    try:
        root.mkdir(parents=True, exist_ok=False)
        target = root / "audit.json"
        temporary = root / ".audit.json.tmp"
        temporary.write_bytes(_canonical(value) + b"\n")
        os.replace(temporary, target)
    except OSError as error:
        raise ArtifactError(f"cannot atomically write P1 audit: {root}") from error
    verified = read_verified_audit(root)
    if verified != value:
        raise ArtifactError("P1 audit readback mismatch")
    return digest


def read_verified_audit(output_dir: str | Path) -> dict[str, Any]:
    path = Path(output_dir) / "audit.json"
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError) as error:
        raise ArtifactError(f"cannot read P1 audit: {path}") from error
    if not isinstance(value, dict) or not isinstance(value.get("audit_digest"), str):
        raise ArtifactError("P1 audit digest is missing")
    recorded = value["audit_digest"]
    payload = {key: item for key, item in value.items() if key != "audit_digest"}
    if _digest(payload) != recorded:
        raise ArtifactError("P1 audit digest mismatch")
    return value
