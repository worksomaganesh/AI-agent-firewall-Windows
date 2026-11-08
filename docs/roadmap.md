# Windows MVP roadmap — 8 to 25 November 2026

## Milestones and checkpoints

| Dates | Workstream | Exit criteria |
|---|---|---|
| **Nov 8** | Repository bootstrap and architecture | New repo, migration map, Windows security architecture and Python policy/audit/simulation core |
| **Nov 9–10** | MXC native-host bridge | .NET 8 sidecar builds with MXC SDK; host discovery and exact ProcessContainer request probe; unsupported hosts fail closed |
| **Nov 11–12** | Windows filesystem and staging | Private workspace copy; secret exclusions; reparse-point, ADS, device-name and traversal tests; MXC filesystem read-write/read-only/denied paths |
| **Nov 13–14** | Offline ProcessContainer execution | Real Windows 11 ProcessContainer run; process termination and timeout; original workspace unchanged; sandbox setup failure never launches target |
| **Nov 15–16** | Identity-scoped network proxy | Separate proxy AppContainer identity; proxy-only egress policy; MXC `allowedProxyPeer`; direct IPv4/IPv6 bypass tests and policy-mediated upstream tests |
| **Nov 17** | Human approvals and review workflow | Host-only one-use approvals; exact target/state revalidation; review/export/discard |
| **Nov 18–19** | End-to-end hardening | Windows adversarial suite, Windows CI, package smoke tests, setup guide and demo on a clean supported machine |
| **Nov 20** | **Registration checkpoint** | Freeze a reproducible demo build and evidence pack; register only with a working build |
| **Nov 21–24** | Stabilization | Fix high-priority defects, re-test install/demo, finalize documentation; avoid risky feature expansion |
| **Nov 25** | **Registration closes** | Confirm registration is complete and retain a tagged build plus test evidence |

Dates are targets, not claims that implementation or registration has already happened.

## Minimum credible registration demo

1. Build/install the Python package and .NET 8 MXC bridge.
2. Show host support discovery and a request-aware ProcessContainer probe.
3. Validate the strict Windows policy and run the deterministic attack simulation.
4. Launch a disposable command inside ProcessContainer against a private staged project copy.
5. Prove direct network access is denied in offline mode.
6. Demonstrate the identity-scoped proxy mode only after the proxy peer is verified and direct network bypass tests pass.
7. Show denied/allowed policy events, verify the audit chain, inspect the workspace diff, and export only after review.
8. Demonstrate that unsupported ProcessContainer requests do not fall back to an ordinary process.

A green unit-test suite is not an OS-enforcement proof. Each enforcement claim needs a Windows integration test on a recorded Windows build.

## Priorities

**P0 — Credible MVP:** policy/audit core, private staging, MXC host probe, offline ProcessContainer, fail-closed setup, original-workspace preservation, audit and diff evidence, Windows CI.

**P1 — Intended networked workflow:** identity-scoped proxy AppContainer, proxy-only egress through MXC, approvals, review/export/discard and clean installation guide.

**P2 — Defer:** GUI dashboard, agent-specific plugins, Windows Sandbox backend, advanced telemetry, automatic patch application, cross-platform support.

## Daily engineering loop

- Use a feature branch for each security-sensitive component and keep commits small.
- Add tests for normal behavior and invalid/ambiguous inputs before marking work complete.
- Record Windows edition/build, architecture, MXC SDK version, .NET runtime and native-host build.
- Run unit, Windows integration and package smoke tests before merging.
- Record failures and skipped enforcement tests explicitly; skipped is not passed.
- Keep the original Linux repository unchanged; it remains the behavioral reference.

## Contingency

If the identity-scoped proxy backend is not proven by November 20, do not silently enable direct network or identity-less proxy access. Register with a clearly labelled offline-only ProcessContainer demo if that path passes real Windows tests, or present the deterministic simulator as simulation. Never describe simulation as OS enforcement.
