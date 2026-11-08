from __future__ import annotations

import pytest

from agent_boundary.policy.engine import ActionRequest, PolicyEngine
from agent_boundary.policy.parser import PolicyValidationError, load_policy_from_text
from agent_boundary.policy.schema import Decision

POLICY = """
schema_version: "1.0"
policy_id: "test-policy"
description: "Test policy."
workspace_root: "/workspace"
default_decision: "deny"
filesystem:
  deny:
    - id: "deny-secret"
      operations: ["read", "write", "delete"]
      paths: ["**/.env"]
      reason: "Secrets denied."
  require_approval:
    - id: "approve-delete"
      operations: ["delete"]
      paths: ["/workspace/**"]
      reason: "Deletion requires approval."
  allow:
    - id: "allow-workspace"
      operations: ["read", "write"]
      paths: ["/workspace/**"]
      reason: "Workspace source allowed."
commands:
  deny:
    - id: "deny-force"
      executables: ["git.exe", "git"]
      arg_patterns: ["*push*--force*"]
      reason: "Force push denied."
  require_approval:
    - id: "approve-reset"
      executables: ["git.exe", "git"]
      arg_patterns: ["reset*--hard*"]
      reason: "Hard reset requires approval."
network:
  allow:
    - id: "allow-api"
      hosts: ["api.example.com"]
      ports: [443]
      reason: "Test API allowed."
"""

def test_duplicate_yaml_keys_fail_closed() -> None:
    with pytest.raises(PolicyValidationError, match="Duplicate YAML key"):
        load_policy_from_text('schema_version: "1.0"\nschema_version: "1.0"')

def test_unknown_policy_fields_fail_closed() -> None:
    with pytest.raises(PolicyValidationError, match="Policy schema validation failed"):
        load_policy_from_text(POLICY.replace('description: "Test policy."', 'description: "Test policy."\nunknown: true'))

def test_explicit_deny_overrides_allow() -> None:
    result = PolicyEngine(load_policy_from_text(POLICY)).evaluate(ActionRequest("filesystem", "read", "/workspace/.env"))
    assert result.decision is Decision.DENY
    assert result.matched_rule_id == "deny-secret"

def test_default_deny_on_unmatched_network() -> None:
    result = PolicyEngine(load_policy_from_text(POLICY)).evaluate(ActionRequest("network", "connect", "evil.example.com:443"))
    assert result.decision is Decision.DENY

def test_workspace_delete_requires_approval() -> None:
    result = PolicyEngine(load_policy_from_text(POLICY)).evaluate(ActionRequest("filesystem", "delete", "/workspace/src/main.py"))
    assert result.decision is Decision.REQUIRE_APPROVAL

def test_windows_executable_extension_matches_policy_stem() -> None:
    result = PolicyEngine(load_policy_from_text(POLICY)).evaluate(ActionRequest("command", "exec", r"C:\Program Files\Git\git.exe push --force origin main"))
    assert result.decision is Decision.DENY
