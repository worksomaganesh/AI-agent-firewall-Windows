# Windows Build Plan — Phase-by-Phase Execution

**Project:** AI Agent Firewall for Windows  
**Reference implementation:** https://github.com/worksomaganesh/ai-agent-firewall  
**Windows implementation:** https://github.com/worksomaganesh/AI-agent-firewall-Windows  
**Plan date:** 8 November 2026  
**Target registration date:** 20 November 2026  
**Hard registration deadline:** 25 November 2026

---

## 1. Mission and product boundary

Build a practical Windows-native security supervisor for AI coding agents. An agent should work in a private project copy, have only the resources the operator grants, use a policy-mediated network path when enabled, require human approval for explicitly mediated sensitive operations, and leave behind verifiable evidence and a reviewable diff.

The Windows repository is a separate implementation. The Linux repository is our architecture, behavior, and test reference—not a source of Linux enforcement code to be renamed.

### Product guarantees we intend to prove

1. Strict policy parsing: duplicate YAML keys, unknown fields, malformed input, and unknown actions fail closed.
2. Deterministic decisions: DENY > REQUIRE_APPROVAL > ALLOW > DEFAULT DENY.
3. The agent cannot modify the original project; it works only in a private staged copy.
4. Required Windows isolation is established before the requested process starts. No silent unsandboxed fallback.
5. Network is denied by default. Networked execution is permitted only when the exact proxy-only policy and identity binding are enforced and tested.
6. Human approvals are exact-target, short-lived, one-use, host-side, and revalidated immediately before the mediated operation.
7. Each session produces an audit chain, baseline/final manifests, a diff, and a report.
8. Security claims describe only tested enforcement. Simulation and policy evaluation are never described as OS enforcement.

The first release is a focused local developer tool, not a GUI dashboard, enterprise endpoint product, universal command interceptor, or independently certified security product.

---

## 2. Architecture and technology choices

### Control plane

- Python 3.11+ package and Typer CLI.
- Pydantic policy schema and strict YAML parser.
- Portable policy engine, deterministic simulator, hash-chained audit log, verifier and report generator.
- Windows-specific path/command normalization, workspace staging, approval and review/export workflows.

### Windows execution boundary

**MXC ProcessContainer is the preferred integration candidate**, using the official .NET SDK. It avoids us writing a custom AppContainer/WFP implementation before we have evidence that the supported Windows APIs and host environment can meet the project requirements.

- Native bridge: .NET 8 console sidecar.
- SDK baseline to evaluate: `Microsoft.Mxc.Sdk` 1.0.1; pin the exact package after the host proof-of-concept.
- Required preflight: platform support, available ProcessContainer backend, request-specific probe, selected isolation tier, warnings and errors.
- Filesystem policy: explicit read-only/read-write/denied paths on the private staged workspace.
- Network: offline/default-deny first; proxy-only mode only with the MXC-supported identity-scoped proxy peer and exact loopback endpoint.
- Any host preparation that requires administrator approval remains an explicit operator step. The product must not elevate itself or change host security settings silently.

MXC's public docs state Windows 11 24H2 or later with a supported ProcessContainer environment and .NET 8 or later. OS version alone does not establish feature availability. The runtime/request probe is a hard gate. Some hosts need one-time system/null-device preparation, which must be approved by an administrator. Review the official [quickstart](https://learn.microsoft.com/en-us/windows/apps/develop/mxc/quickstart), [platform support](https://learn.microsoft.com/en-us/windows/apps/develop/mxc/platform-support), [networking contract](https://github.com/microsoft/mxc/blob/v1.0.1/docs/backends/process-container/networking.md), and [v1.0.1 release](https://github.com/microsoft/mxc/releases/tag/v1.0.1).

**Fallback rule:** if the selected MXC tier cannot enforce the required policy, stop and investigate. Do not fall back to ordinary `subprocess.Popen`, WSL, an identity-less proxy, or direct network access while retaining the word “protected”.

---

## 3. Phases and exit gates

We complete one phase at a time. A phase is not complete because code has been written; it is complete only after its exit gate passes and the evidence is recorded.

### Phase 0 — Build control, host compatibility and CI baseline

**Target:** 8 November

