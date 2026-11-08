# Windows-native architecture

**Status:** the portable Python core is present. The MXC native-host integration and its enforcement tests are not complete yet. Treat every Windows security control below as a design target until an observed Windows test demonstrates it.

## 1. Design objective

Preserve the useful control-plane guarantees of the Linux-first project while using a maintained Windows-native containment engine. The agent must never start if the requested Windows isolation cannot be established.

Primary target: Windows 11 24H2 or later with an MXC-supported ProcessContainer tier. Other releases and architectures are unsupported until tested.

## 2. Component split

| Component | Responsibility | Implementation |
|---|---|---|
| CLI / supervisor | Validate inputs, coordinate sessions and present results | Python + Typer |
| Policy core | Strict YAML validation and deterministic decisions | Python + Pydantic |
| Audit core | JSONL event chain, optional HMAC, verification and reports | Python |
| Workspace stager | Private copy, secret exclusions, Windows path validation, manifests and diffs | Python initially; native handle checks where required |
| Windows containment host | Probe and launch native ProcessContainer requests | .NET 8 sidecar using official `Microsoft.Mxc.Sdk` v1.0.1 |
| OS enforcement | Process containment, filesystem policy, network filters and proxy restrictions | Microsoft Execution Containers (MXC) ProcessContainer backend |
| Host approval broker | Exact-action, one-use approval, independent of agent stdin | Trusted host-side Python/console broker |
| Network policy proxy | HTTP/HTTPS destination rules, DNS checks and network audit | Separate, restricted Windows proxy process; identity-bound to the MXC client |
| Review/export | Inspect staged changes, verify evidence and copy selected files | Python Windows-safe workflow |

The security-critical OS boundary should be delegated to MXC's maintained native runtime rather than reimplemented as ad hoc P/Invoke scattered across the application. Our product remains responsible for composing the policy, checking support, arranging the proxy identity, preserving the staged workspace, and verifying the evidence.

## 3. MXC ProcessContainer integration

### 3.1 Runtime discovery and preflight

The .NET bridge references `Microsoft.Mxc.Sdk` version `1.0.1` and uses the public `Microsoft.Mxc.Sdk.V1` API.

Before any target process starts, it must:

1. Call `MxcPlatform.GetPlatformSupport()`.
2. Call `MxcPlatform.GetAvailableBackends()` and verify that `ProcessContainer` is present.
3. Build the exact `ContainerRequest` for the requested workspace, filesystem rules and network mode.
4. Call `MxcContainer.Probe(request)` and inspect its selected isolation tier, warnings, and error.
5. Reject the request if the selected tier cannot honour the filesystem/network controls we require.
6. Only then call `MxcContainer.RunAsync` or `MxcContainer.SpawnAsync`.

A host-wide support result is advisory; the request-specific probe is the relevant preflight for a particular policy. A probe does not execute the command and does not prove that an external proxy is reachable. The supervisor must separately health-check the exact broker endpoint.

**Fail-closed rule:** no automatic fallback to an ordinary process, WSL shell, Linux container, or an unfiltered proxy. Unsupported requests return an error before the command starts.

### 3.2 Filesystem isolation

MXC's `FilesystemPolicy` supports read-write paths, read-only paths and denied paths. The first run design grants the agent write access only to the private staged workspace; the original source directory is never granted.

- Apply explicit read-only and denied paths for sensitive repository metadata and protected files.
- Exclude common credentials from the staged copy before the sandbox starts.
- Do not follow reparse points, junctions or mount points while staging. Reject unsupported paths rather than guessing.
- Reject device names, alternate data stream syntax, drive-qualified paths, UNC paths, trailing dots/spaces and traversal.
- Do not copy source ACLs or alternate data streams into the staged workspace.
- Snapshot the staged copy before and after the run, without following reparse points.

The Python policy engine's logical `/workspace` path is not a physical Windows path. The native bridge maps the logical workspace to the explicit physical staging path in the MXC request.

The current MXC filesystem API is path-based and offers static read-write/read-only/denied path lists. It does not, by itself, implement our per-operation one-time approval semantics. For paths requiring approval, the first secure design is to keep them non-writable inside the agent container and route approved modifications through a trusted mediated operation. Do not claim that MXC automatically prompts for a human approval on arbitrary writes.

### 3.3 Network isolation

Do not rely on `HTTP_PROXY`, `HTTPS_PROXY`, or `NO_PROXY` environment variables alone; an arbitrary program can bypass them with direct sockets.

The intended Windows network mode is MXC's **proxy-only egress** contract:

