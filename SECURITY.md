# Security policy

## Reporting a vulnerability

Report vulnerabilities privately through GitHub: open the repository's **Security** tab and choose **Report a vulnerability**. Do not open a public issue or pull request for a security problem.

Include the affected file or skill, the version tag, what an attacker could achieve, and steps to reproduce with generic data. Maintainers aim to acknowledge reports within a week and will coordinate a fix and disclosure with you.

## Scope

In scope:

- Skill instructions that could make an agent act unsafely: running untrusted code, leaking secrets or credentials, weakening isolation, or bypassing approvals.
- Bypasses of the safety invariants listed in [AGENTS.md](AGENTS.md#non-negotiable-invariants).
- Flaws in `inventory.py`, `compare_junit.py`, `check.py` or the tools, such as unsafe parsing, path traversal, credential exposure in output, or code execution.
- Ways to get tampered or unofficial content accepted as an official snapshot.
- CI configuration weaknesses.

Out of scope:

- Vulnerabilities in Laravel, PHP or third-party packages themselves. Report those upstream.
- Security of applications being upgraded.

## Supported versions

Only the latest release tag receives fixes.