**Purpose:** Lock the design and remove unknowns before investing in the Windows runtime.

Work:
- Freeze the phase plan and the MVP scope.
- Verify the new repository tree, package layout, branch/commit convention and issue/phase log convention.
- Inspect the user's Windows edition/build, architecture, Python, .NET SDK/runtime, and available permissions.
- Fix the existing Windows CI lint blocker, then execute lint, type-check, tests and package build.
- Build a tiny MXC .NET probe outside the product runner: print platform support, available backends and request-probe diagnostics for a minimal no-network ProcessContainer request.
- Record whether host preparation is required; do not perform privileged setup automatically.

**Exit gate:**
- Windows CI passes through all steps (not just dependency installation).
- We know whether the development machine can run the selected ProcessContainer tier.
- A minimal .NET MXC app builds and returns structured host/request probe results.
- The MVP and unsupported-host behavior are documented.

**Stop condition:** If MXC cannot provide the required Windows containment on the development/target environment, reassess the backend before continuing. Do not build product features on an assumed sandbox.

### Phase 1 — Portable security core parity

**Target:** 8–10 November

**Purpose:** Reuse existing proven logic rather than rewriting it.

Port/refine:
- Pydantic policy schema and strict YAML parser.
- Deterministic policy engine and rule precedence.
- Policy evaluation result types and stable exit codes.
- Hash-chained audit events/logger/verifier, optional HMAC and reports.
- Deterministic simulator and reusable attack scenarios.
- Current CLI surface for validate, evaluate, simulate, audit verification and reports.

Method:
- Compare each copied module with the Linux reference and preserve behavior where it is OS-independent.
- Port existing tests alongside modules: acceptance, regression, policy properties, approval semantics, proxy parsing, audit tamper detection and report behavior.
- Do not port Bubblewrap, Seccomp, Linux resource limits or UNIX-socket bridge code.

**Exit gate:**
- Portable core tests pass on Windows Python 3.11, 3.12 and 3.13.
- Test coverage includes duplicate YAML keys, unknown fields, precedence, default-deny, unknown actions, hash/HMAC verification, tampering, and simulation expectations.
- CI passes lint, mypy, test and wheel/sdist smoke checks.

### Phase 2 — Windows policy semantics and filesystem safety primitives

**Target:** 9–11 November

**Purpose:** Make policy decisions correct for Windows rather than applying POSIX assumptions.

Implement/test:
- Drive-qualified, UNC, device namespace, rooted and relative path handling.
- Case-insensitive Windows path comparisons and documented logical `/workspace` mapping.
- Reserved device names, trailing dots/spaces, alternate data stream syntax and control characters.
- Reparse-point, symlink, junction, mount-point and hard-link detection strategy.
- Windows command-line tokenization, executable basename/extension resolution, quoting edge cases, and no shell invocation at the process boundary.
- Host/port parsing including bracketed IPv6, malformed authorities and port limits.
- Windows-specific default policy and test fixtures.

**Exit gate:**
- Unit/property tests prove unsafe/ambiguous paths and commands fail closed.
- Policy matching is deterministic under case variation and executable path variation.
- Filesystem paths passed to the enforcement layer are canonical physical paths, while the policy core uses the documented logical workspace namespace.

### Phase 3 — Private workspace staging and evidence

**Target:** 10–12 November

**Purpose:** Ensure the agent never works directly in the user's source project.

Implement:
- Create unique per-session workspace copy.
- Secret/credential exclusions and protected metadata handling.
- Safe traversal and file copying without following unsupported reparse points.
- Reject or safely omit ADS, junctions, mount points, unsupported file types and hard-link relationships.
- Apply restrictive session-directory permissions; ensure the agent is not granted the original workspace.
- Sanitize copied Git metadata/hooks as designed.
- Baseline/final manifests, SHA-256 file hashes, changed-path diff and session cleanup.
- Safe export/discard with no overwrite and traversal protections.

**Exit gate:**
- Attack fixtures for traversal, symlink/reparse escape, hard links, ADS, secret files and Git hook persistence pass on real Windows.
- A child process modifying the staged copy leaves the original workspace byte-for-byte unchanged.
- Interrupted staging and cleanup failures are handled safely and recorded.

