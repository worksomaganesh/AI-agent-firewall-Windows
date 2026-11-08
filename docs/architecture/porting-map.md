# Linux-to-Windows porting map

This document maps the existing [Linux-first reference repository](https://github.com/worksomaganesh/ai-agent-firewall) to the separate Windows implementation.

| Existing Linux component | Existing job | Windows direction | Current status |
|---|---|---|---|
| `policy/schema.py` | Strict Pydantic policy model | Retain portable schema; add Windows path and command semantics | Implemented baseline |
| `policy/parser.py` | Safe YAML, duplicate-key and unknown-field rejection | Retain with Windows fixtures | Implemented baseline |
| `policy/engine.py` | Deterministic decisions | Retain precedence; use Windows command tokenizer and later IPv6/path normalization fixes | Implemented baseline |
| `audit/events.py` | Event schema and hashing | Retain; use Windows ProcessContainer enforcement mode | Implemented baseline |
| `audit/logger.py` | Hash-chained JSONL | Retain; secure Windows session directory permissions still to add | Implemented baseline |
| `audit/verifier.py` | Audit verification | Retain | Implemented baseline |
| `audit/report.py` | Human-readable report | Windows-specific enforcement disclosures | Implemented baseline |
| `simulator.py` | Deterministic mock-agent workflow | Retain and extend Windows scenarios | Implemented baseline |
| `sandbox/bwrap.py` | Bubblewrap startup, namespace setup and Linux resource limits | Replace with .NET MXC ProcessContainer bridge and request-aware probing | Planned |
| `sandbox/seccomp.py` | Linux Seccomp-BPF syscall restrictions | No direct port; Windows containment supplied by MXC ProcessContainer | Replaced by integration design |
| `sandbox/workspace.py` | Secret-aware workspace copy | Rebuild for NTFS, DACLs, reparse points, ADS, device names and hard links | Planned |
| `sandbox/snapshot.py` | Workspace manifests and diffs | Rebuild for Windows file attributes and reparse points | Planned |
| `sandbox/proxy.py` | Host-side HTTP/HTTPS policy proxy | Port destination policy; identity-bound AppContainer/package proxy peer with MXC proxy-only egress | Planned |
| `sandbox/guest_bridge.py` | Loopback-to-UNIX-socket bridge | Remove; MXC routes agent proxy traffic to the configured loopback endpoint | Replaced by integration design |
| `sandbox/approval.py` | Host `/dev/tty` approval prompts | Windows host-only approval channel | Planned |
| `sandbox/guard.py` | Mediated action gate | Retain the model and connect it to trusted Windows adapters | Planned |
| `sandbox/workspace_tools.py` | Policy-gated file helpers | Rebuild with handle-based Windows file access and race tests | Planned |
| `cli.py` | User-facing commands and Linux run wiring | Keep current core CLI; add host discovery, staging and guarded run commands | Implemented core only |
| Linux CI | Linux sandbox execution tests | Windows CI plus real MXC ProcessContainer enforcement tests | CI workflow added; first run needs lint fixes |

## Guarantees to preserve

1. Unknown policy fields, duplicate YAML keys, malformed inputs and unknown actions fail closed.
2. Explicit deny overrides approval and allow; unmatched actions default to deny.
3. Approval is exact-target, one-use, expiring and revalidated immediately before the mediated action.
4. The source project is never the agent's writable working directory.
5. Session evidence includes an audit chain, manifests, diff and report.
6. Required sandbox setup failure never falls back to an ordinary unsandboxed process.
7. Windows enforcement tests assert actual access/connect outcomes, not only constructed request values.

## Linux assumptions that must not leak into Windows

- POSIX `/workspace` is a logical policy namespace, not a physical Windows path.
- `posixpath`, `shlex`, POSIX mode bits and Linux symlink assumptions cannot substitute for NTFS/Win32 path semantics.
- Bubblewrap, namespaces, Seccomp-BPF, `resource.setrlimit`, `/dev/tty`, UNIX sockets and Linux mount flags are not Windows controls.
- A Python policy decision is not OS enforcement unless a Windows containment control enforces it.
- Proxy environment variables alone do not prevent direct-socket bypass.
- MXC's identity-less loopback proxy mode is weaker and is not an acceptable silent fallback for the secure release path.

## Migration order

1. Portable core and regression tests — started.
2. .NET 8 MXC bridge, host discovery and request-aware offline ProcessContainer probe.
3. Windows-safe private workspace staging, ACL and MXC filesystem policy.
4. Identity-scoped AppContainer proxy process and MXC proxy-only egress.
5. Approval broker, session audit, review/export/discard.
6. Windows adversarial integration tests, packaging and clean-machine installation.
