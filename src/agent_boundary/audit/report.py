"""Windows-neutral session report generator with explicit enforcement disclosure."""

from __future__ import annotations

import json
from pathlib import Path

from agent_boundary.audit.events import AuditEventType, AuditRecord, EnforcementMode
from agent_boundary.audit.verifier import verify_audit_log


def generate_session_report(session_dir: Path) -> str:
    """Build a readable report from a session directory's audit.jsonl."""
    audit_path = session_dir / "audit.jsonl"
    verification = verify_audit_log(audit_path)
    records: list[AuditRecord] = []
    if audit_path.exists():
        for line in audit_path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                records.append(AuditRecord.model_validate(json.loads(line)))

    session_id = records[0].session_id if records else "unknown"
    mode = records[0].enforcement_mode if records else EnforcementMode.SIMULATION
    action_rows: list[str] = []
    counts = {"allow": 0, "require_approval": 0, "deny": 0}
    for record in records:
        if record.event_type is AuditEventType.ACTION_EVALUATED:
            payload = record.payload
            decision = str(payload.get("decision", payload.get("policy_decision", "deny")))
            counts[decision] = counts.get(decision, 0) + 1
            action_rows.append(
                f"| {record.seq} | {payload.get('category', '-')}:{payload.get('operation', '-')} | "
                f"{payload.get('target', '-')} | {payload.get('normalized_target', '-')} | "
                f"**{decision.upper()}** | {payload.get('matched_rule_id', '-')} |"
            )

    sandbox_started = any(record.event_type is AuditEventType.SANDBOX_STARTED for record in records)
    if mode is EnforcementMode.SIMULATION:
        banner = (
            "> **[SIMULATION MODE — NO OS ENFORCEMENT]**\n"
            "> Policy logic was evaluated without launching an isolated Windows process."
        )
    elif sandbox_started:
        banner = "> **[WINDOWS APPContainer ENFORCEMENT — CHILD STARTED]**"
    else:
        banner = (
            "> **[WINDOWS SANDBOX NOT STARTED — TARGET COMMAND NOT RUN]**\n"
            "> Required preflight or setup failed. Do not treat this attempt as protected execution."
        )

    table_body = "\n".join(action_rows) if action_rows else "| - | - | - | - | - | - |"
    lines = [
        f"# agent-boundary Windows Session Report (`{session_id}`)",
        "",
        banner,
        "",
        "## 1. Session summary",
        "",
        f"- Enforcement mode: `{mode.value}`",
        f"- Audit records checked: {verification.records_checked}",
        f"- Audit chain integrity: **{'PASSED' if verification.valid else 'FAILED'}**",
        f"- Final audit head hash: `{verification.head_hash}`",
        f"- Decisions: {counts['allow']} allowed, {counts['require_approval']} approval-required, {counts['deny']} denied",
        "",
        "## 2. Evaluated actions",
        "",
        "| Seq | Action | Requested target | Normalized target | Decision | Rule |",
        "|---:|---|---|---|---|---|",
        table_body,
        "",
        "## 3. Security limitations",
        "",
        "- Simulation is not OS enforcement.",
        "- Proxy environment variables alone do not prevent direct-socket access.",
        "- Command and workspace adapters only mediate operations explicitly routed through them.",
        "- A local hash chain needs an independently retained head hash or protected HMAC key to detect replacement of the complete evidence bundle.",
        "- HTTPS CONNECT destinations are visible to the proxy, but encrypted TLS payloads are not inspected.",
        "",
    ]
    for warning in verification.warnings:
        lines.append(f"- Audit warning: {warning}")
    return "\n".join(lines)
