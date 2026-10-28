# PHP, Composer, packages and upgrade tooling

## Runtime compatibility is an intersection, not a floor

Record separate runtimes for: application/FPM, CLI/cron/workers, test suite and upgrade tools. For each proposed hop evaluate **source patch + target patch + all locked packages + root PHP constraint + extensions/system libraries + Composer/plugins + dev tools + deployment order**. A framework minimum is not the app's minimum, maximum, or supported test range.

- Use the official support matrix in [versions.md](versions.md) and exact target-patch `composer.json`. Initial-release snapshots document historical floors; later patches can add PHP compatibility or change transitive requirements.
- Prefer a PHP-only transition first **when the current app and its complete dependency set support both PHP versions**. If not, retain the old baseline runtime and perform a bounded framework/runtime transition. Do not assume a Laravel 5.8 app can run on PHP 8.3; validate the exact framework patch and complete lock.
- If code deploys before the runtime switch, the candidate artifact must run on both old and new runtimes. Syntax, root constraints and the **same lock** must support that order. Otherwise coordinate the switch and retain an old-compatible rollback artifact/runtime.
- `config.platform.php` tells the resolver to simulate a chosen deployment PHP; it does not install PHP or prove actual extensions. It must represent a verified deployment constraint, not the developer laptop. A trial platform is explicitly provisional. Run real-platform checks on the actual artifact/runtime before acceptance.
- Avoid broad “PHP 8 compatible” claims: 8.0, 8.1, 8.2, 8.3, 8.4 and 8.5 have different incompatible changes and deprecations. Read **every intervening PHP migration guide**, incompatible changes plus deprecated features. Sources: [migration index](https://www.php.net/manual/en/appendices.php), [supported PHP](https://www.php.net/supported-versions.php), [EOL PHP](https://www.php.net/eol.php).

## Isolated Docker runtimes and Composer safety

A host that only has a modern PHP (for example Homebrew PHP 8.4) plus Docker cannot supply legacy PHP bridges locally. Use one reviewed runtime image per approved PHP, based on `php:<exact-version>-cli`; pin each PHP and Composer tag/digest when actually building or running. An approved continuous range authorizes only an isolated upgrade worktree and local per-hop commits—not push, pull request or deployment. Do not use host Composer or share `vendor/` between PHP versions or working trees.

Build a separate derived image for each approved PHP version. `php:<version>-cli` is only a base: install the exact PHP extensions and OS libraries required by the source/target lock and tooling; never assume the base image is sufficient. Copy Composer into that PHP runtime so Composer itself executes under the selected PHP:

```dockerfile
FROM php:<exact-version>-cli@sha256:<php-image-digest>
# For PHP below 7.2.5:
COPY --from=composer:2.2@sha256:<composer-image-digest> /usr/bin/composer /usr/local/bin/composer
# For PHP 7.2.5 or later, REPLACE the preceding COPY with:
# COPY --from=composer:2@sha256:<approved-composer-2-image-digest> /usr/bin/composer /usr/local/bin/composer
# Install the lock-derived PHP extensions and OS libraries in this image.
```

Resolve exact supported image tags and digests at execution time; replace placeholders, and use one build/image per approved PHP. Build each from a reviewed tooling-only context, not the application tree:

```bash
docker build --file /approved/tooling/Dockerfile.php-<version> --tag approved-php-runtime:<version> /approved/tooling
```

### Archived Debian bases in legacy PHP images

Inspect the pinned image's Debian codename before installing lock-required OS libraries/PHP extensions. Legacy PHP 7.x images based on **stretch** or **buster** can fail `apt-get` with HTTP 404 because their suites moved off `deb.debian.org` / `security.debian.org`. Point that engineering image's reviewed APT source definitions at **archive.debian.org**, not a current Debian suite with incompatible libraries. Choose only the pair matching the actual base; do not mix distributions:

```text
# Stretch base only:
deb http://archive.debian.org/debian stretch main
deb http://archive.debian.org/debian-security stretch/updates main

# Buster base only (instead of the Stretch pair):
deb http://archive.debian.org/debian buster main
deb http://archive.debian.org/debian-security buster/updates main
```

Keep **Release/InRelease signature and package-hash verification enabled**. The HTTP examples still require that authentication; prefer HTTPS when the old image has a working reviewed CA/transport stack, and never bypass TLS verification to bootstrap it. Review all existing source files, including deb822 `.sources`; replace only obsolete entries for the actual archived suite, and remove unsupported update-suite entries only after checking archive availability. Do not blindly substitute a different OS release or concatenate both example pairs.

An expired `Valid-Until` may require a narrowly scoped **owner-approved exception** for an isolated, non-production engineering image. Record the image/digest, exact source, reason and approval, then use a per-source option such as the following only if needed and supported by that APT version:

```text
deb [check-valid-until=no] http://archive.debian.org/debian stretch main
```

This relaxes metadata freshness/replay protection, **not GPG authentication**; do not disable it globally or copy it into a final deployment image. Never use `trusted=yes`, `--allow-unauthenticated`, `AllowInsecureRepositories`, or any GPG bypass. For missing/invalid signing keys, provision a matching keyring only from reviewed trusted artifacts and verify provenance/fingerprints; stop if signatures cannot be established. Archived repositories do not restore security maintenance. PHP 7.4 CLI tags using bullseye also need support review: Debian bullseye LTS ended in August 2026 even if its repositories still respond. These old images are temporary isolated bridges, not production recommendations. This suite update does not run Docker builds or APT installs.

### Composer/runtime command phases

Composer 2.2 LTS supports legacy PHP 5.3.2+; current Composer requires PHP 7.2.5+. Laravel 10+ requires Composer 2.2.0+ / runtime API `^2.2`. These are tool/framework floors, not guarantees that all packages and plugins accept a combination. Do not `self-update` the host's global Composer. Composer 1 and old repositories/TLS can be retrieval blockers, not reasons to disable security checks.

Before Composer, inspect root scripts, plugins, custom repositories and hooks. Disable plugins and scripts in Composer commands; review any hook or test bootstrap before explicitly running it, even offline. Do not print auth files or credential-bearing URLs. Do not mount SSH directories or Composer auth files, or pass credentials, without explicit approval. If private repository access is needed, stop and obtain approval for an approved secret-delivery method. Keep trusted tooling outside downloaded/untrusted directories.

The following Bash example is for one approved isolated tree and one built runtime image. Repeat with a different writable tree and runtime image for every B/P/C tree and every PHP version. Use a fresh temporary `COMPOSER_HOME`; do not share `vendor/` or Composer state between trees/runtimes. The networked commands use Docker's bridge network for approved package resolution; this network has egress.

```bash
APP=/absolute/path/to/one-isolated-tree
RUNTIME_IMAGE=approved-php-runtime:<version>
TARGET_FRAMEWORK='^<target-major>.0'
TARGET_PHP='<target-php-constraint>'
COMPOSER_HOME_HOST="$(mktemp -d)"
REPORT_DIR="$(mktemp -d)"
chmod 700 "$COMPOSER_HOME_HOST" "$REPORT_DIR"
test -d "$APP" && test -w "$APP"

run_runtime() {
  network="$1"
  shift
  docker run --rm --network "$network" \
    --user "$(id -u):$(id -g)" \
    -e COMPOSER_HOME=/tmp/composer \
    -v "$APP:/app" \
    -v "$COMPOSER_HOME_HOST:/tmp/composer" \
    -v "$REPORT_DIR:/reports" \
    -w /app "$RUNTIME_IMAGE" "$@"
}

# Networked metadata/constraint checks and an approved dry-run only.
run_runtime bridge composer --no-plugins --no-scripts validate --strict
run_runtime bridge composer --no-plugins --no-scripts prohibits laravel/framework "$TARGET_FRAMEWORK" --tree
run_runtime bridge composer --no-plugins --no-scripts prohibits php "$TARGET_PHP" --tree
run_runtime bridge composer --no-plugins --no-scripts update laravel/framework vendor/package --dry-run -W

# Only after approving the dry-run's scope, resolve the same named package set.
# Skip this update when reproducing a baseline: its lock must remain unchanged.
run_runtime bridge composer --no-plugins --no-scripts update laravel/framework vendor/package -W

# Install the reviewed lock in this isolated tree; plugins and scripts stay disabled.
run_runtime bridge composer --no-plugins --no-scripts install --no-interaction --prefer-dist

# Check the actual selected PHP/extensions, then run tests without network access.
run_runtime none composer --no-plugins --no-scripts check-platform-reqs
run_runtime none vendor/bin/phpunit --log-junit /reports/phpunit.xml
```

Replace every placeholder with the approved exact target, package names, host paths and image built for that runtime. `vendor/package` stands for explicitly named approved packages; do not replace the dry-run with an unrestricted update. Networked resolution/install contacts configured package endpoints, so do not run it now or against live endpoints absent explicit authorization. For tests requiring DB/Redis, use throwaway services and attach only the test container and those services to a Compose network declared `internal: true`; publish no service ports and attach no other networks. Compose's default network has egress. Use `--network none` when tests need no services. Network isolation limits egress, not filesystem effects, so review test/bootstrap hooks before explicit execution.

Run containers as the host UID/GID and ensure the isolated tree, its `vendor/` directory, temporary Composer home and report directory are writable by that user. This keeps new files owned by the caller; correct ownership only within the isolated tree, never with a blanket recursive permission change. When a usable lock exists, install it rather than resolving a new baseline. An install with plugins/scripts disabled may not create a bootable deployment if approved installers or discovery hooks are required; review each necessary hook, obtain explicit authorization, run it only in the isolated candidate, and re-check vendor consistency. Never blanket-allow plugins, disable insecure-package blocking globally, ignore platform requirements or delete a lock to bypass a conflict.

`check-platform-reqs` checks the actual selected container PHP/extensions and ignores `config.platform`; run it after install, with dev requirements on the test runtime and production requirements separately if needed. Record root constraints, resolved versions, changed transitives/additions/removals/downgrades, platform constraints and why each change is necessary. `-W` permits selected package dependencies to update even when they are root requirements; review the resulting scope. No broad unrestricted `composer update` by default.

For security auditing, check command support in the selected Composer version: Composer 2.2 LTS lacks some modern options, especially audit behavior. When needed, run a newer compatible trusted audit tool against the candidate lock in an isolated tool runtime; it may use the network and must not silently mutate the lock/config. Record tool version, lock hash and advisory retrieval date. If unavailable, security status is UNVERIFIED, not clean.

## Package compatibility ledger

For every relevant package maintain:

| Package / kind | Locked → candidate | PHP / extensions | Maximum supported Laravel major / blocked hop | Upstream source | Required change / callers | Gate / security status |
|---|---|---|---|---|---|---|
| <direct/transitive/dev> | <versions> | <requirements> | <highest major / first blocked boundary, or unknown> | <constraint/guide> | <approved disposition + file:line> | <checks + separate advisory result> |

Choose the smallest compatible maintained release. Package-specific data migrations, provider changes, config defaults, storage formats and rendered output matter as much as `illuminate/*` constraints. A successful solve proves constraint consistency, not behavior. Custom/private packages need maintainer/source review; do not guess support.

Typical investigations, **not mandatory major-version pins**:

- First-party: UI/auth traits, Sanctum, Passport, Socialite, Horizon, Telescope, Scout, Cashier, Octane, Livewire/Inertia and their published migrations.
- Infrastructure: Fideloper/proxy, Fruitcake CORS, Predis/phpredis, Flysystem adapters/S3, Monolog/Slack/log handlers, SwiftMailer/Symfony Mailer, Pusher/Vonage.
- Business outputs: Barryvdh Dompdf/Snappy, dompdf/wkhtmltopdf binaries/fonts, Maatwebsite Excel/PhpSpreadsheet/PhpWord, ZIP/image libraries, Carbon and locale dependencies.
- Operations: Spatie backup/db-dumper/permission/sitemap, notification-channel packages and third-party API clients.
- Dev: PHPUnit/Pest/Mockery, Ignition/Collision, Faker, BrowserKit/Dusk, PHPStan/Larastan, Rector and build tooling.

An abandoned package is a maintenance warning, not automatically a CVE or a hard compatibility blocker. Record its maximum supported Laravel major or the exact blocked hop based on upstream evidence; classify it as a hard blocker only when an incompatible constraint/behavior prevents that hop and no approved resolution exists. Check current advisories and whether a proposed replacement is maintained. A reused PHP namespace or version number can refer to a different library; verify package identity, maintainer, repository and source before applying compatibility claims. Do not remove packages merely because static search found no obvious class name: providers, discovery, Blade, configuration and scripts may use them.

When a required major changes package defaults, diff tracked published config **and unpublished upstream defaults**. Never force-publish over customized files. Test backup notification classes, PDF remote assets, queue/session payloads and other indirect effects. Optional package modernization belongs in a separate scoped step; a critical security remediation is not deferred silently.

## PHP semantic hotspots

Read official migration guides for the actual span. Pay special attention to removed PHP 5-era APIs and `each`/`create_function`/curly-brace offsets, throwable/error handling and return signatures; loose number/string comparisons and `switch`/non-strict searches in PHP 8; named-argument effects on associative `call_user_func_array`; resource-to-object APIs; null-to-internal scalar deprecations; dynamic properties in PHP 8.2; implicit-nullability deprecations in PHP 8.4; and PHP 8.5 library/helper collisions. Do not blanket-replace `==` with `===` or `empty()`—write down the real input types/truth table first.

DB fetch types depend on PDO driver, emulated/native prepares and extensions. Validate actual JSON/business types rather than assuming every numeric value stays a string. Deprecation ≠ immediate removal; keep a separate remediation list and do not hide warnings with broad suppression.

## Rector, Shift and Boost: optional aids

- Reuse existing tooling. Modern Rector/rules can require PHP newer than the legacy app; keep it in an approved isolated tool project if needed, with output targeting the app's actual runtime. Do not alter the immutable baseline lock to make a scanner executable.
- Read installed `rector/rector` and `driftingly/rector-laravel` metadata and [upstream docs](https://github.com/driftingly/rector-laravel). Set constants/APIs change and some documented rules may be unreleased. Do not invent `LARAVEL_130` or use cumulative-to-13 sets before confirming installed availability and approving scope.
- Select only next-hop PHP/Laravel compatibility rules, run dry-run first, inspect every source/caller/config change, then apply required fixes. No blanket style/dead-code/attribute/skeleton/test rewrites. A clean Rector run is not behavioral proof.
- Laravel Shift is a paid external service; assess cost vs manual work but obtain permission before access/payment/source upload. Review every generated change and run the same gates. Chained automation does not remove any intermediate-guide obligations.
- Laravel Boost's Laravel 13 upgrade prompt is an optional first-party helper for an appropriate Laravel 12 app; the official guide names Boost ^2.0. Do not install it into Laravel 5 or add it solely because the guide lists it. Tool use never substitutes for evidence or authorization.
