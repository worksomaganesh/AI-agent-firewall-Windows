# Windows MVP roadmap — 8 to 25 November 2026

## Milestones and checkpoints

| Dates | Workstream | Exit criteria |
|---|---|---|
| **Nov 8** | Repository bootstrap and architecture | New repo created; architecture, porting map, security boundaries and roadmap documented |
| **Nov 9–10** | Portable core migration | Policy schema/parser, policy engine baseline, audit chain, verifier and simulator imported/refactored; original Linux repo unchanged |
| **Nov 11–12** | Windows filesystem and session staging | Private workspace copy; secret exclusions; reparse-point/ADS/device-name protections; restrictive DACL; baseline/final manifests and diffs |
| **Nov 13–14** | Native process sandbox | AppContainer launch; no default network capability; Job Object assigned before resume; kill-on-close, timeout and supported resource limits; preflight fail-closed |
| **Nov 15–16** | Network enforcement | Host proxy; per-session WFP filters scoped to AppContainer SID; loopback broker exception restricted to exact proxy address/port; IPv4/IPv6 direct-connect tests |
| **Nov 17** | Human approvals and review workflow | Host-only approval, one-use scoped grants, target-state revalidation; review/export/discard |
| **Nov 18–19** | End-to-end hardening | Adversarial tests, Windows CI, packaging checks, setup guide, clean-machine smoke test, demo scenario |
| **Nov 20** | **Registration checkpoint** | Freeze a reproducible demo build and evidence pack; register using a working build, not a roadmap promise |
| **Nov 21–24** | Stabilization | Fix high-priority bugs, retest clean install, verify documentation and demo, avoid risky feature expansion |
| **Nov 25** | **Registration closes** | Confirm registration is complete; retain a tagged build and final test evidence |

Dates are planning targets, not claims that implementation or external registration has already happened.

## Registration checkpoint: minimum credible demo

By November 20, aim to demonstrate all of the following on a real Windows machine:

1. Install the project and validate a strict Windows policy.
2. Run a deterministic attack simulation with expected allow/deny/approval decisions.
3. Launch a disposable agent process in an AppContainer and Job Object against a private project copy.
4. Prove the original project is unchanged after the run.
5. Prove direct external networking is blocked; prove only the host proxy path works when network mediation is enabled.
6. Show a denied destination and an allowed destination in the audit log.
7. Verify the audit chain and inspect a workspace diff.
8. Show that failure to establish required Windows enforcement prevents the requested command from starting.

A feature is not complete because the CLI prints a success banner. Each enforcement claim requires a Windows integration test with an observed outcome.

## Priority order

**P0 — Required for a credible Windows MVP:** core policy/audit, private staging, AppContainer, Job Object, fail-closed preflight, direct-network denial, reviewable evidence, Windows CI.

**P1 — Required for the intended usable workflow:** host proxy mediation, scoped approvals, review/export/discard, install and usage documentation.

**P2 — Defer unless P0/P1 are stable:** GUI dashboard, agent-specific integrations, Windows Sandbox backend, advanced telemetry, automatic patch application, cross-platform support.

## Daily engineering loop

- Work on a dedicated feature branch; keep commits small and explainable.
- For every security change, add a regression test before marking the task complete.
- Record the tested Windows edition/build, Python version, native-host build, and relevant security settings.
- Run unit tests, Windows integration tests and package smoke tests before merging.
- Record test failures and skipped enforcement tests explicitly; skipped is not passed.
- Keep the old Linux repository unchanged and use it only as the reference implementation.

## Contingency

If WFP/loopback enforcement is not proven by the registration checkpoint, do not silently downgrade to proxy-only networking. Ship a clearly labelled offline-only execution path only if its no-network posture is proven, or defer the run feature and present the policy simulator as a simulation. Never describe simulation as OS enforcement.
