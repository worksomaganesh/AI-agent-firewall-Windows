# Windows-native architecture

**Status:** proposed architecture, not yet implemented. Treat every control below as a design target until an implementation and a Windows enforcement test demonstrate it.

## 1. Design objective

Keep the reusable security control plane from the Linux-first prototype, but replace every Linux enforcement dependency with a Windows-native mechanism. Never start the requested agent command after a required enforcement step fails.

The primary target is Windows 11 x64. Other Windows releases and architectures are not supported claims until tested.

## 2. Component split

| Component | Responsibility | Implementation target |
|---|---|---|
| CLI / supervisor | Validate inputs, coordinate sessions, report status | Python + Typer |
| Policy core | Strict policy schema and deterministic decisions | Python + Pydantic |
| Audit core | Structured JSONL events, SHA-256 chain, optional HMAC, verification | Python |
| Workspace stager | Private project copy, secret exclusion, snapshots and diffs | Python with Windows-native file checks |
| Windows native host | AppContainer profile/token, process creation, ACLs, Job Objects, WFP filters | Small C#/.NET sidecar using reviewed Win32 P/Invoke |
| Host approval broker | Operator confirmation independent of child stdin | Host-side console/UI component |
| Network proxy | HTTP proxy and HTTPS CONNECT destination mediation | Python host process, loopback-only listener |
| Review/export | Inspect and export selected staged changes without overwriting | Python, Windows-safe filesystem operations |

The native host is deliberately separate from the Python control plane. Security-sensitive Windows structures and handles should be implemented in one small, testable layer rather than scattered ctypes calls throughout the application.

## 3. Windows enforcement design

### 3.1 AppContainer identity

Create or derive a dedicated AppContainer profile for a session (or a carefully managed reusable profile). Launch the agent with the AppContainer security capabilities attribute and grant no network capabilities to the agent.

The AppContainer package SID is the identity used for explicit access to the staged workspace and for WFP filtering. Access to a file requires both the normal user/group access and the AppContainer access to permit it; granting the package SID write access to one staged directory does not grant it write access to the original project.

Initial capability posture:
- No internetClient or privateNetworkClientServer capability.
- No camera, microphone, location, or other unrelated capabilities.
- No access to the original project directory.
- Only explicit read/write access to the session's staged workspace and required runtime paths.

AppContainer is a Windows kernel-enforced process isolation mechanism, but it is **not** a separate virtual machine or a guarantee against every OS vulnerability. We must test the actual process token and attempted resource access.

### 3.2 Process lifetime and resource limits

Create a Windows Job Object for each session. Configure limits before the target starts, create the process suspended, assign it to the Job Object, and only then resume its primary thread.

Required controls:
- Kill all associated processes when the session/job handle is closed.
- No breakaway flags.
- Configurable active-process and job-memory limits.
- CPU-rate or job-time limits where the selected API semantics match the documented CLI option.
- A supervisor wall-clock timeout that terminates the whole job.
- Record which limits were successfully installed; never report an unsupported limit as enforced.

Windows normally associates child processes created with CreateProcess with the parent's job. We must separately test alternate process-creation paths and document any that are outside the guarantee.

### 3.3 Network mediation

The host proxy must never be the only network control. Environment variables such as HTTP_PROXY and HTTPS_PROXY are application conventions and can be bypassed by direct sockets.

Planned network path:

1. The AppContainer receives no general network capabilities.
2. The host starts a loopback-only HTTP proxy on a random, session-specific port.
3. If AppContainer loopback isolation requires an exemption, it is temporary and removed during teardown.
4. Windows Filtering Platform filters are installed for the session's AppContainer package SID. The intended rule is to permit only the exact loopback broker address/port and block other outbound connect attempts for that SID (IPv4 and IPv6).
5. The agent receives proxy environment variables pointing only to that broker.
6. The host proxy evaluates the policy, resolves destinations itself, rejects loopback/private/link-local/reserved/metadata destinations, revalidates the decision, and only then opens the upstream connection.
7. HTTPS CONNECT remains an opaque TLS tunnel; the proxy sees the destination, not encrypted request bodies.

The design uses WFP's application-layer enforcement and AppContainer package identity conditions. The WFP rule ordering, loopback behavior, filter lifetime, IPv4/IPv6 coverage, and required elevation must be proven in tests before network-enabled execution is advertised.

**Fail-closed rule:** if the AppContainer identity, loopback restriction, WFP filters, or proxy health check cannot be established, a network-enabled run is refused. An explicit offline mode may be offered only when the agent has no path to the network and this has been verified.

