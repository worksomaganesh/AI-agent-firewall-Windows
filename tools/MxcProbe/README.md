# MXC host probe

This diagnostic utility reports the current Windows/.NET host information, MXC platform support, available backends, and the SDK's default ProcessContainer probe result.

It does **not** execute an agent command, change machine settings, elevate privileges, or claim that a backend is usable merely because it appears in discovery output.

## Prerequisites

- Windows 11 x64 or ARM64.
- .NET 8 SDK.
- NuGet access to the pinned `Microsoft.Mxc.Sdk` package.

## Run

From the repository root:

```powershell
dotnet run --project .\tools\MxcProbe\MxcProbe.csproj
```

Save the diagnostic output for the Phase 0 host-compatibility log. Redact usernames, local paths, machine identifiers, or other private details before sharing it publicly.

## Interpretation

- Platform support and backend discovery are host-level diagnostics.
- The ProcessContainer probe is the request-specific feasibility check.
- A failed or unsupported probe means the protected workload must not be launched.
- This initial probe uses the SDK's default request. The production bridge must later probe the exact filesystem/network/environment policy it intends to launch.
- A probe is not proof of successful enforcement. A harmless no-network integration execution and adversarial tests are still required.