### Phase 4 — Windows ProcessContainer execution backend

**Target:** 12–14 November

**Purpose:** Launch an actual Windows process within the selected OS-enforced boundary.

Implement:
- .NET 8 host bridge referencing the pinned MXC SDK.
- Typed request construction from validated Python-side session settings.
- Host and request-specific capability probing.
- Explicit physical workspace grants and protected-path denials.
- Explicit minimal child environment (including Windows-required environment variables).
- Process spawn/wait/timeout/kill and stdout/stderr transport.
- Structured result/error/warning protocol between Python and .NET.
- Fail-closed preflight; no target command starts on unsupported backend, failed probe, missing required policy or bridge crash.

**Exit gate:**
- Real Windows integration test runs a harmless command under ProcessContainer.
- Positive test reads an explicitly granted file and writes only to an explicitly granted output directory.
- Negative test attempts to write a denied/original host path and is denied.
- Timeout/termination behavior is verified.
- A forced preflight failure proves that the target command was never started.
- Selected tier and all warnings are recorded in the audit evidence.

### Phase 5 — Network policy firewall and proxy-only egress

**Target:** 14–17 November

**Purpose:** Preserve the original project's key network value: direct connections are not trusted just because an agent sets a proxy variable.

Implement:
- Host-side HTTP proxy and HTTPS CONNECT handling.
- Existing hostname/port policy semantics, destination normalization and DNS checks.
- Deny loopback, private, link-local, reserved and cloud metadata ranges by default; validate every DNS answer and connection target.
- Session-specific loopback endpoint, random port and bounded request parsing/timeouts.
- MXC egress default deny + documented proxy-only configuration.
- Identity-scoped proxy using the required package family/AppContainer profile identity and `allowedProxyPeer`; keep general host-loopback access denied.
- Proxy starts before client sandbox, is health-checked, remains alive for the session and is stopped during teardown.
- Record network allow/deny/approval decisions in the audit chain.

**Exit gate:**
- Direct IPv4 and IPv6 socket attempts from the contained process are blocked.
- Only the intended proxy endpoint is reachable from the contained workload.
- Proxy identity and exact loopback endpoint are verified.
- Unlisted destinations, private/loopback/metadata destinations, malformed requests, DNS rebinding patterns and private mixed DNS answers are denied before upstream connect.
- An allowed test destination works through the proxy.
- If identity-scoped proxy prerequisites are unavailable, network-enabled execution is refused; no weaker proxy mode is silently selected.

### Phase 6 — Human approvals, guarded operations and review workflow

**Target:** 16–18 November

**Purpose:** Preserve the original design's human-in-the-loop workflow without claiming universal interception.

Implement:
- Trusted host approval broker independent of agent stdin/stdout.
- Exact action, normalized target, policy rule, target fingerprint, expiry and one-use grant binding.
- Revalidation immediately before each mediated action; deny on target replacement/state change.
- Guarded filesystem/command/network adapters for actions explicitly mediated by the product.
- Session review, changed-path display, explicit export/discard and evidence preservation.
- Never treat approval as universal permission for arbitrary syscalls or child commands.

**Exit gate:**
- Wrong, expired, reused, mismatched and unavailable approvals all deny.
- Target mutation while approval is pending revokes the grant.
- Denied operations are never performed.
- Export copies only reviewed changed files, never overwrites, rejects traversal/reparse sources, and preserves audit evidence.

### Phase 7 — End-to-end adversarial validation

**Target:** 18–19 November

**Purpose:** Prove the complete product behavior on Windows—not only unit-level functions.

Run full test layers:
- Policy schema, precedence and property-based tests.
- Workspace/path/reparse/ADS/race tests.
- Process containment and process-tree timeout tests.
- Direct network bypass, IPv4/IPv6, loopback and DNS adversarial tests.
- Approval-scope/replay/expiry/TOCTOU tests.
- Audit tampering, ordering, missing HMAC and head-anchor tests.
- Full attack scenario with expected outcomes and evidence inspection.
- Clean Windows environment smoke test and Python/.NET package build tests.

