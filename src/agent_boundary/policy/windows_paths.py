"""Windows path validation and mapping into the logical /workspace policy namespace."""

from __future__ import annotations

import re

_RESERVED = {"CON", "PRN", "AUX", "NUL"} | {
    *(f"COM{i}" for i in range(1, 10)),
    *(f"LPT{i}" for i in range(1, 10)),
}
_INVALID = set('<>:"|?*')


class WindowsPathError(ValueError):
    """Raised when a path is unsafe or ambiguous for the Windows workspace."""


def normalize_workspace_relative_path(raw_path: str) -> str:
    """Return a slash-separated workspace-relative path or reject it.

    This is a lexical validation layer, not a replacement for native handle-based
    reparse-point and race checks when the Windows stager opens files.
    """
    if not isinstance(raw_path, str) or not raw_path:
        raise WindowsPathError("Workspace path must not be empty")
    if "\x00" in raw_path or any(ord(ch) < 32 for ch in raw_path):
        raise WindowsPathError("Control characters are not permitted in workspace paths")
    if raw_path.startswith(("\\\\", "//", "\\\\?\\", "\\\\.\\")):
        raise WindowsPathError("UNC and Win32 device namespace paths are not workspace-relative")
    if re.match(r"^[A-Za-z]:", raw_path):
        raise WindowsPathError("Drive-qualified paths are not workspace-relative")
    if raw_path.startswith(("/", "\\")):
        raise WindowsPathError("Rooted paths are not workspace-relative")

    normalized = raw_path.replace("\\", "/")
    parts = normalized.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        raise WindowsPathError("Empty, dot, and parent path segments are not permitted")
    for part in parts:
        if any(ch in _INVALID for ch in part):
            raise WindowsPathError(f"Invalid Windows path character in segment {part!r}")
        if part.endswith((".", " ")):
            raise WindowsPathError("Windows path segments must not end with a dot or space")
        device_base = part.split(".", 1)[0].upper()
        if device_base in _RESERVED:
            raise WindowsPathError(f"Reserved Windows device name: {part!r}")
    return "/".join(parts)


def to_policy_target(relative_path: str) -> str:
    """Map a validated Windows-relative path to the portable logical policy root."""
    normalized = normalize_workspace_relative_path(relative_path)
    return "/workspace/" + normalized
