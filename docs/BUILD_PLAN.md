# Windows Build Plan — Sequential Phase Delivery

**Project:** AI Agent Firewall for Windows  
**Linux reference:** https://github.com/worksomaganesh/ai-agent-firewall  
**Windows implementation:** https://github.com/worksomaganesh/AI-agent-firewall-Windows  
**Plan date:** 8 November 2026  
**Registration checkpoint:** 20 November 2026  
**Hard deadline:** 25 November 2026

---

## 1. Mission

Build a usable Windows-native security supervisor for AI coding agents. An agent works against a private staged copy of a developer's project, receives only the filesystem and network access the operator allows, requests human approval for explicitly mediated sensitive operations, and leaves reviewable, verifiable evidence.

This is a separate Windows implementation. The Linux repository is our reference for architecture, policy behavior, tests, engineering sequence and documentation discipline—not code to mechanically rename.

### Product guarantees we intend to prove

1. **Strict policy:** duplicate YAML keys, unknown fields, malformed inputs and unknown actions fail closed.
2. **Deterministic decisions:** DENY > REQUIRE_APPROVAL > ALLOW > DEFAULT DENY.
3. **Private workspace:** the agent cannot modify the original project; it works only inside a staged copy.
4. **OS enforcement:** required Windows isolation is established before the requested process starts. No silent unsandboxed fallback.
5. **Network:** offline/default-deny is the initial posture. Networked execution is enabled only after proxy-only HTTP/HTTPS egress and proxy identity are verified.
6. **Human approval:** exact-target, short-lived, one-use, host-side approval, revalidated before explicitly mediated operations.
7. **Evidence:** session audit chain, baseline/final manifests, diff and human-readable report.
8. **Honest claims:** simulation is never called enforcement; only observed and tested behavior is claimed.

The first release is a focused local developer tool—not a GUI dashboard, enterprise endpoint product, universal command interceptor or certified production security product.

---

## 2. Build method: follow the existing Linux project

We will follow the same development discipline that produced the Linux project:

- Build a deterministic policy core first.
- Keep enforcement behind a clear backend boundary.
- Separate the trusted host/supervisor from the untrusted agent.
- Add tests with each component instead of postponing tests to the end.
- Exercise attacks, malformed input, fail-closed behavior and state changes—not only happy paths.
- Maintain audit evidence and explicit phase logs.
- Keep the README and security limitations aligned with the actual code.
- Finish one phase, review its evidence, then start the next.

### Reuse from the Linux repository

| Existing implementation | Windows plan |
|---|---|
| Pydantic policy schema and strict YAML parser | Reuse where platform-neutral |
| DENY / approval / ALLOW / default-deny policy engine | Preserve precedence and behavior |
| Audit event schema, SHA-256 chain, optional HMAC and verifier | Reuse portable core |
| Simulator and mock-agent attack scenarios | Reuse and extend Windows attack cases |
| Exit codes, report structure and CLI concepts | Preserve the interface where useful |
| Existing acceptance, regression, property and adversarial tests | Port the test intent, then adapt platform-specific cases |

### Rewrite for Windows only

- Process launch and operating-system containment.
- Workspace staging, Windows paths, ACLs, reparse points, junctions and alternate data streams.
- Network restrictions and the Windows proxy path.
- Host approval channel and Windows process lifecycle.
- Windows packaging, install/setup and CI.

### Do not copy into the Windows runtime

Bubblewrap, Linux namespaces/mount flags, Seccomp-BPF, POSIX `resource.setrlimit`, `/dev/tty`, UNIX-domain socket guest bridge, and POSIX permission/symlink assumptions.

---

## 3. Architecture choice and mandatory feasibility gate

### Preferred containment candidate: Microsoft Execution Containers (MXC)

The preferred path is Microsoft's Windows ProcessContainer backend, integrated through the official .NET SDK. This avoids building our own AppContainer/WFP layer before proving host compatibility.

- Python 3.11+ is the product control plane.
- A small .NET 8 sidecar references `Microsoft.Mxc.Sdk`.
- It probes platform support and the exact requested ProcessContainer policy before launching.
- MXC applies the Windows process/filesystem/network restrictions it supports.
- Python remains responsible for policy composition, domain policy proxy decisions, approvals, session audit and review/export.

