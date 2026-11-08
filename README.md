# AI Agent Firewall for Windows

**A Windows-first local security supervisor for AI coding agents.**

This repository is the Windows-native implementation of ideas explored in the [original Linux-first project](https://github.com/worksomaganesh/ai-agent-firewall). It is a separate codebase: Linux-specific enforcement is not copied or presented as Windows security.

> [!WARNING]
> **Development status: architecture and repository bootstrap.** Windows OS enforcement is not implemented or validated yet. Do not use this repository as a security boundary until the Windows backend, adversarial tests, and release checks are complete.

## Goal

Run a local AI coding agent against a private staged copy of a developer's project while enforcing least-privilege Windows isolation, mediating supported network requests, requiring explicit approval for sensitive mediated actions, and producing reviewable evidence.

The security principle is simple: **a prompt is not a security boundary.**

## Planned Windows architecture

- **Python control plane:** CLI, strict YAML policy validation, deterministic policy decisions, audit evidence, simulation, reports, and workspace review.
- **Windows native host:** a small native helper for AppContainer process creation, Windows Job Objects, ACL management, and WFP session filters.
- **AppContainer:** a low-privilege identity with only explicitly granted access; network capabilities are not granted to the agent.
- **Job Objects:** process-tree lifetime and supported resource limits.
- **Windows Filtering Platform:** restrict the sandbox identity to the host policy proxy when network mediation is enabled.
- **Host policy proxy:** resolves destinations, applies host/port policy, rejects unsafe address ranges, and records network decisions.
- **Private workspace copy:** the original project is not the agent's working directory; changes are reviewed and exported separately.

See:
- [Windows architecture](docs/architecture/windows-architecture.md)
- [Linux-to-Windows porting map](docs/architecture/porting-map.md)
- [Build roadmap: 8–25 November 2026](docs/roadmap.md)
- [Security policy and disclosure](SECURITY.md)

## Planned operator workflow

The intended CLI commands are policy validation, deterministic simulation, sandboxed run, session review, and audit verification. They will become available as implementation milestones land.

## Security boundaries and limitations

The first target is **Windows 11 x64**. Windows 10, ARM64, Windows Sandbox integration, and broader host configurations will be marked supported only after separate validation.

AppContainer is an OS-enforced process isolation mechanism, not a separate Hyper-V virtual machine. Job Objects do not by themselves mediate every command a child process starts. Network access is considered enforced only when preflight confirms the per-session WFP restrictions and proxy path are active. If required enforcement cannot be established, the requested agent command must not start.

This project is an educational/hackathon prototype until it receives independent security review. A green test suite is evidence for tested cases, not proof of complete security.

## Development target

- Start: 8 November 2026
- Planned registration checkpoint: 20 November 2026
- Registration closes: 25 November 2026

The roadmap prioritizes a demonstrable, test-backed Windows MVP before registration and stability work afterwards.
