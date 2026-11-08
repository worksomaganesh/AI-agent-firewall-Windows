from __future__ import annotations
import pytest
from agent_boundary.policy.windows_paths import WindowsPathError, normalize_workspace_relative_path, to_policy_target

@pytest.mark.parametrize(("raw", "expected"), [
    (r"src\main.py", "src/main.py"),
    (r"config\agent.yaml", "config/agent.yaml"),
    ("README.md", "README.md"),
])
def test_normalize_windows_relative_path(raw: str, expected: str) -> None:
    assert normalize_workspace_relative_path(raw) == expected

@pytest.mark.parametrize("raw", [
    "", r"..\outside.txt", r"src\..\outside.txt", r"C:\Users\user\secret.txt",
    r"\\server\share\file.txt", r"\\?\C:\device.txt",
    "folder\file.txt:secret-stream", "NUL.txt", "folder\trailing. ", "bad<name>.txt",
])
def test_unsafe_windows_paths_rejected(raw: str) -> None:
    with pytest.raises(WindowsPathError):
        normalize_workspace_relative_path(raw)

def test_policy_target_uses_logical_workspace_root() -> None:
    assert to_policy_target(r"src\main.py") == "/workspace/src/main.py"