- Client container egress defaults to deny.
- Client ingress defaults to allow only to establish the required private-network capability; MXC's BaseContainer/WFP enforcement then restricts the client's outbound traffic to the configured proxy endpoint.
- The client uses `runtimeConfig.networkProxy` to point to a loopback endpoint.
- The preferred deployment is an **identity-scoped proxy**: `processContainer.network.allowedProxyPeer` names the package family or AppContainer profile that owns the proxy.
- With an identity-scoped proxy, `ingress.hostLoopback` remains deny; do not open general host-loopback access.
- The proxy process is separate from the client container and has its own constrained identity/capabilities. It is the only component that can make upstream connections, and it applies our hostname/port policy before connecting.
- The proxy binds only to the exact loopback address and random session port supplied to MXC.
- On teardown, stop the proxy and remove per-session resources.

Microsoft documents an identity-less host proxy as a weaker development/testing compatibility route: it omits `allowedProxyPeer` and requires `hostLoopback: allow`. That opens broader host-loopback access and does not verify which process owns the listener. **It is not the intended secure release configuration and must not be silently used as fallback.**

The proxy still sees HTTPS CONNECT destinations, not encrypted TLS payloads. It cannot prevent data exfiltration to a destination explicitly allowed by policy.

### 3.4 Process lifetime and limits

MXC provides a process handle, timeout support, and process termination operations. The bridge will set an explicit wall-clock timeout and kill the session process tree on cancellation or teardown. Any CPU/memory limits must be exposed only if the selected backend documents and passes tests for those exact limits; do not claim aggregate resource quotas without evidence.

### 3.5 Human approval

Retain exact-action, one-use, short-lived grants:
- Prompt only on a trusted host channel, never via agent stdin.
- Bind grants to the action, normalized target, matched rule and target-state fingerprint.
- Revalidate immediately before the mediated operation.
- Deny if there is no trusted approval channel, if the operator response is not exact, or if the target changes.

Approval applies only to operations routed through our trusted broker/adapters. It does not mean every arbitrary process or filesystem call is intercepted.

### 3.6 Audit and session evidence

Keep the portable evidence design:
- JSONL with sequence numbers, UTC timestamps and SHA-256 event chaining.
- Optional HMAC; the key must be protected separately.
- Explicit enforcement mode: simulation versus Windows ProcessContainer.
- Policy/approval/network decisions, preflight failures, execution result and cleanup.
- Baseline/final workspace manifests, diffs, session summary and human-readable report.

A local hash chain detects changes that break its links, but a host actor who can replace the entire evidence bundle can recompute it unless the final head hash or HMAC key is independently protected.

## 4. Data flow

Developer
  -> Python CLI / Supervisor
  -> strict YAML validation -> Policy Engine
  -> private staged workspace -> baseline manifest
  -> start restricted proxy process (network mode only)
  -> .NET MXC bridge
       -> host/backend capability discovery
       -> request-specific ProcessContainer probe
       -> fail if the required tier or proxy policy is unsupported
       -> launch agent in ProcessContainer
  -> untrusted agent + child processes
       -> staged workspace only
       -> proxy-only network path (when enabled)
  -> audit log + final manifest + diff + report
  -> human review -> explicit export or discard

## 5. Command policy boundary

The policy engine can evaluate command requests, but neither a prompt nor a command rule in YAML automatically intercepts every command launched by a child process. MXC provides the OS containment boundary around the workload; our command approval gate covers only the initial launch and operations explicitly routed through our trusted adapters.

Do not claim universal command interception unless a separate, tested process-creation enforcement mechanism exists.

## 6. Host compatibility

- MXC documents Windows 11 24H2 or later for ProcessContainer.
- The actual ProcessContainer tier and feature support depend on the installed Windows build and host capabilities.
- The application must call MXC runtime discovery and request-aware probe rather than infer support from the marketing version string.
- Some host preparation or elevated setup may be required. Surface the precise MXC diagnostic; never elevate or change host security settings silently.

## 7. Official references

- [Microsoft Execution Containers (MXC)](https://github.com/microsoft/mxc)
- [MXC .NET SDK quickstart](https://learn.microsoft.com/en-us/agent-framework/sandbox/quickstart)
- [MXC .NET API reference](https://github.com/microsoft/mxc/tree/v1.0.1/docs/api-reference/dotnet/v1)
- [MXC ProcessContainer networking](https://github.com/microsoft/mxc/blob/v1.0.1/docs/backends/process-container/networking.md)
- [MXC Windows OS-version support](https://github.com/microsoft/mxc/blob/v1.0.1/docs/backends/process-container/os-version-support.md)