Do not pin a package version based only on a documentation example. Phase 0 must verify the current package version, API surface, license, supported Windows build and host diagnostics; then we pin the exact tested SDK/runtime in the bridge project.

### MXC compatibility facts that affect the design

- The current official quickstart states Windows 11 24H2 or later, a supported ProcessContainer environment, and .NET 8 SDK or later for C#.
- A supported OS version does **not** guarantee that every optional ProcessContainer feature exists on a given host. Runtime support and request-specific probes are mandatory.
- Some hosts need a one-time administrator-approved preparation step for the AppContainer fallback tier. The app must display the diagnostic and instructions; it must never self-elevate or silently change machine security settings.
- The network proxy contract is for HTTP/HTTPS clients using the supported proxy path. It is **not a transparent TCP/UDP tunnel**. Raw sockets and non-proxy protocols must remain blocked in the proxy-only posture.
- MXC's WFP rules enforce IP/CIDR, protocol and port boundaries. They do not provide durable DNS-name policy. Our host proxy must enforce hostname/port rules and DNS-address validation for HTTP CONNECT / HTTP requests.
- The secure proxy mode requires an identity-scoped proxy peer (`allowedProxyPeer`) and the documented ingress/egress settings. Identity-less host-loopback proxy is a weaker compatibility path and must not be silently selected.
- If exact request probing says the requested tier/policy is unsupported, the run command must not start.

