# Security policy

## Project status

This project is under active development. The Windows ProcessContainer bridge, workspace staging and proxy enforcement are not yet complete or independently audited. Do not rely on this project as the only protection for credentials, sensitive workstations, customer data or production infrastructure.

## Reporting a vulnerability

Do not publish exploitable details in a public issue. Contact the maintainer privately through the security contact configured on the GitHub repository/profile.

Please include:
- A concise description and security impact.
- The affected commit SHA.
- Windows edition/build, architecture, Python version, .NET runtime and MXC SDK version.
- Exact policy and command used, with secrets removed.
- Minimal reproduction using a disposable workspace and synthetic credentials.
- Expected and observed behavior.
- Relevant redacted logs, audit events or test output.

## Testing rules

- Test only on systems and repositories you own or have explicit permission to assess.
- Use disposable workspaces and synthetic credentials.
- Do not access, modify or exfiltrate third-party data.
- Do not run destructive tests on shared or production systems.
- Never commit API keys, passwords, private keys, access tokens, customer records or sensitive logs.

## Security claim requirements

- A policy-engine decision is not automatically an OS-enforced restriction.
- Proxy environment variables are not a network boundary.
- The MXC host probe must validate the exact request before the command starts.
- The secure network mode requires an identity-scoped proxy peer; identity-less host-loopback access is not an acceptable silent fallback.
- The proxy binds only to the exact loopback address/port configured in the ProcessContainer request.
- Reparse points, junctions, hard links, alternate data streams, path traversal, case folding, device names and race conditions require dedicated tests.
- A skipped Windows enforcement test is not a passing test.
- A local hash chain is not immutable against an attacker who can replace the entire evidence bundle.
- Do not claim universal command interception, TLS payload inspection, production readiness or independent security certification without evidence.
