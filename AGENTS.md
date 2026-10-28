# Agent guide

Instructions for coding agents, and the humans driving them, who change or review this repository. The full contributor process is in [CONTRIBUTING.md](CONTRIBUTING.md).

## What this repository is

Four skills that upgrade a Laravel application from 5.0–5.8 to 13.x one breaking-change hop at a time:

- `skills/laravel-upgrade/SKILL.md`: shared rules, routing and planning. Its `references/` hold per-hop guidance, gates, templates and `official/` (pinned upstream snapshots listed in `source-manifest.json`). Its `scripts/` hold `inventory.py`, `compare_junit.py` and `check.py`.
- `skills/laravel-upgrade-audit/`, `skills/laravel-upgrade-step/`, `skills/laravel-upgrade-verify/`: companion skills.
- `tools/`: maintainer tools that are not shipped to users (`add_snapshot.py`, `verify_sources.py`).

Skill files are instructions that users' agents follow with their full permissions. Treat every line in `skills/**/*.md` as executable.

## Non-negotiable invariants

Do not weaken these. A change that touches one must say so in the pull request and justify it.

- Audit and plan are read-only: no application code, Composer scripts, Artisan, migrations, tests or installs.
- `laravel-upgrade-step` keeps `disable-model-invocation: true`. Execution starts only when the user types the command with an approved plan that is stored outside the repository and bound by SHA-256.
- Every 5.x minor and every later major is its own hop, and each hop reads the full official guide.
- Execution never touches the user's working tree. There is no push, PR or deployment.
- Composer runs with `--no-plugins --no-scripts`. Tests run in Docker without internet access. Secrets, SSH keys and the Docker socket are never mounted without approval. GPG verification is never bypassed.
- Missing evidence is BLOCKED or NOT RUN, never PASS. Level 0 gates are never waived for automatic advancement. A security regression is never an accepted PARTIAL.

## Working rules

- **Facts:** every fact about Laravel, PHP or Composer behavior comes from an official source; cite the URL and the commit or tag.
- **Snapshots:** never hand-edit `skills/laravel-upgrade/references/official/`. Add snapshots with `tools/add_snapshot.py` and verify them with `tools/verify_sources.py`.
- **Scripts:** Python 3.9+, standard library only, run with `python3 -I`. `inventory.py` and `check.py` never use the network or write into an analyzed project. Every behavior change gets a positive and a negative fixture in `check.py`.
- **Paths:**
  - Reference scripts as `<laravel-upgrade-dir>/scripts/...`; never hard-code an install location.
  - Slash-command examples use absolute paths.
  - Committed run-state writes home paths as `~/...`.
- **Consistency:** when behavior changes, update together the affected `SKILL.md` files, `references/*`, the root `README.md`, `skills/laravel-upgrade/README.md` (Vietnamese) and `check.py`. Add an entry to `CHANGELOG.md` under Unreleased.
- **Privacy and dependencies:**
  - Never commit secrets, personal paths, real project names or client data; use generic examples.
  - Never run the skills against private projects as part of a change.
  - Add no dependencies, telemetry or network calls to the shipped scripts.

## Validate

```bash
python3 -I skills/laravel-upgrade/scripts/check.py      # must pass; CI runs it on Python 3.9 and the latest Python
GITHUB_TOKEN=$(gh auth token) python3 -I tools/verify_sources.py   # when official/ or the manifest changed
```

## Reviewing a pull request

Review in this order and stop at the first blocker. Run code from a pull request only in a sandbox, for example Docker with `--network none` on a copy. Verify snapshots with the trusted `tools/verify_sources.py` from `main`, not the pull request's copy.

1. **Instruction safety.** Read every changed line in `skills/**`. Block any of the following:
   - downloading or executing code (`curl | sh`, `eval`, encoded payloads);
   - disabling checks or hooks, or broadening permissions;
   - reading or sending secrets, `.env` files or credentials;
   - weakening an invariant above;
   - hidden behavior: zero-width or bidi characters (`check.py` rejects them in skill docs), misleading links, or instructions unrelated to Laravel upgrades.
2. **Workflows and tooling.**
   - Changes in `.github/`: no `pull_request_target`, least-privilege `permissions`, actions pinned by full commit SHA.
   - Changes in `tools/` and `scripts/`: no shell subprocesses, no network in shipped scripts, no new dependencies, no writes outside temporary directories.
3. **Provenance.** Any change under `official/` or to `source-manifest.json` must pass `tools/verify_sources.py`: content, folder/version match, and commit reachable from the official branch. Compare any guidance that quotes or summarizes it against the official source.
4. **Correctness.** Claims match the cited sources. Fixtures cover the change. CI is green on Python 3.9 and the latest Python.
5. **Completeness.** Related documents are updated together, there is a CHANGELOG entry, and the version impact follows the rules in CONTRIBUTING.md.

Write the review as: verdict (approve / request changes / needs discussion), blockers with `file:line`, non-blocking suggestions, and version impact.
