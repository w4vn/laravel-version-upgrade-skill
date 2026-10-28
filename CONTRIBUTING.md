# Contributing

Thanks for helping improve these Laravel upgrade skills. Bug reports, corrections backed by official sources, support for new Laravel releases and tooling improvements are all welcome.

If you use a coding agent, point it at [AGENTS.md](AGENTS.md): it contains the same rules in a compact form.

## Ground rules

- **Official sources first.** Guidance about Laravel, PHP or Composer behavior must cite the official upgrade guide, release notes, documentation, or a framework commit or tag. Community posts can motivate a change but cannot be its only evidence.
- **Safety invariants stay intact.** The skills drive agents that act with the user's permissions. The invariants in [AGENTS.md](AGENTS.md#non-negotiable-invariants) are not negotiable without a discussion issue first.
- **No private data.** Never include secrets, personal paths, real project or company names, or client code in examples, fixtures, issues or pull requests.

## Development setup

You need Git and Python 3.9 or newer. There are no dependencies to install. Docker is optional; use it to run the checks on Python 3.9 locally.

```bash
git clone https://github.com/w4vn/laravel-version-upgrade-skill.git
cd laravel-version-upgrade-skill
python3 -I skills/laravel-upgrade/scripts/check.py
```

To try your changes in Claude Code, link the four directories under `skills/` into `~/.claude/skills/` (see the README) and start a new session.

## Making a change

1. Open an issue first for anything larger than a small fix, so the approach can be agreed before you write it.
2. Create a branch and keep the pull request focused on one topic.
3. Write commit messages in English, with an imperative subject of at most 72 characters (`Fix lock hash for empty objects`).
4. Update `CHANGELOG.md` under **Unreleased**.
5. Run the checks below and fill in the pull request template.

### Checks

```bash
python3 -I skills/laravel-upgrade/scripts/check.py
docker run --rm --network none -v "$PWD":/src:ro python:3.9-slim \
  sh -c 'cp -r /src /tmp/w && python3 -I /tmp/w/skills/laravel-upgrade/scripts/check.py'
GITHUB_TOKEN=$(gh auth token) python3 -I tools/verify_sources.py   # if snapshots or the manifest changed
```

CI runs `check.py` on Python 3.9 and on the latest Python. It also runs `verify_sources.py` whenever official snapshots, the manifest or the verifier change.

## Common contributions

### Fix a bug in a script

Add a fixture to `check.py` that fails without your fix, using generic data. Then fix the shared function rather than one caller. Scripts stay Python 3.9+, standard library only, with no network access and no writes into analyzed projects.

### Improve guidance

Change the relevant `references/*.md`, and the `SKILL.md` files if the workflow changes. Cite the official source in the pull request. Keep the root `README.md` and the Vietnamese `skills/laravel-upgrade/README.md` consistent.

### Add or refresh official snapshots

Never edit files under `skills/laravel-upgrade/references/official/` by hand. Pin each file to a full commit SHA on the official branch:

```bash
DOCS=$(gh api repos/laravel/docs/commits/14.x -q .sha)
python3 -I tools/add_snapshot.py laravel/docs "$DOCS" upgrade.md 14.x/upgrade.md 14.x "14.x docs"
GITHUB_TOKEN=$(gh auth token) python3 -I tools/verify_sources.py
```

`add_snapshot.py` downloads the file and appends its manifest entry (commit, URL, SHA-256, size). It refuses to overwrite an existing file. `verify_sources.py` checks the content and that the commit is reachable from the official branch named by `version`. `check.py` also asserts the total number of manifest entries in `reference_checks()`; update that count when you add or remove entries.

### Support a new Laravel major (example: 14)

1. **Research.** Read the new upgrade guide, release notes and support table, the framework `composer.json` at the `v14.0.0` tag and `CHANGELOG.md` on the `14.x` branch. If the guide is silent on a behavior, check the framework source at the tag.
2. **Snapshots.** Pin `14.x/upgrade.md` and `releases.md` (from `laravel/docs`), `framework-composer.json` (`v14.0.0`) and `framework-changelog.md` (`14.x`) with `add_snapshot.py`. Update the manifest header fields (`edition`, `retrieved_on`, `latest_stable_major_observed`, `latest_patch_changelog_observed`).
3. **Code.**
   - In `scripts/inventory.py`, extend `HOPS` (`range(6, 14)` → `range(6, 15)`) and change the default `--target`.
   - In `scripts/check.py`, extend the `versions` list and update fixtures that mean "latest target" (for example the `hop_path("v5.0.0", "13")` assertion) and the manifest count.
4. **Documents.** Find every mention with:

   ```bash
   grep -rn -E '\b13\b|13\.x|9-to-13|v13\.' --exclude-dir=official .
   ```

   Then decide for each whether it means "the latest target" (update it) or "Laravel 13 specifics" (keep it). Expect to touch:
   - `SKILL.md` descriptions and the target line, and the companion descriptions;
   - `references/versions.md`: hop path, PHP floors, support windows, runtime bridges;
   - a new 13 → 14 section in the modern hotspots file (rename the file and fix every link);
   - `references/sources.md`, `references/templates.md`, and both READMEs.
5. **Verify.** Run all checks. Also try a read-only audit and plan against a neutral sample application (for example a fresh `laravel/laravel` skeleton), never a private project.

## Pull requests and review

Fill in the template. Reviewers follow the order in [AGENTS.md](AGENTS.md#reviewing-a-pull-request): instruction safety, workflows and tooling, provenance, correctness, completeness. A pull request needs green CI and maintainer approval. Maintainers merge it, keeping you as the author, and handle releases.

## Versioning

Releases are annotated tags following SemVer:

- **MAJOR:** incompatible changes to how users install or invoke the skills.
- **MINOR:** support for a new Laravel major, guidance-changing data refreshes, or new features.
- **PATCH:** fixes and documentation.

The root README pins the latest tag in its manual install command.

## Security

Do not report vulnerabilities in public issues; follow [SECURITY.md](SECURITY.md).

## License

By contributing, you agree that your contributions are licensed under the [MIT License](LICENSE) of this repository.
