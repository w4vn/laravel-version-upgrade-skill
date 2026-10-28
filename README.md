# laravel-version-upgrade

Coding-agent skills that upgrade a Laravel application from any 5.x release (5.0–5.8) to 13.x one breaking-change hop at a time. They audit and plan read-only, run approved hops in an isolated worktree with per-version PHP runtimes, and verify behavior against the original baseline before moving on.

> Edition 2026-10-26: targets Laravel 13.x (latest observed patch v13.38.0). Re-check the latest release, support policy and security advisories before every real upgrade.

## What it does

The suite is four skills that share one rulebook:

1. **Audit** (`/laravel-upgrade-audit`): reads `composer.json`/`composer.lock`, runtime files and source without running the app. It reports locked versions, lock/manifest sync, PHP and package blockers per hop, advisories, test gaps and risky integrations.
2. **Plan** (`/laravel-upgrade`): sequences every hop (5.0 → 5.1 → … → 5.8 → 6 → … → 13), the PHP/Docker runtime for each hop, package replacements and verification gates. It collects every owner decision in one batch, saves the approved plan outside the repository with its SHA-256, and prints the run command.
3. **Execute** (`/laravel-upgrade-step`): runs one hop (`"8 -> 9"`) or a continuous range (`"5.8 -> 13"`) without touching your working tree. A range runs on `upgrade/laravel-<x>-to-<y>` in its own worktree, with one local commit per closed hop, a persistent three-round repair budget per hop and hard stops, and resumes from `docs/upgrade/run-state.json`. A single hop ends with a reviewed diff and commits only if you authorize it.
4. **Verify** (`/laravel-upgrade-verify`): compares the original baseline (B), the previous hop (P) and the candidate (C) through gate levels 0/1/2, plus security, rollout and rollback evidence.

Missing evidence is reported as BLOCKED or NOT RUN, never as PASS.

## Files

