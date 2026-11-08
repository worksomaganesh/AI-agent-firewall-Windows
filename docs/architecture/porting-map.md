# Linux-to-Windows porting map

This document compares the existing [Linux-first reference repository](https://github.com/worksomaganesh/ai-agent-firewall) with the Windows implementation. The source repository is a reference; this repository is developed independently.

| Existing Linux component | Existing job | Windows direction | Port status |
|---|---|---|---|
| policy/schema.py | Strict versioned Pydantic schema | Reuse the policy model where portable; keep a virtual /workspace policy namespace and Windows-aware target handling | Not started |
| policy/parser.py | Safe YAML, duplicate-key and unknown-field rejection | Reuse with regression tests | Not started |
| policy/engine.py | Deny > approval > allow > default-deny decisions | Preserve precedence; rewrite path matching, case semantics, executable resolution and Windows command parsing | Not started |
| audit/events.py | Event schema and canonical hashes | Reuse; define a Windows AppContainer enforcement mode | Not started |
| audit/logger.py | Thread-safe hash-chained JSONL | Reuse; select secure Windows session storage and file ACLs | Not started |
| audit/verifier.py | Chain, sequence and HMAC verification | Reuse and extend Windows tests | Not started |
| audit/report.py | Human-readable report | Replace Linux-specific descriptions and report Windows controls actually installed | Not started |
| simulator.py | Deterministic mock-agent simulation | Reuse with Windows-path and policy fixtures | Not started |
| sandbox/bwrap.py | Bubblewrap startup, preflight and Linux resource limits | Replace with Python supervisor + Windows native host launcher | Not started |
| sandbox/seccomp.py | Seccomp-BPF syscall restrictions | No direct port; Windows AppContainer and WFP enforce different boundaries | Not started |
| sandbox/guard.py | Mediated action gate and approval revalidation | Preserve the model; Windows host approval channel | Not started |
| sandbox/approval.py | Host /dev/tty one-use approvals | Replace terminal access and I/O handling; never trust child stdin | Not started |
| sandbox/workspace.py | Secret-aware Linux workspace copy | Rewrite for NTFS, DACLs, reparse points, junctions, ADS, device names and hard links | Not started |
| sandbox/snapshot.py | File manifests and diffs | Rewrite without following Windows reparse points; record Windows file metadata | Not started |
| sandbox/workspace_tools.py | Policy-gated read/write/delete helpers | Rebuild with handle-based Windows path/file operations and race tests | Not started |
| sandbox/proxy.py | HTTP/HTTPS destination proxy over Unix socket | Keep destination-policy logic where portable; host loopback listener, WFP package-SID enforcement and Windows-specific socket lifecycle | Not started |
| sandbox/guest_bridge.py | Linux loopback-to-Unix-socket bridge | Likely remove; agent connects to the protected host loopback proxy directly | Not started |
| cli.py | CLI commands and Linux run wiring | Keep the useful operator command surface; remove every Bubblewrap/Linux-only assumption | Not started |
| Linux CI workflow | Linux kernel sandbox tests and packaging | Add Windows CI and real enforcement tests on Windows runners | Not started |

## Reusable guarantees to preserve

1. Unknown policy fields, duplicate YAML keys, malformed requests and unknown actions fail closed.
2. Explicit deny overrides approval and allow; unmatched actions default to deny.
3. Approval is exact-target, one-use, expiring and revalidated immediately before the action.
4. Original source workspace is never the agent's writable working directory.
5. The session evidence includes an auditable record, manifests, diff and report.
6. A required sandbox setup failure never falls back to running the target command unsandboxed.
7. Tests exercise observed OS behaviour, not only argument construction.

## Linux assumptions that must not leak into Windows

- POSIX /workspace is a logical policy namespace, not a physical Windows path.
- posixpath, shlex, POSIX mode bits and Linux symlink assumptions are not valid substitutes for NTFS/Win32 semantics.
- Bubblewrap, namespaces, Seccomp-BPF, resource.setrlimit, /dev/tty, Unix sockets, and Linux mount flags are not Windows controls.
- A policy decision made in Python is not an OS enforcement event unless a native Windows control actually enforces it.
- Proxy environment variables alone do not prevent direct-socket bypass.

## Migration order

1. Freeze reference behaviour with portable policy, audit and simulation tests.
2. Extract the portable modules without copying the Linux runner.
3. Introduce a Windows path/command normalization layer and Windows-specific default policy.
4. Implement workspace staging and ACL isolation.
5. Implement AppContainer launch and Job Object containment.
6. Implement WFP network restrictions and the host proxy path.
7. Port approval, session review/export and reports.
8. Add Windows adversarial tests, CI, packaging and user documentation.
