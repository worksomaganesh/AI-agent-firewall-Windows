# Phase tracker

**Plan:** [Sequential Windows build plan](BUILD_PLAN.md)  
**As of:** 8 November 2026  
**Rule:** work on one phase at a time. Do not mark a phase complete until all its exit criteria and evidence are recorded.

| Phase | Name | Planned window | Status | Exit gate |
|---:|---|---|---|---|
| 0 | Build control, host compatibility and CI baseline | Nov 8 | IN PROGRESS | Windows CI green; local MXC probe result recorded; host requirements understood |
| 1 | Portable security core parity | Nov 8–10 | NOT STARTED | Reference behavior and portable tests pass on Windows/Python 3.11–3.13 |
| 2 | Windows policy semantics and filesystem safety primitives | Nov 9–11 | NOT STARTED | Windows path, command and network parsing adversarial tests pass |
| 3 | Private workspace staging and evidence | Nov 10–12 | NOT STARTED | Original workspace remains unchanged; unsafe filesystem fixtures fail closed |
| 4 | Windows ProcessContainer execution backend | Nov 12–14 | NOT STARTED | Real Windows sandbox run and fail-closed preflight verified |
| 5 | Network policy firewall and proxy-only egress | Nov 14–17 | NOT STARTED | Direct network bypass blocked; only identity-bound proxy route works |
| 6 | Human approvals, guarded operations and review workflow | Nov 16–18 | NOT STARTED | Approval replay/expiry/race tests and safe export tests pass |
| 7 | End-to-end adversarial validation | Nov 18–19 | NOT STARTED | Required Windows integration suite passes; no critical/high demo-path defect |
| 8 | Usable MVP, demo and registration | Nov 19–20 | NOT STARTED | Second-person setup/demo succeeds; tagged build and evidence pack; register Nov 20 |
| — | Stabilization | Nov 21–24 | NOT STARTED | Only high-priority fixes; known-good candidate retained |
| — | Registration deadline | Nov 25 | UPCOMING | Registration confirmed before deadline |

## Current phase 0 checklist

- [x] Confirm new repository exists and is writable.
- [x] Create Windows architecture and Linux-to-Windows porting map.
- [x] Add initial Python package/policy/audit/simulator scaffold.
- [x] Add Windows CI workflow.
- [x] Research MXC ProcessContainer and identity-scoped proxy contract.
- [x] Record sequential build phases in BUILD_PLAN.md.
- [ ] Fix Ruff lint failures and format all Python files.
- [ ] Get mypy to pass.
- [ ] Get core tests to pass; record failures and correct the code/tests.
- [ ] Get wheel/source distribution build and clean-install smoke test to pass.
- [ ] Run a .NET 8 MXC host probe on the actual development machine.
- [ ] Record Windows edition/build, architecture, .NET version, MXC probe tier/warnings and any host-preparation requirement.
- [ ] Close phase 0 with a concise phase log and tested commit SHA.

## Phase close-out rule

Each completed phase gets a log under docs/phase-logs/ with:
- Scope and delivered files/modules.
- Tests executed and exact results.
- CI run URL and commit SHA.
- Host/runtime versions where relevant.
- Security assumptions, limitations, and deferred work.
- Explicit exit-gate result.

A failed or skipped gate leaves the phase IN PROGRESS. Later phases must not be marked complete by inference.
