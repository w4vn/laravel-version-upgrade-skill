# Changelog

All notable changes to this project are documented here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [1.0.1] - 2026-10-28

### Added

- Contributor documentation: `CONTRIBUTING.md`, `AGENTS.md` (agent rules and pull request review order), `SECURITY.md`, this changelog, and issue and pull request templates.
- `tools/add_snapshot.py`, which pins an official upstream file and records its manifest entry.
- `tools/verify_sources.py`, which verifies snapshot content, the folder/version match, and that each commit is reachable from the official branch.
- CI runs `check.py` on Python 3.9 and the latest Python, and runs source verification when snapshots or the manifest change.
- `check.py` rejects zero-width and bidi control characters in skill documents.

## [1.0.0] - 2026-10-28

### Added

- Four skills (`laravel-upgrade`, `laravel-upgrade-audit`, `laravel-upgrade-step`, `laravel-upgrade-verify`) for upgrading Laravel 5.0–5.8 to 13.x hop by hop.
- 70 pinned official reference files (edition 2026-10-26, Laravel 13.38.0), `inventory.py`, `compare_junit.py`, `check.py`, and a CI workflow.
