# Laravel 5.0 → 8: upgrade hotspots

This is a **triage map**, not a replacement for each full official upgrade guide. For every guide heading record applicability, source/callers, proposed fix or N/A rationale, and a verification case. Archived guides may include multiple patch/older-version sections; select those that affect the actual source patch, including security changes.

PHP floors and exact initial dependency manifests: [versions.md](versions.md). Use latest approved compatible patches and complete lock constraints, not the initial manifests as an execution lock. All versions in this file are EOL; run bridge versions in isolated engineering environments, not as recommended production destinations.

## 5.0 baseline

[Official 5.0 guide](official/5.0/upgrade.md) · [release notes](official/5.0/releases.md)

Confirm the app is really on 5.0, its patch, `bootstrap/autoload.php` compiled-file behavior (including 5.0.16), PHP ≥5.4 and required legacy extensions. Preserve its actual application structure. The guide's “fresh install then migrate” recommendation is for **4.2→5.0**, not permission to rebuild an existing 5.x app with a Laravel 13 skeleton. Unsupported PHP/TLS/packages may make exact reconstruction blocked; do not bypass integrity checks.

## 5.0 → 5.1

[Official 5.1 guide](official/5.1/upgrade.md) · [release notes](official/5.1/releases.md)

- PHP ≥5.5.9. Check AWS SDK 3/SQS/SES and Flysystem S3 adapter targets if used; SQLite column migrations may need DBAL.
- `lists()` now returns a Collection; collection sorting/grouping/mutation assumptions and model date serialization can change. **Gate:** actual callers and API/JSON contracts, not only type-compatible code.
- Encryption transitions toward OpenSSL. Inventory stored encrypted values and cookies; preserve key handling and test decrypt/session continuity rather than blindly regenerating APP_KEY.
- Ensure writable `bootstrap/cache`, preserving the project's ignore policy without committing generated cache artifacts. Existing command/handler paths remain supported; directory modernizations are optional.
- Legacy test base URL/config assumptions need the documented update; use a baseline-compatible test harness.

## 5.1 → 5.2

[Official 5.2 guide](official/5.2/upgrade.md) · [release notes](official/5.2/releases.md)

- Authentication changes can invalidate existing sessions; guard/provider configuration and session schema need review. Implicit model binding can resolve a type-hinted model from URI rather than injecting an empty model. **Gate:** guard login, existing cookies, model binding success/404/authorization.
- Separate command/handler bus patterns change. Trace command dispatch, handler resolution and event listeners, including background execution.
- Config caching makes runtime `env()` outside config unsafe. Do not introduce config caching as incidental cleanup; preserve the deploy policy and test cached mode only in isolation.
- Date/datetime casts, collection key retention, strict-mode/date/JSON DB behavior may change consumers. Test real DB driver inputs, invalid dates and serialization.
- CSRF no longer automatically runs in unit tests: negative and valid-control HTTP tests are required for security evidence.

## 5.2 → 5.3

[Official 5.3 guide](official/5.3/upgrade.md) · [release notes](official/5.3/releases.md)

- PHP ≥5.6.4; Symfony 3.1. Query Builder `get()`/`pluck()` return Collections. Test raw query consumers and calculations, not just Eloquent.
- Primitive validation rules with `null` need intentional `nullable` behavior. Cover empty/null/zero/optional and wildcard forms.
- Controller constructors cannot rely on session/auth state before middleware. Move required access to the correct middleware/request flow, not an unconditional bypass.
- Logout is POST; resource parameters/names and route-prefix behavior change. Compare URLs, route methods and CSRF-protected logout.
- Queued Closures are not supported at this hop; worker daemon defaults, retry config and failed-job schema change. Inspect existing payloads/worker supervision before execution.
- Mcrypt encryption support is removed. Plan authorized migration of persisted encrypted data if required; never silently drop unreadable data.

## 5.3 → 5.4

[Official 5.4 guide](official/5.4/upgrade.md) · [release notes](official/5.4/releases.md)

- Historical guide targets PHPUnit 5.7, Guzzle 6 and optional Tinker; review conditional Passport/Scout/Socialite versions. The testing layer was rewritten: BrowserKit compatibility or deliberate test porting may be necessary. Keep B runnable.
- Date casts normalize to start-of-day; `random(1)` returns a one-item Collection; `orWhere([...])` predicate logic changes; related models can inherit parent connection; Query Builder `chunk` needs ordering.
- Legacy `Class@method`/Closure mail paths need mailables. Test rendered mail, recipients, attachments, and queued delivery separately.
- Clear/rebuild only isolated compiled views/route artifacts as required; compare semantic query/date behavior, not just successful boot.

## 5.4 → 5.5 (historic LTS)

[Official 5.5 guide](official/5.5/upgrade.md) · [release notes](official/5.5/releases.md)

- PHP 7.0 floor; PHPUnit 6/SwiftMailer 6 and package discovery need deliberate tool/runtime changes. Inspect post-autoload scripts before enabling discovery.
- `Request::has()` now regards empty/null values as present; `filled()` may express old intent. Compare actual request filtering and validation truth tables.
- JSON validation/auth response envelopes and `withCount` aliases change. `Illuminate\Filesystem\Filesystem::files()` returns `SplFileInfo` objects—do not assume this is the same API as `Storage::files()`.
- **5.5.42 security behavior:** encrypted cookie serialization disabled, invalidating sessions/custom cookie values. Test continuity and plan an explicit reauthentication decision. Do not restore unsafe serialization to claim parity. APP_KEY rotation is an incident/security decision, not an unconditional upgrade step.

## 5.5 → 5.6

[Official 5.6 guide](official/5.6/upgrade.md) · [release notes](official/5.6/releases.md)