### 3.4 Workspace staging and Windows filesystem safety

The original workspace is read-only input to the supervisor; the agent operates on a private session copy.

Windows-specific requirements:
- Inspect file attributes and reparse tags using native handle-based APIs; do not rely only on Python Path.is_symlink().
- Initial safe policy: reject or omit reparse points, junctions, mount points, and unsupported file types rather than following them.
- Do not preserve hard-link relationships from the source tree in the staged copy.
- Reject alternate-data-stream path syntax and Windows device names; normalize drive paths, UNC paths, case-insensitive comparisons, trailing dots/spaces, and extended-length path prefixes.
- Copy ordinary file data into new files; do not copy security descriptors or alternate data streams from untrusted source entries.
- Sanitize Git configuration and hooks; protect .git, .github/workflows, and build/dependency metadata through the policy and staging boundary.
- Apply a restrictive DACL to the session directory and grant the AppContainer SID only the required staged-workspace rights.
- Snapshot file contents with SHA-256 and record metadata without following reparse points.

A staging failure must stop the run before the agent process is created.

### 3.5 Human approval

Retain exact-action, one-use, short-lived approval grants. Approval must:
- Be displayed by the trusted host process, never accepted from the agent's stdin.
- Bind to the action, normalized target, matched rule, and target-state fingerprint.
- Expire quickly and be consumed once.
- Be revalidated immediately before the mediated action.
- Deny if there is no interactive approval channel, if the response is not exact, or if the target state changes.

Approval applies only to operations routed through our trusted broker/adapters. It does not mean every arbitrary command or filesystem syscall is intercepted.

### 3.6 Audit and session evidence

Keep the portable audit design:
- JSONL records with sequence numbers and timestamps.
- SHA-256 hash chaining and optional HMAC.
- Explicit enforcement mode (simulation vs. Windows AppContainer enforcement).
- Session start/end, policy decisions, approval outcomes, network decisions, sandbox setup failures, and final exit result.
- Baseline/final workspace manifests, changed-path diff, session summary, and human-readable report.

A local hash chain is tamper-evident for edits that break the chain, but a host actor who can replace the complete bundle can recompute it unless the final head or key is independently protected.

## 4. Operator data flow

Developer
  -> Python CLI / Supervisor
  -> strict policy validation -> Policy Engine
  -> private workspace copy -> Windows-safe stager + baseline manifest
  -> start host proxy -> loopback HTTP/HTTPS proxy
  -> native launch request -> Windows Native Host
       -> AppContainer identity
       -> DACL and WFP setup
       -> Job Object limits
       -> suspended process -> assign job -> resume
  -> untrusted agent + child processes
       -> workspace operations inside staged copy
       -> proxy-routed HTTP/HTTPS -> Host Policy Proxy -> checked public destination
  -> audit log + final manifest + diff + report
  -> human review -> explicit export or discard

## 5. Command policy boundary

A policy engine can evaluate command requests, but AppContainer and Job Objects do not automatically inspect every command a descendant process starts. The first Windows MVP will enforce the OS sandbox around the full child process tree and enforce command rules only for explicitly mediated command/tool adapters and the initial launch request.

Do not claim universal command interception until a separate, tested process-creation enforcement design exists.

## 6. Optional stronger isolation backend

Windows Sandbox may be explored as an optional high-isolation backend for compatible Windows editions. It must use an explicit configuration with networking disabled by default and carefully reviewed mapped-folder permissions. It is not the default MVP backend because availability, host integration, and safe change export need separate validation.

## 7. Microsoft references

- [Launch an AppContainer](https://learn.microsoft.com/en-us/windows/win32/secauthz/implementing-an-appcontainer)
- [AppContainer isolation](https://learn.microsoft.com/en-us/windows/win32/secauthz/appcontainer-isolation)
- [Job Objects](https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects)
- [Job Object extended limits](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_extended_limit_information)
- [Windows Filtering Platform](https://learn.microsoft.com/en-us/windows/win32/fwp/about-windows-filtering-platform)
- [Application Layer Enforcement](https://learn.microsoft.com/en-us/windows/win32/fwp/application-layer-enforcement--ale-)
- [WFP filtering condition identifiers](https://learn.microsoft.com/en-us/windows/win32/fwp/filtering-condition-identifiers-)
- [Windows Sandbox configuration](https://learn.microsoft.com/en-us/windows/security/application-security/application-isolation/windows-sandbox/windows-sandbox-configure-using-wsb-file)
