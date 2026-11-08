# Windows project roadmap — November 2026

The authoritative sequential implementation plan is [docs/BUILD_PLAN.md](BUILD_PLAN.md). The phase states are maintained in [docs/phase-tracker.md](phase-tracker.md).

| Date | Target |
|---|---|
| **Nov 8** | Phase 0: repository/build control, fix Windows CI baseline, verify MXC host feasibility |
| **Nov 8–10** | Phase I: deterministic policy/audit/simulation core and Windows-specific policy semantics |
| **Nov 10–16** | Phase II: private workspace staging, MXC ProcessContainer execution, offline and proxy-only network enforcement |
| **Nov 16–18** | Phase III: trusted approvals, guarded adapters, complete audit/snapshot/review/export workflow |
| **Nov 18–20** | Phase IV: adversarial Windows validation, clean install, reproducible demo and registration |
| **Nov 20** | Planned registration checkpoint |
| **Nov 21–24** | Stabilization; high-priority fixes only |
| **Nov 25** | Registration hard deadline |

Dates are targets, not claims that implementation is complete or registration has happened. Every phase must pass its exit gate before the next major phase is started. A skipped Windows enforcement test is not a pass.
