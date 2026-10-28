# Sources, provenance and maintenance

## Authority order

1. **Laravel target upgrade guide**, official release notes/support policy, framework release/tag/changelog/source and exact Composer metadata.
2. **PHP / Composer / database / package maintainer** migration and support documentation for the versions actually used.
3. Repository source, matching lock/artifact and reproducible application evidence.
4. Community skills: prompts for investigation, never authoritative version/support/security evidence.

When sources disagree, distinguish version/patch, framework vs new-skeleton defaults, manifest constraints vs official tested support, and documented intention vs actual observed behavior. Do not resolve disagreements by choosing whichever makes the upgrade easier.

## Bundled official archive

Edition: **2026-10-26**. [source-manifest.json](source-manifest.json) records **70 files / 17 version lines**: the original 69 snapshots are unchanged and not refreshed; one tagged source snapshot was added. Each entry has repository, immutable commit URL, local path, SHA-256 and byte count:

- 17 full `upgrade.md` + 17 full `releases.md`: Laravel 5.0–5.8 and 6.x–13.x.
- 17 initial framework release-tag `composer.json` snapshots: exact historical PHP/runtime dependency constraints.
- 15 framework changelogs: 5.2–5.8 and 6.x–13.x. Guessed5.0/5.1 `CHANGELOG-5.x.md` URLs returned 404; **no changelog is fabricated for them**. Use official historical framework tag/release history for a precise patch question.
- Laravel 13.38.0 framework Composer metadata as an additional observed current-release example.
- Official Laravel documentation and framework MIT license files, preserved below.
- [TransformsRequest at v13.38.0](official/13.x/TransformsRequest-v13.38.0.php), pinned to framework commit `c42f9abd4a3d2f9a3cd6be109255ddce8092ceb8`: source evidence for the undocumented 20 MiB cumulative input-key limit / HTTP 413. The introduced behavior must be distinguished from later Unreleased parser changes.

All archived files were fetched from pinned official GitHub URLs. The actual URL pattern is:

```text
https://raw.githubusercontent.com/laravel/docs/<commit>/upgrade.md
https://raw.githubusercontent.com/laravel/docs/<commit>/releases.md
https://raw.githubusercontent.com/laravel/framework/<commit>/composer.json
```

A branch resolves to a root tree; **do not insert `/5.8/` or `/13.x/` after the commit**. Framework changelog filenames vary; use the manifest's exact URL. Snapshots retain upstream formatting, historical text, placeholders and links. Old guide sections can discuss4.x or earlier patches; the suite does not claim those are new required changes for every5.x app.

Offline integrity check (Python 3.9+, no application code or network):

```bash
python3 -I <laravel-upgrade-dir>/scripts/check.py
```

This checks hashes, coverage, local suite links, frontmatter and inventory safety fixtures. It does **not** certify factual completeness, live URLs/advisories, application compatibility or actual rollback.

## Live canonical Laravel sources

