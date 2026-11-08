# Phase 0 — Build control, host compatibility and CI baseline

**Date opened:** 8 November 2026  
**Status:** IN PROGRESS  
**Plan:** [BUILD_PLAN.md](../BUILD_PLAN.md)

## Completed

- Confirmed the Windows repository is public, has a main branch, and is writable.
- Established a separate Windows-first project rather than mutating the Linux reference.
- Added architecture, porting map, security policy, package metadata and dated roadmap.
- Added the initial Python policy/parser/engine/audit/simulator/CLI scaffold and Windows-focused starter tests.
- Added a Windows GitHub Actions matrix for Python 3.11, 3.12 and 3.13.
- Identified Microsoft Execution Containers (MXC) ProcessContainer as the preferred Windows containment integration candidate, subject to exact host/request probe results.
- Documented identity-scoped proxy-only egress as the secure networked execution design; identity-less host-loopback proxy access is not an automatic fallback.

## CI findings

The first CI run installed the Python package and development dependencies on Windows runners, then stopped at Ruff lint. Because lint failed, mypy, pytest, and distribution checks were skipped. A later lint retry still reported five import-formatting issues. The phase is therefore not complete.

The observed lint errors are recorded here as a current blocker, not hidden as a passed check.

## Pending

- Resolve all Ruff errors.
- Run mypy and fix its findings.
- Run the full portable suite and correct failures, including command-line quoting and Windows path cases.
- Build and smoke-test wheel and source distributions.
- Build/run a minimal .NET 8 MXC probe on the actual development laptop.
- Record host compatibility diagnostics and any administrator-approved preparation needed.
- Re-run the full Windows CI matrix after final corrections.

## Evidence

- Repository: https://github.com/worksomaganesh/AI-agent-firewall-Windows
- Build plan: https://github.com/worksomaganesh/AI-agent-firewall-Windows/blob/main/docs/BUILD_PLAN.md
- CI workflow: https://github.com/worksomaganesh/AI-agent-firewall-Windows/actions/workflows/windows-ci.yml
- Latest known lint failure log: https://github.com/worksomaganesh/AI-agent-firewall-Windows/actions/runs/42447970771
- Phase 0 exit gate: NOT MET
