# Security policy

## Project status

This project is under active development. The Windows enforcement backend is not yet implemented or independently audited. Do not rely on it as the only protection for credentials, sensitive workstations, customer data, or production infrastructure.

## Reporting a vulnerability

Do not publish exploitable details in a public issue. Contact the maintainer privately through the security contact listed on the GitHub profile/repository settings.

Please include:
- A concise description and security impact.
- The affected commit SHA.
- Windows edition/build, architecture, Python version and native-host build.
- Exact policy and command used, with secrets removed.
- Minimal reproduction steps using a disposable workspace and synthetic credentials.
- Expected behaviour and actual behaviour.
- Relevant redacted logs, audit events or test output.

## Testing rules

- Test only on systems and repositories you own or have explicit permission to assess.
- Use disposable workspaces and synthetic credentials.
- Do not access, modify or exfiltrate third-party data.
- Do not run destructive tests on shared or production systems.
- Do not include real API keys, passwords, private keys, tokens, customer records or sensitive logs in issues or commits.

## Security claim requirements

- A policy-engine decision is not automatically an OS-enforced restriction.
- Proxy environment variables are not a network boundary.
- AppContainer and Job Objects must be tested on the supported Windows build.
- WFP filters must be observed blocking direct network paths and permitting only the intended broker path.
- Reparse points, junctions, hard links, alternate data streams, path traversal, case folding, device names and race conditions need dedicated tests.
- A skipped Windows enforcement test is not a passing test.
- A local hash chain is not immutable against an attacker who can replace the entire evidence bundle.
- Do not claim universal command interception, TLS payload inspection, production readiness or independent security certification without evidence.