Official sources:
- [MXC quickstart](https://learn.microsoft.com/en-us/windows/apps/develop/mxc/quickstart)
- [MXC platform support](https://learn.microsoft.com/en-us/windows/apps/develop/mxc/platform-support)
- [ProcessContainer networking](https://github.com/microsoft/mxc/blob/main/docs/backends/process-container/networking.md)
- [MXC .NET SDK reference](https://github.com/microsoft/mxc/tree/main/docs/api-reference/dotnet/v1)

### Mandatory backend gate

The team does not commit to MXC as the final runtime until Phase 0 proves that the development/target laptop can probe and execute the minimum no-network ProcessContainer request. If it cannot, stop and reassess the backend before building the rest of the product on an assumed sandbox.

---

## 4. Phases

We use four major phases, matching the structure of the existing project, preceded by a short Phase 0 feasibility gate.

## Phase 0 — Foundation and Windows runtime feasibility

**Target:** 8 November

Purpose: lock architecture, toolchain and CI before feature development.

Work:
1. Confirm the new repo, default branch, folder layout, phase tracker and documentation convention.
2. Record the actual target machine's Windows edition/build, architecture, Python version and available .NET SDK/runtime.
3. Fix the current Windows CI lint blocker and get the full Python checks running.
4. Build a tiny standalone .NET MXC probe; inspect platform support, available ProcessContainer backend and exact request-probe diagnostics.
5. Check host-preparation warnings, package version, public API, licensing and deployment requirements.
6. Record whether the laptop can run a harmless no-network ProcessContainer test. No privileged preparation is performed automatically.

Exit gate:
- Windows CI passes lint, typing, tests and package build.
- MXC probe builds and reports support/unsupported reasons on the actual target machine.
- Host-preparation requirements and exact SDK/runtime versions are known.
- Backend feasibility is explicitly recorded.

**Stop condition:** if the chosen containment tier cannot be made available on the target environment, reassess before Phase I/II work expands.

## Phase I — Deterministic security core and Windows policy semantics

**Target:** 8–10 November

Purpose: port the reusable core quickly and make Windows-specific decision inputs correct.

Work:
1. Port/refine strict Pydantic policy schema and duplicate-key/unknown-field YAML parser.
2. Preserve deterministic rule precedence: DENY > REQUIRE_APPROVAL > ALLOW > DEFAULT DENY.
3. Port policy evaluation, stable exit codes, audit schema/hash core/verifier, simulator and report concepts.
4. Build Windows command-line tokenization and executable normalization. Never invoke a shell for policy parsing or direct process launch.
5. Define a logical `/workspace` policy namespace mapped explicitly to the physical staged workspace.
6. Normalize Windows paths and reject unsafe forms: traversal, drive-qualified/UNC/device namespace paths, reserved device names, trailing dots/spaces, alternate data streams and control characters.
7. Normalize/validate network targets including bracketed IPv6, malformed authorities, IDNA/hostname rules and port bounds.
8. Port relevant existing acceptance, regression, property and adversarial tests; add Windows fixtures.
9. Finish `validate-policy`, `evaluate`, and deterministic `simulate` CLI paths.

Exit gate:
- The portable policy/audit/simulation suite passes on Windows with Python 3.11, 3.12 and 3.13.
- Policy precedence, default-deny, YAML rejection, malformed command/path/network inputs and audit tamper/HMAC cases are tested.
- The Windows default policy and attack scenario validate.
- No Linux execution dependency remains in the Phase I code path.

## Phase II — Windows sandbox, private workspace and network enforcement

**Target:** 10–16 November

Purpose: build the real Windows execution boundary.

### A. Workspace staging

- Create a unique per-session private workspace copy.
- Exclude credentials and sensitive local files; protect Git hooks/config and sensitive metadata.
- Reject/omit unsupported reparse points, symlinks, junctions, mount points, hard-link relationships and ADS rather than following them.
- Apply restrictive permissions to the session root.
- Do not copy source ACLs or alternate streams.
- Create baseline/final manifests and SHA-256 file hashes.
- Prove source workspace immutability.

### B. MXC host bridge and process execution

- Build a minimal .NET 8 sidecar with a pinned, tested `Microsoft.Mxc.Sdk` version.
- Use typed SDK request classes, not hand-assembled JSON.
- Run host-wide capability discovery and exact request-specific ProcessContainer probe.
- Map the staged workspace to explicit read-write/read-only/denied filesystem paths.
- Supply a minimal child environment. For Windows ProcessContainer, validate all required environment fields (including `SystemRoot` and `LOCALAPPDATA`) against the selected SDK contract.
- Spawn/wait/terminate with a clear timeout; stream stdout/stderr back to the supervisor.
- Use structured request/response types and explicit error/warning codes between Python and .NET.
- Refuse to start the requested command after a missing bridge, failed probe, unsupported tier, invalid filesystem policy or setup error.

### C. Network controls

First implement and test **offline mode**, with all external network access denied.

Then implement the secure network-enabled mode:
- Start a separate host policy proxy on a session-specific loopback endpoint.
- Configure MXC's supported HTTP/HTTPS proxy-only egress mode, with egress default deny.
- Use an identity-scoped proxy package/AppContainer profile through `allowedProxyPeer`; keep general host-loopback access denied.
- Health-check and bind the proxy to the exact endpoint specified in the MXC request.
- Apply domain/port policy, DNS answer validation, reserved/private/loopback/link-local/metadata destination rejection, request framing limits and timeouts inside the proxy.
- Ensure IPv4 and IPv6 direct sockets and raw/non-HTTP protocols are blocked by the OS containment policy.
- Record proxy decisions in audit evidence and tear down proxy/session state after exit.

Exit gate:
- Real Windows tests prove agent access is restricted to the staged workspace.
- A harmless ProcessContainer command runs; original source remains unchanged.
- Unsupported request/probe or backend failure proves the target process is never launched unsandboxed.
- Offline mode denies external network.
- Proxy-only mode (when supported) allows only the identity-bound proxy path; direct IPv4/IPv6 and raw/non-proxy network paths are blocked.
- The proxy enforces allowed/denied hostnames and ports before opening upstream connections.
- All tested tier, proxy, network and cleanup details are reported honestly.

## Phase III — Approvals, guarded workflows and evidence

**Target:** 16–18 November

Purpose: integrate the human-in-the-loop and evidence workflow from the existing product.

Work:
1. Port exact-action, one-use, short-lived approval grants.
2. Implement a trusted host approval channel independent of agent stdin/stdout.
3. Bind grants to action, normalized target, matched rule and target-state fingerprint; revalidate just before mediated operation.
4. Fail closed on wrong response, timeout, expiry, reuse, scope mismatch, missing broker and changed target.
5. Connect approvals to explicitly mediated filesystem/command/network adapters.
6. Add complete session lifecycle events: policy decisions, sandbox preflight, selected tier, proxy state, process result, approvals, cleanup.
7. Generate baseline/final workspace snapshots and changed-path diff.
8. Implement review, explicit export and discard; prevent overwrite/traversal/reparse-source export.
9. Preserve evidence even when export is denied or the session fails.

Important boundary: this approval layer governs operations routed through our trusted adapters. Do not claim it intercepts every arbitrary syscall or every child command.

Exit gate:
- Approval replay/expiry/mismatch/TOCTOU tests pass.
- Denied operations never execute.
- Export only copies reviewed files, never overwrites, and cannot follow unsafe source paths.
- A complete session report shows enforcement mode, policy decisions, audit status, changed files, and limitations.

## Phase IV — Advanced verification, adversarial hardening and release

**Target:** 18–20 November

Purpose: test the product as a complete Windows security tool and prepare a usable demo.

Test layers:
- Policy schema and property-based tests.
- Windows command/path normalization and adversarial path cases.
- Reparse point, junction, ADS, hard-link and staging race cases.
- Process containment, process termination and timeout tests.
- Direct IPv4/IPv6 network bypass and proxy identity tests.
- HTTP framing, CONNECT authority mismatch, DNS rebinding and private-address tests.
- Approval scope, expiry, replay and target replacement tests.
- Audit ordering, hash-chain tampering, HMAC and external head-anchor tests.
- End-to-end attack scenario with expected decisions and evidence inspection.
- Clean-machine install, wheel/source package smoke tests and Windows CI.

Release work:
- Clear Python and .NET installation/setup guide.
- Prerequisite and supported-host matrix.
- Example Windows policy and attack scenario.
- Troubleshooting for unsupported hosts, required admin-approved preparation, policy denials and cleanup.
- Repeatable judge/demo script.
- Tag a known-good release candidate and retain the tested commit SHA/CI evidence.
- Register on **20 November** as planned.

Exit gate:
- Required Windows integration/adversarial tests pass on a recorded Windows build.
- No critical/high known defect remains in the demo path.
- CI and package/install smoke tests are green.
- Another person can follow the docs and run the safe demo.
- Exact release candidate is tagged and evidence is preserved.

## Stabilization — 21–24 November

Only fix high-priority security, installation and demo-breaking defects. Avoid risky feature expansion. Re-test the known-good candidate after every change and keep a fallback tag.

## 25 November — hard registration deadline

Confirm registration completion and preserve the tagged build and evidence snapshot. No claim of registration is made until the user confirms it.

---

## 5. Fast-track plan

We move faster by reusing the existing project's tested logic, not by weakening enforcement or skipping tests.

- Port logic and tests together, not code alone.
- Keep the policy engine independent of OS-specific adapters.
- Start with offline-only Windows process containment before networked mode.
- Reuse the simulator for rapid regression while separately requiring real Windows enforcement tests.
- Limit the first UI to CLI and reports; defer GUI, plugin ecosystem, dashboards and multi-platform work.
- Use one small .NET bridge rather than implementing native Windows APIs in multiple Python modules.
- Make host capability probing a runtime gate, not a one-time assumption.
- Do not begin the next major phase while the current phase's exit gate is red.

## 6. Definition of done and phase records

For every phase, record:
- Deliverables and changed modules.
- Reused Linux behavior and Windows-specific adaptations.
- Tests executed and exact pass/fail/skip counts.
- Windows edition/build, architecture, Python/.NET/MXC versions where relevant.
- CI run URL and tested commit SHA.
- Security assumptions, limitations and deferred work.
- Updated README/security claims and a phase log under `docs/phase-logs/`.

A commit without test evidence is not phase completion.

---

## 7. Current position — 8 November 2026

| Item | Status |
|---|---|
| New Windows repo, README and architecture/porting docs | Present |
| Python policy/parser/engine/audit/simulator scaffold | Present; full parity not yet demonstrated |
| Windows command/path helpers and starter tests | Present; adversarial coverage incomplete |
| Windows policy/scenario and CLI scaffold | Present |
| Windows CI matrix | Added; currently red at Ruff lint; mypy/tests/package steps have not completed |
| MXC candidate and proxy-only networking research | Done at documentation level |
| Actual laptop MXC host probe | Not done |
| Workspace stager | Not implemented |
| .NET ProcessContainer bridge | Not implemented |
| Windows execution enforcement | Not implemented |
| Identity-scoped proxy service | Not implemented |
| Approval/review/export workflow | Not implemented |
| End-to-end Windows security evidence | Not done |

**Current status:** Phase 0 is IN PROGRESS. Phase I has an initial scaffold but has not passed its completion gate. No protected Windows agent-run command is available yet.
