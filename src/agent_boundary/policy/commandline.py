"""Fail-closed Windows command-line tokenizer for policy evaluation.

This parses a Windows-style command line only. It never invokes a shell.
The launcher will still use an explicit executable plus argv sequence.
"""

from __future__ import annotations


class CommandLineError(ValueError):
    """Raised when a command line is empty or ambiguously quoted."""


def split_windows_command_line(command_line: str) -> list[str]:
    """Split according to Windows backslash-before-quote rules.

    The tokenizer is intentionally conservative: an unmatched quote is rejected.
    Callers should prefer an argv sequence at the process-launch boundary.
    """
    if not isinstance(command_line, str) or not command_line.strip():
        raise CommandLineError("Command line must not be empty")
    if "\x00" in command_line:
        raise CommandLineError("NUL is not permitted in a command line")

    args: list[str] = []
    i = 0
    n = len(command_line)
    while i < n:
        while i < n and command_line[i] in " \t\r\n":
            i += 1
        if i >= n:
            break

        arg: list[str] = []
        in_quotes = False
        started = False
        while i < n:
            if command_line[i] in " \t\r\n" and not in_quotes:
                break

            slash_count = 0
            while i < n and command_line[i] == "\\":
                slash_count += 1
                i += 1

            if i < n and command_line[i] == '"':
                arg.extend("\\" for _ in range(slash_count // 2))
                if slash_count % 2:
                    arg.append('"')
                    i += 1
                else:
                    in_quotes = not in_quotes
                    i += 1
                started = True
                continue

            arg.extend("\\" for _ in range(slash_count))
            if i < n and (in_quotes or command_line[i] not in " \t\r\n"):
                arg.append(command_line[i])
                i += 1
                started = True
            elif slash_count:
                started = True
            else:
                break

        if in_quotes:
            raise CommandLineError("Unmatched double quote in command line")
        if started:
            args.append("".join(arg))
        while i < n and command_line[i] in " \t\r\n":
            i += 1

    if not args or not args[0]:
        raise CommandLineError("Executable name must not be empty")
    return args
