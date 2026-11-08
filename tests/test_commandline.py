from __future__ import annotations

import pytest

from agent_boundary.policy.commandline import CommandLineError, split_windows_command_line


@pytest.mark.parametrize(("raw", "expected"), [
    ("agent.exe --flag value", ["agent.exe", "--flag", "value"]),
    ('"C:\\Program Files\\Agent\\agent.exe" --workspace "C:\\My Projects\\demo"', ["C:\\Program Files\\Agent\\agent.exe", "--workspace", "C:\\My Projects\\demo"]),
    ('agent.exe "" tail', ["agent.exe", "", "tail"]),
    ('agent.exe "a b" c', ["agent.exe", "a b", "c"]),
    (r'agent.exe a\"b', ["agent.exe", 'a"b']),
])
def test_split_windows_command_line(raw: str, expected: list[str]) -> None:
    assert split_windows_command_line(raw) == expected

@pytest.mark.parametrize("raw", ["", "   ", 'agent.exe "unterminated', "agent.exe\x00bad"])
def test_invalid_command_lines_fail_closed(raw: str) -> None:
    with pytest.raises(CommandLineError):
        split_windows_command_line(raw)
