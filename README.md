# AI Agent Firewall for Windows

**A Windows-first local security supervisor for AI coding agents.**

This is a separate Windows-native codebase based on the architecture of the [original Linux-first project](https://github.com/worksomaganesh/ai-agent-firewall). It does not copy Bubblewrap or pretend Linux enforcement works on Windows.

> [!WARNING]
> **Development status: portable policy/audit core implemented; Windows containment integration in progress.** No agent process should be considered protected by this repository until the MXC ProcessContainer host bridge and real Windows enforcement tests are complete.

## Goal

Run an AI coding agent against a private staged copy of a project, constrain its filesystem and network access using Windows OS-enforced controls, require explicit approval for sensitive mediated actions, and produce reviewable evidence.

**A prompt is not a security boundary.**

## Windows architecture

- **Python control plane:** CLI, strict YAML policy, deterministic evaluation, approval state, workspace staging, audit chain, simulation and reports.
- **Microsoft Execution Containers (MXC):** use the official .NET SDK to create Windows ProcessContainer sessions. MXC owns the low-level Windows containment implementation, runtime capability probing, filesystem policy, and Windows network filters.
- **.NET 8 native-host bridge:** a small sidecar uses `Microsoft.Mxc.Sdk` v1.0.1 to probe the current machine and launch a ProcessContainer request. The bridge must refuse unsupported requests rather than silently run a normal process.
- **Host policy proxy:** the separate network broker evaluates the existing domain/port policy and resolves destinations. Proxy-only egress must use an identity-scoped AppContainer/package peer; a plain proxy environment variable is not a security boundary.
- **Private workspace copy:** the original project is not the agent's writable working directory. Changes are reviewed and exported separately.

Read the [Windows architecture](docs/architecture/windows-architecture.md), [Linux-to-Windows porting map](docs/architecture/porting-map.md), [build roadmap](docs/roadmap.md), and [security policy](SECURITY.md).

## Current implementation

<badge color="success">Implemented</badge> Strict policy schema/parser, policy evaluation, Windows command tokenizer, lexical Windows path validation, hash-chained audit records, simulator, Windows CLI core, example policy/scenario, and Windows CI workflow.

<badge color="warning">In progress</badge> MXC .NET bridge, Windows staging/ACL integration, identity-scoped proxy service, session runner, approvals and review/export.

There is intentionally no working `run` command yet. The CLI currently validates and evaluates policies, simulates attacks, verifies audit chains, and generates reports. Simulation is never presented as OS enforcement.

## Host requirements

The planned native backend uses Windows ProcessContainer through MXC. MXC documents Windows 11 24H2 or later for ProcessContainer; the exact tier and requested policy support must be verified on the host at runtime. The .NET host bridge targets .NET 8 and references the official `Microsoft.Mxc.Sdk` NuGet package.

A host that cannot satisfy the requested containment/network policy must not launch the agent.

## Planned operator workflow

1. Install Python package and build the .NET host bridge.
2. Run host capability discovery and the request-specific ProcessContainer probe.
3. Validate the Windows policy and simulate the attack suite.
4. Stage a project copy and launch only after the Windows backend confirms the requested restrictions.
5. Review the staged diff, verify the audit chain, then explicitly export or discard.

## Development checkpoints

- Start: 8 November 2026
- Registration checkpoint: 20 November 2026
- Registration closes: 25 November 2026

The registration checkpoint is a target, not a claim that the Windows enforcement backend is already complete.
