from __future__ import annotations
from pathlib import Path
from agent_boundary.audit.events import AuditEventType, EnforcementMode
from agent_boundary.audit.logger import AuditLogger
from agent_boundary.audit.verifier import verify_audit_log

def test_audit_chain_round_trip_and_mutation_detection(tmp_path: Path) -> None:
    path = tmp_path / "audit.jsonl"
    logger = AuditLogger(path, "test-session", EnforcementMode.SIMULATION, hmac_key="synthetic-test-key")
    logger.log_event(AuditEventType.SESSION_START, {"purpose": "test"})
    logger.log_event(AuditEventType.SESSION_END, {"ok": True})
    verified = verify_audit_log(path, expected_head_hash=logger.head_hash, hmac_key="synthetic-test-key", require_hmac=True)
    assert verified.valid and verified.head_hash_anchored and verified.hmac_verified
    path.write_text(path.read_text(encoding="utf-8").replace('"ok":true', '"ok":false'), encoding="utf-8")
    assert not verify_audit_log(path, hmac_key="synthetic-test-key", require_hmac=True).valid

def test_windows_enforcement_mode_is_explicit() -> None:
    assert EnforcementMode.WINDOWS_APPCONTAINER.value == "os_enforced_windows_appcontainer"
