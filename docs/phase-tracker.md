# Phase tracker

**Plan:** [BUILD_PLAN.md](BUILD_PLAN.md)  
**As of:** 8 November 2026  
**Rule:** finish one major phase and its evidence gate before starting the next.

| Phase | Name | Target window | Status | Exit gate |
|---|---|---|---|---|
| 0 | Foundation and Windows runtime feasibility | Nov 8 | IN PROGRESS | Windows CI green; actual laptop MXC probe and host requirements recorded |
| I | Deterministic security core and Windows policy semantics | Nov 8–10 | NOT STARTED | Portable core and Windows policy tests pass on Python 3.11–3.13 |
| II | Windows sandbox, private workspace and network enforcement | Nov 10–16 | NOT STARTED | Real ProcessContainer, staging, fail-closed and network enforcement tests pass |
| III | Approvals, guarded workflows and evidence | Nov 16–18 | NOT STARTED | Approval/review/export/evidence tests pass |
| IV | Advanced verification, adversarial hardening and release | Nov 18–20 | NOT STARTED | Windows integration suite, clean install and reproducible demo pass |
| — | Stabilization | Nov 21–24 | NOT STARTED | Known-good build maintained; high-priority fixes only |
| — | Registration deadline | Nov 25 | UPCOMING | Registration complete before deadline |

## Phase 0 checklist

- [x] Confirm new repository exists and is writable.
- [x] Create Windows architecture and Linux-to-Windows porting map.
- [x] Add initial Python package/policy/audit/simulator scaffold.
- [x] Add Windows CI workflow.
- [x] Research MXC ProcessContainer and identity-scoped proxy contract.
- [x] Document sequential phases in BUILD_PLAN.md.
- [ ] Fix Ruff lint failures and format all Python files.
- [ ] Get mypy to pass.
- [ ] Get core tests to pass; record and fix failures.
- [ ] Get wheel/source distribution build and clean-install smoke test to pass.
- [ ] Run a minimal .NET 8 MXC host probe on the actual development machine.
- [ ] Record Windows edition/build, architecture, .NET version, MXC probe tier/warnings and any host-preparation requirement.
- [ ] Close Phase 0 with an evidence-backed phase log and tested commit SHA.

## Phase close-out

Each phase has a log under docs/phase-logs/ recording scope, changed files, tests/results, CI URL, tested commit SHA, host/runtime versions, security assumptions, limitations and the exit-gate result.

A failed or skipped gate leaves the phase IN PROGRESS. Later phases must not be marked complete by inference.
