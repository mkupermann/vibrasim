import json

import pytest

from vibrasim2.p1.artifacts import ArtifactError, read_verified_audit, write_audit
from vibrasim2.p1.audit import AuditOutcome, AuditResult


def test_audit_json_is_byte_deterministic(tmp_path):
    result = AuditResult(AuditOutcome.INVALID, (), ("zero variance trace",))
    left = write_audit(tmp_path / "left", result)
    right = write_audit(tmp_path / "right", result)
    assert left == right
    assert (tmp_path / "left" / "audit.json").read_bytes() == (
        tmp_path / "right" / "audit.json"
    ).read_bytes()


def test_readback_rejects_tampered_payload(tmp_path):
    output = tmp_path / "audit"
    write_audit(output, AuditResult(AuditOutcome.UNRESOLVED, ()))
    value = json.loads((output / "audit.json").read_text(encoding="utf-8"))
    value["outcome"] = "WEAK_CHANNEL"
    (output / "audit.json").write_text(json.dumps(value), encoding="utf-8")
    with pytest.raises(ArtifactError, match="digest"):
        read_verified_audit(output)