**Exit gate:**
- All required Windows integration and adversarial tests pass on a recorded Windows build.
- No skipped test is counted as passed.
- No critical/high-severity known defect remains in the demo path.
- README security claims match observed evidence.
- CI green, wheels/package install cleanly, and logs are retained.

### Phase 8 — Usable MVP, demo and registration

**Target:** 19–20 November

**Purpose:** Make the project usable by another developer/judge, not merely reviewable as source code.

Deliver:
- Clean installation instructions for Python, .NET bridge and MXC requirements.
- A one-command policy validation/simulation path and an accurately gated run command.
- Example Windows policy, example disposable workspace and repeatable attack demo.
- Troubleshooting: host support, required host prep, policy denials, audit verification and clean-up.
- Short demo script and evidence pack.
- Release candidate tag and tested commit SHA.
- Register on **20 November** as planned.

**Exit gate:**
- A second person can follow the setup guide and run the safe demo without reading internal source code.
- The exact demo build is tagged and its test evidence is saved.
- Registration is complete on 20 November.

### Stabilization window — 21–24 November

Only fix high-priority defects, installation issues, demo-breaking problems and documentation inaccuracies. Avoid introducing new features unless they are required to correct a security flaw.

### Hard deadline — 25 November

Registration closes. Keep a known-good tagged build and evidence snapshot. Do not describe post-deadline work as part of the pre-registration release.

---

## 4. Fast-track strategy using the Linux reference

We move faster through **reuse and test-porting**, not by weakening security checks.

### Reuse directly where behavior is portable

- Policy Pydantic models and strict YAML parser.
- Decision precedence and deterministic policy result structure.
- Audit record schema, hash chaining, HMAC and verification logic.
- Simulator and scenario runner.
- Stable exit-code and reporting concepts.
- Test cases and adversarial attack intent.

### Rewrite only where Windows semantics differ

- Process launch and isolation.
- Filesystem staging, path validation, ACLs and reparse-point handling.
- Network enforcement and proxy transport.
- Approval terminal/broker implementation.
- Process lifecycle, environment and Windows-specific packaging.

### Do not carry over

- Bubblewrap command construction.
- Linux namespaces and mount flags.
- Seccomp-BPF filters.
- POSIX `resource.setrlimit`.
- `/dev/tty`.
- UNIX-domain socket guest bridge.
- POSIX-only path, permission or symlink assumptions.

### Work pattern for every phase

1. Read the matching Linux implementation and tests.
2. Write/port acceptance tests for the intended Windows behavior.
3. Port the smallest reusable code slice.
4. Implement the Windows-specific adapter/backend.
5. Run targeted tests, the complete test suite and Windows CI.
6. Update README, architecture notes, security limitations and phase log.
7. Commit the phase with a clear message and record its tested commit SHA.
8. Stop at the exit gate. Do not start the next phase with a red gate.

---

## 5. Definition of done for every phase

A phase close-out must contain:
- Scope completed and intentionally deferred items.
- Files/modules changed.
- Tests added and executed, with exact result.
- Windows build / Python / .NET / MXC versions where applicable.
- Security assumptions and limitations.
- CI run URL and tested commit SHA.
- A phase log under `docs/phase-logs/`.
- Updated phase status in `docs/phase-tracker.md`.

A code commit without its test evidence is not a phase completion.

---

## 6. Current position (8 November)

| Workstream | Status |
|---|---|
| New Windows repository and architecture docs | Done |
| Python policy/parser/audit/simulator baseline copied | Done as initial scaffold; parity not yet demonstrated |
| Windows command/path helper baseline | Present; more adversarial cases required |
| Windows policy/scenario/CLI baseline | Present |
| Windows CI workflow | Added; currently **red at Ruff lint**, so later CI steps did not run |
| MXC candidate and networking design research | Done at documentation level |
| MXC host probe on the actual development machine | Not done |
| Workspace stager | Not implemented |
| .NET ProcessContainer bridge | Not implemented |
| Proxy identity and network enforcement | Not implemented |
| Approval and review/export workflow | Not implemented |
| End-to-end Windows security proof | Not done |

**Current phase status:** Phase 0 is in progress; Phase 1 has a scaffold but is not complete. No Windows agent-run security boundary is available yet.