- PHP 7.1.3/Symfony 4, PHPUnit 7 and conditional proxy/auth/browser-tool upgrades. Validate the exact lock before changing runtime.
- Blade/`e()` double-encode entities by default. Inspect escaped output and inline JSON for visible/security differences rather than globally disabling escaping.
- Newly created model responses may now be 201; `morphs()` index order affects rollback; logging/proxy headers and Bootstrap 4 pagination change. Compare response clients, schema rollback, HTTPS/IP and page rendering.
- `optimize` is removed at this hop; inspect deploy scripts rather than pasting modern optimize commands.
- **5.6.30 security behavior:** cookie serialization disabled. Same security/session controls as 5.5.42; never preserve a vulnerable setting merely to avoid logout.

## 5.6 → 5.7

[Official 5.7 guide](official/5.7/upgrade.md) · [release notes](official/5.7/releases.md)

- Blade `or` defaults removed; redirect defaults change to 302; SQLite foreign-key drop behavior changes; nested validation returns only validated fields.
- Scheduled jobs honor job queue/connection settings; Artisan test output mocking changes how old test helpers observe commands. Test actual dispatch routing and command results.
- Required cache data directory/ignore setup must exist in the artifact. Keep generated data out of Git.

## 5.7 → 5.8

[Official 5.8 guide](official/5.8/upgrade.md) · [release notes](official/5.8/releases.md)

- **Integer cache TTL is now seconds, not minutes.** Inventory `put/add/remember` and related callers, explicit TTL wrappers and atomic locks. Use explicit durations or correct unit conversions only where required. Test just-before/at/after expiration and lock ownership, including scheduler/unique-job locks.
- Lock release requires owner identity. Do not force-release another worker's lock as a compatibility shortcut.
- phpdotenv 3 changes unquoted `#` handling; compare intended config structure without dumping secrets. Email validation is RFC6530-aware; test internationalized/legacy inputs and consumer requirements, not a blanket rollback of valid email support.
- Carbon 1/2 compatibility needs boundary/locale tests; taking Carbon 2 is separate from assuming every date string comparison was correct.
- Markdown mail `plain`→`text`, lazy tagged services, irregular-plural table inference, password minimum and notification channels can affect real behavior. Pheanstalk/Slack/Nexmo are conditional packages.
- Test lifecycle methods require `void` at this hop. Do not port that syntax back into PHP 5.x baseline tests.

## 5.8 → 6 (historic LTS)

[Official 6 guide](official/6.x/upgrade.md) · [release notes](official/6.x/releases.md)

- PHP 7.2 floor/Carbon 2; `str_*`/`array_*` helpers and `Input` facade are removed from framework. Prefer `Str`/`Arr` and request APIs; an approved `laravel/helpers` bridge may reduce churn but must be tracked, especially before PHP 8.5/Laravel 13 helper collisions.
- `authorizeResource` index policies require `viewAny`. A controller still rendering does not prove authorization policy parity.
- Default Redis client becomes phpredis; inspect extension/client configuration. Default worker tries becomes one; test retries/failures and job idempotency.
- Email verification resend becomes POST; review existing verification URL consumers and custom contracts. PasswordBroker no longer validates passwords itself: callers outside the standard controller must validate explicitly.
- URL generation with required/null/misnamed parameter keys is a practical legacy-app regression candidate; exercise every actual `route()`/`action()` consumer rather than declaring all static array matches broken.
- UI/auth scaffolding is separated from core in this release family; inspect existing traits/routes and compatible `laravel/ui` if needed. Do not regenerate frontend/auth screens.

## 6 → 7

[Official 7 guide](official/7.x/upgrade.md) · [release notes](official/7.x/releases.md)

- PHP 7.2.5/Symfony 5; guide aligns PHPUnit 8.5, Collision 4.1, Tinker 2, Ignition 2, and UI2 **when used**.
- **Eloquent dates in arrays/JSON become ISO-8601 UTC with fractional seconds.** Trace JS/API/exports/reposted values. Preserve consumed contracts deliberately through supported serialization hooks where required; do not override all models without evidence.
- Exception handler/report/render and job failure handlers use `Throwable`; validate custom overrides and error-page responses.
- Route names must be unique; test cacheability, action URL ambiguity and cached/uncached routing. Mailer configuration becomes multi-mailer; existing old mail config may remain valid, so do not rename env keys blindly.
- Response assertions escape expected content; keep characterization assertions semantically identical across tool versions.

## 7 → 8

[Official 8 guide](official/8.x/upgrade.md) · [release notes](official/8.x/releases.md)

- PHP 7.3 floor; guide aligns Guzzle 7, Ignition 2.3.6, Collision 5, PHPUnit 9 and conditional first-party packages. Later Laravel 8 patches support newer PHP; validate exact patches/locks and official support, not only the initial `^7.3` manifest.
- Factory rewrite breaks 7-style factories. Choose supported legacy-factory compatibility or deliberate conversion; inspect all factory/seed callers/autoload. Namespace changes require reviewing imports and custom `db:seed --class` callers **without running seeds on persistent data**.
- New-skeleton controller namespace defaults do not mandate changing an existing provider. Preserve supported routing structure and test actual URLs/actions.
- Pagination defaults to Tailwind; retain supported Bootstrap configuration if behavior requires it, instead of vendor-view overrides by default.
- Queue `retryAfter`→`backoff`, `timeoutAt`→`retryUntil`, chained-job methods and closure serialization require coverage of real jobs. Maintenance commands/bypass changed; inspect deploy scripts for removed options.

Next: [modern-9-to-13.md](modern-9-to-13.md), [runtime-and-dependencies.md](runtime-and-dependencies.md), and the full [verification matrix](verification.md).