- [Official docs repository](https://github.com/laravel/docs): choose the target branch and read its full `upgrade.md` / `releases.md`.
- [Laravel 13 upgrade](https://laravel.com/docs/13.x/upgrade) and [release/support notes](https://laravel.com/docs/13.x/releases). Public docs URLs may redirect to `/framework/docs/...`; archived raw files avoid version redirects.
- [Framework repository/releases](https://github.com/laravel/framework/releases), [13.x changelog](https://github.com/laravel/framework/blob/13.x/CHANGELOG.md), [observed13.38.0 tag](https://github.com/laravel/framework/releases/tag/v13.38.0).
- [Application skeleton comparison](https://github.com/laravel/laravel/compare/12.x...13.x): compare selectively; skeleton changes are not automatically required framework changes.
- [Laravel 13 CSRF](https://laravel.com/docs/13.x/csrf), [deployment](https://laravel.com/docs/13.x/deployment), [queues](https://laravel.com/docs/13.x/queues), [cache](https://laravel.com/docs/13.x/cache), [session](https://laravel.com/docs/13.x/session), [database](https://laravel.com/docs/13.x/database).

Latest stable major observed was 13; latest released entry observed in the archived framework changelog was 13.38.0 on 2026-10-20. Never interpret “Unreleased” as an available package release, or freeze that patch as the right target forever.

## PHP sources

- [Supported versions](https://www.php.net/supported-versions.php), [EOL](https://www.php.net/eol.php), [manual migration index](https://www.php.net/manual/en/appendices.php).
- PHP 5.4→5.5: the live `migration55.php` URL returned 404 in this research. Verified historical **official php/doc-en** source: [migration55.xml at 0d77f05](https://github.com/php/doc-en/blob/0d77f05f4541d8a977ebe4f96965dec4e10d6b33/appendices/migration55.xml); inspect linked incompatible/deprecated sections in that revision for an actual legacy runtime bridge. Do not present the removed live URL as working.
- [5.6](https://www.php.net/manual/en/migration56.php), [7.0](https://www.php.net/manual/en/migration70.php), [7.1](https://www.php.net/manual/en/migration71.php), [7.2](https://www.php.net/manual/en/migration72.php), [7.3](https://www.php.net/manual/en/migration73.php), [7.4](https://www.php.net/manual/en/migration74.php), [8.0](https://www.php.net/manual/en/migration80.php), [8.1](https://www.php.net/manual/en/migration81.php), [8.2](https://www.php.net/manual/en/migration82.php), [8.3](https://www.php.net/manual/en/migration83.php), [8.4](https://www.php.net/manual/en/migration84.php), [8.5](https://www.php.net/manual/en/migration85.php).

For each intervening version read **backward-incompatible changes, deprecated features, changed functions, extensions and runtime/config changes**, not only new features. The Laravel archive does not bundle all PHP/database/package docs; those remain explicit live/historical-source dependencies.

## Composer and tooling sources

- [Composer system requirements](https://getcomposer.org/doc/00-intro.md), [CLI and command options](https://getcomposer.org/doc/03-cli.md), [platform dependencies](https://getcomposer.org/doc/articles/composer-platform-dependencies.md), [config.platform](https://getcomposer.org/doc/06-config.md#platform), [scripts](https://getcomposer.org/doc/articles/scripts.md), [plugins](https://getcomposer.org/doc/articles/plugins.md), [Composer 1→2](https://getcomposer.org/doc/articles/upgrade-1.x.md), [downloads](https://getcomposer.org/download/).
- [Carbon maintainer migration](https://carbon.nesbot.com/guide/getting-started/migration.html).
- [Rector CLI](https://getrector.com/documentation/cli-options), [Laravel community rules source](https://github.com/driftingly/rector-laravel). These are maintainer sources for tools, not Laravel-official rules or behavioral guarantees. Check the installed release rather than latest README alone.
- [Claude Code skill format](https://code.claude.com/docs/en/skills): a skills directory such as `~/.claude/skills/` (user) or `.claude/skills/` (project), progressive references, invocation controls. No permissions/hooks were changed to install this suite.

Database/package guides must be added to the **specific app's evidence ledger** when relevant. Avoid a static universal package-pin matrix that will silently rot.

## Community inputs and licensing

Reviewed community inputs, upstream revisions, useful ideas and corrections are documented in [community-review.md](community-review.md). Third-party instructions/scripts were inspected as reference data; no downloaded script or installer was executed. Their implementation/text is not vendored into this suite. The suite's procedures and Python tools are newly written; project-specific claims are not labeled verified merely because an input used a checkmark.

Official snapshots are redistributed under their retained licenses: [Laravel docs MIT](official/laravel-docs-license.md), [Laravel framework MIT](official/laravel-framework-license.md). Preserve these and upstream copyright notices when sharing. Project-specific identities, paths and historical findings live outside this reusable suite in private notes; never upload private source, notes or evidence without permission.

## Refresh procedure — explicitly requested maintenance only

1. Determine the request date and official latest stable release/support policy. Do not silently change the suite's target during an application hop.
2. Resolve relevant official branch/tag to a commit, then fetch into a **new empty isolated download directory**. Keep trusted scripts outside it; never run downloaded code. Verify status/body, provenance and required license.
3. Diff the relevant guides/releases/changelogs and runtime metadata. **When the guide/changelog is silent about a reported behavior, inspect the exact release-tag source and its introducing commit before concluding “unverified” or absent.** Separate tagged release behavior from branch-tip/Unreleased changes; document source-verified but undocumented changes. Do not repeat the original input-key-limit mistake.
4. Preserve existing official snapshots byte-for-byte. Add a distinctly named new snapshot pinned to an immutable commit with its own URL/hash/byte count and actual retrieval provenance; retain old entries and update authored references only as justified. Do not overwrite old files or merely recompute a hash over unexplained edits.
5. Run the offline check, inventory fixture checks and affected workflow scenarios. If adding a future major, update hop coverage, tests and current references together. A requested refresh must not start an app upgrade or index update.
6. If live access fails, retain the last proven archive, disclose its edition and mark current support/advisory checks unavailable. Do not claim fresh security status from old snapshots.