| Path | Purpose |
|------|---------|
| `skills/laravel-upgrade/SKILL.md` | Shared rules, routing and planning procedure |
| `skills/laravel-upgrade-audit/SKILL.md` | Read-only readiness audit |
| `skills/laravel-upgrade-step/SKILL.md` | Approved hop/range execution, resume and hard stops (manual invocation only) |
| `skills/laravel-upgrade-verify/SKILL.md` | Baseline/previous/candidate verification and readiness verdicts |
| `skills/laravel-upgrade/references/versions.md` | Hop path, PHP floors, support windows, runtime bridges |
| `skills/laravel-upgrade/references/legacy-5-to-8.md`, `modern-9-to-13.md` | Per-hop breaking-change hotspots |
| `skills/laravel-upgrade/references/runtime-and-dependencies.md` | Docker PHP runtimes, Composer safety, package ledger |
| `skills/laravel-upgrade/references/audit.md`, `verification.md`, `operations.md`, `templates.md` | Audit procedure, gate levels, cutover/rollback, report and run-state templates |
| `skills/laravel-upgrade/references/official/` | 70 pinned files from the official Laravel docs and framework repositories: upgrade guides, release notes, Composer manifests, changelogs, one framework source file and their licenses |
| `skills/laravel-upgrade/references/sources.md`, `source-manifest.json` | Source authority, per-file provenance (commit, URL, SHA-256) and refresh procedure |
| `skills/laravel-upgrade/references/community-review.md` | Community skills that were reviewed and the corrections adopted from them |
| `skills/laravel-upgrade/README.md` | Detailed guide in Vietnamese |
| `skills/laravel-upgrade/scripts/inventory.py` | Static inventory: locked versions, Composer content-hash sync, upgrade hints |
| `skills/laravel-upgrade/scripts/compare_junit.py` | Compares two JUnit reports by test identity and status |
| `skills/laravel-upgrade/scripts/check.py` | Offline self-check of the suite, plus a read-only run-state validator |
| `tools/add_snapshot.py`, `tools/verify_sources.py` | Maintainer tools to pin official files and verify their content and provenance; not shipped to users |
| `AGENTS.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, `CHANGELOG.md` | Agent rules and review order, contributor guide, community standards, vulnerability reporting, release history |

## Installation

Install all four skills together; they reference each other as sibling directories.

With the [Skills CLI](https://skills.sh):

```bash
npx skills add w4vn/laravel-version-upgrade-skill --skill '*' -g -a claude-code
```

Drop `-g` to install into the current project instead. `-a` can target other agents, but only Claude Code has been tested. For a private copy of this repository, you need access to it plus Git credentials for github.com (for example `gh auth setup-git`), or use the SSH URL `git@github.com:w4vn/laravel-version-upgrade-skill.git` as the source. Run `npx skills --help` for more options.

Manually, pinned to a version tag:

```bash
git clone --branch v1.0.1 https://github.com/w4vn/laravel-version-upgrade-skill.git
mkdir -p ~/.claude/skills
# Back up or remove existing copies of these four skills first.
for s in "$PWD"/laravel-version-upgrade-skill/skills/*; do ln -s "$s" ~/.claude/skills/; done
python3 -I ~/.claude/skills/laravel-upgrade/scripts/check.py
```

Open a new agent session afterwards. Before updating to a newer version tag, review the diff of `skills/`: these files are instructions your agent follows.

## Usage

In Claude Code:

```text
/laravel-upgrade-audit /absolute/path/to/app 13
/laravel-upgrade /absolute/path/to/app 13 plan
```

After you answer the decision batch and approve the plan, the skill prints a ready-to-run command such as:

```text
/laravel-upgrade-step /absolute/path/to/app "5.8 -> 13" "/absolute/path/to/approved-plan.md"
/laravel-upgrade-verify /absolute/path/to/app "B=<original> P=<previous> C=<candidate>" evidence-only
```

Re-issuing the same `/laravel-upgrade-step` command resumes an interrupted run. In other agents (untested), ask for the skill by name, for example "use the laravel-upgrade-audit skill on /path/to/app, target 13".

## Requirements

- A coding agent with shell access; Claude Code is the primary target.
- Git, and Python 3.9+ (standard library only) for the helper scripts.
- Docker for executing hops on PHP versions the host does not have.
- An application that uses Composer. Laravel 4.x and Lumen are out of scope. Without a `composer.lock`, the original baseline has to be reconstructed with owner approval.

## Design principles

- **Read-only until you invoke execution.** Audit and planning never run application code, Composer scripts, Artisan, tests or installs. In Claude Code, `disable-model-invocation` keeps the agent from starting `/laravel-upgrade-step` on its own; other agents rely on the skill's written rule.
- **No skipped boundaries.** Every 5.x minor is its own hop, and every hop reads the full official guide.
- **Isolation.** Execution never touches your working tree. Composer resolves with `--no-plugins --no-scripts`. Tests run in Docker without internet access (`--network none`, or an internal-only network for disposable DB/Redis). SSH keys, auth files and the Docker socket are not mounted unless you approve it. Nothing is pushed or deployed.
- **Evidence over claims.** Every gate compares B, P and C. A security regression can never be accepted as PARTIAL.
- **Pinned sources.** Bundled official files are pinned to immutable GitHub commit URLs, and `check.py` verifies their SHA-256 offline.

## Security

Skill files steer your agent, so treat updates like code: install from a version tag and review diffs before upgrading. Report vulnerabilities privately as described in [SECURITY.md](SECURITY.md).

## Contributing

Contributions are welcome; see [CONTRIBUTING.md](CONTRIBUTING.md). Coding agents should read [AGENTS.md](AGENTS.md), which also defines the pull request review order. Changes are listed in [CHANGELOG.md](CHANGELOG.md).

- CI runs `check.py` on Python 3.9 and the latest Python for every push to `main` and every pull request.
- CI runs `tools/verify_sources.py` whenever official snapshots or the manifest change. It checks content and that every pinned commit belongs to the official Laravel branch.
- To make `check.py` fail when private client or project names leak into the docs, set `LARAVEL_UPGRADE_PRIVATE_TERMS="name-one,name-two"`.

## License

MIT, see [LICENSE](LICENSE). Files under `skills/laravel-upgrade/references/official/` are © Taylor Otwell and distributed under their own MIT licenses ([docs](skills/laravel-upgrade/references/official/laravel-docs-license.md), [framework](skills/laravel-upgrade/references/official/laravel-framework-license.md)).

These skills guide an AI agent; they do not guarantee a correct upgrade. Review every change and test on staging before deploying.
