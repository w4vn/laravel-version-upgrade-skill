# Laravel 8 → 13: upgrade hotspots

Read the **full next-target guide** and its patch changelog. This file highlights practical regression gates; it does not replace the guide's low-impact items, package docs or exact target patch requirements. Every guide heading needs an applicability disposition. See [versions.md](versions.md) for floors/support and [runtime-and-dependencies.md](runtime-and-dependencies.md) for safe resolution.

## 8 → 9

[Official upgrade](official/9.x/upgrade.md) · [releases](official/9.x/releases.md) · [framework changelog](official/9.x/framework-changelog.md)

**Runtime/packages:** PHP **8.0.2+**, not merely any 8.0 patch. Official guide: framework ^9.0, Collision ^6.1, replace facade/ignition with spatie/laravel-ignition ^1.0; conditional Pusher/Vonage and Flysystem adapter changes. Check the full lock/dev tools and actual extensions. Laravel 8's documented PHP overlap tops out at 8.1; a PHP 8.2 Docker image is not proof of supported Laravel 8 compatibility.

**Changes / evidence:**

- SwiftMailer→Symfony Mailer: inspect custom Swift callbacks/transports/plugins, raw messages and attachments. Compare captured **decoded MIME + envelope recipients**, not Message-ID/boundaries or just `Mail::fake()` counts.
- Flysystem 1→3: failed writes can return false, missing reads return null, writes overwrite, missing deletes can report success, cached adapters removed, custom adapter signatures/wrappers change. Test storage errors/permissions and DB/file consistency. Use supported exception policy only where the app requires it; do not assume all failures throw.
- PostgreSQL `schema`→`search_path`, validation exclusion of unvalidated array keys, HTTP client default timeout, custom casts handling null, belongs-to-many create methods and PHP return signatures need actual caller tests.
- Trusted-proxy/CORS packages and new-skeleton middleware paths are **conditional**. Inspect existing inheritance and package compatibility; do not copy a new Kernel blindly. Verify load-balancer HTTPS/IP and real CORS behavior.
- Review removed/changed test assertions (`assertDeleted` etc.), session APIs and JSON payload types after PHP 8 changes.

## 9 → 10

[Official upgrade](official/10.x/upgrade.md) · [releases](official/10.x/releases.md) · [framework changelog](official/10.x/framework-changelog.md)

**Runtime/packages:** PHP 8.1+, Composer 2.2.0+. Conditional targets include Sanctum ^3.2, Passport ^11.0, UI ^4.0, DBAL ^3.0 and Ignition ^2.0. PHPUnit 10 is **optional** in this hop; if adopted, align Collision and XML configuration deliberately, without breaking the original characterization harness.

- Model `$dates` is removed: migrate actual custom date attributes to supported casts and test Carbon behavior/JSON; leave unrelated supported casts alone.
- Database expressions no longer support blind string casting. Use the target grammar-aware API and validate SQL against the actual DB, not SQLite as a surrogate for MySQL.
- `dispatchNow`→`dispatchSync`, removed service-mocking helpers, custom logging/Monolog 3 handlers, Redis cache tags and FormRequest `after()` name collisions need source/caller review.
- Review ULID column correction and actual schema/client behavior before changing migrations.
- New-skeleton middleware aliases/language-directory conventions do not justify an application restructure where legacy APIs remain supported.

## 10 → 11

[Official upgrade](official/11.x/upgrade.md) · [releases](official/11.x/releases.md) · [framework changelog](official/11.x/framework-changelog.md)

**Runtime/packages:** PHP 8.2+, curl7.34+. Framework ^11.0/Collision ^8.1; only when present, inspect the guide's targets for Breeze, Cashier, Dusk, Jetstream, Octane, Passport, Sanctum, Scout, Spark, Telescope, Livewire and Inertia. Review their own guides and migration publishing; do not publish/execute package migrations automatically.

**Keep the old structure.** Official guidance explicitly advises Laravel 10 apps **not** to migrate to Laravel 11's slim application skeleton. Existing Kernels, Handler and providers remain the starting point. New installs' defaults are not mandatory upgrade steps.

- `->change()` drops unspecified column modifiers; explicitly preserve required unsigned/default/comment/nullable characteristics. Review schema, floats/doubles/spatial APIs and removed DBAL integrations; disposable migration/rollback tests are required for relevant changes.
- SQLite minimum3.26; target drivers/server versions must meet actual requirements. Framework DB changes do not automatically require a production DB-major upgrade.
- Password rehash-on-login may write to the user row; custom `UserProvider`/`Authenticatable` implementations gain methods. Exercise different-cost hashes, every guard, remember-me and the intended write behavior. Do not disable hashing protections just to avoid expected writes.
- Passport password grants disabled by default; token/auth package migrations and expiration behavior need explicit assessment.
- Rate limiter interval units/constructors and custom contracts change; test throttle limits/expiry under a persistent isolated store.
- Carbon 2 **and** Carbon 3 are supported here. If constraints permit, keep the existing major to isolate the framework step. If moving to 3, `diffIn*` can be signed floats; test deadlines/backoff/absolute-vs-signed semantics now, not only at 12.
- Effective framework/package config defaults may merge new keys without a tracked config diff. Inspect a redacted/whitelisted structural diff and the actual application behavior.

## 11 → 12

[Official upgrade](official/12.x/upgrade.md) · [releases](official/12.x/releases.md) · [framework changelog](official/12.x/framework-changelog.md)

**Runtime/packages:** PHP 8.2 floor remains; guide aligns framework ^12.0, PHPUnit ^11.0 or Pest ^3.0. This does not make all previously installed dev tools compatible.

- **Carbon 3 required; Carbon 2 removed.** Trace `diffIn*`, date math, relative labels, timezone/locale and zero/future/past boundaries. Preserve intentional signed/fractional contracts; use explicit absolute/truncation only where baseline behavior requires it. Do not blanket-cast every duration to int.
- `HasUuids` now generates UUIDv7. Use `HasVersion4Uuids` only where the existing external/storage contract needs v4; inspect ordering, validation, DB type and consumers.
- Container resolution respects nullable class default values; custom constructors/container bindings must not assume auto-created instances for null defaults. Low-level DB constructors, schema inspection across schemas and grammar APIs change.
- Password token repository expiry is now seconds, not minutes. Test generated token expiration and custom repositories/constructors, including edge instants.
- `mergeIfMissing()` dotted keys become nested; concurrency result keys and route matching changes deserve relevant tests.
- Local storage defaults to `storage/app/private` **only when local disk configuration is absent**; existing explicit roots need not change.
- Image validation excludes SVG by default. Do not allow SVG globally to silence a regression; review sanitization/serving policy and actual business need.

## 12 → 13

[Official upgrade](official/13.x/upgrade.md) · [releases](official/13.x/releases.md) · [framework changelog](official/13.x/framework-changelog.md)

**Runtime/packages:** PHP 8.3+; current edition documents PHP 8.3–8.5 support. The guide lists framework ^13.0, Boost ^2.0, Tinker ^3.0, PHPUnit ^12.0 / Pest ^4.0; update the relevant installed tools. Boost is needed for the optional Boost upgrade command, **not a mandatory runtime dependency to add to every app**. Do not invent Sanctum/Passport/Horizon/Telescope target versions absent upstream evidence. The full lock can require a higher PHP patch than framework's floor.

### Security, cache, cookies, sessions

- `VerifyCsrfToken`/`ValidateCsrfToken` become deprecated aliases for **PreventRequestForgery**, with origin verification. Same-origin `Sec-Fetch-Site` can pass without a token; default fallback remains token validation. Review middleware inheritance, route/test exclusions and the supported config API. Do not automatically override origin checks or enable origin-only mode; run the real HTTP matrix in [verification.md](verification.md).
- The guide documents default **application cache config** `serializable_classes => false`, recommending explicit object-class allow-lists or non-object payloads. **Do not assume that every retained old config has the same effective value**: inspect the exact locked framework/store defaults and app config. Inventory cache objects and test restoration; never set unrestricted deserialization merely to preserve behavior.
- Fallback cache/Redis prefixes and session cookie names now use hyphens. Explicit old config may preserve names. Test shared-state continuity; pin deliberate names where necessary rather than clear caches and log out everyone accidentally.
- New skeleton session serialization defaults to JSON. Copying that setting into an existing app invalidates active PHP-serialized sessions and cannot carry arbitrary objects. Retaining compatible PHP session serialization vs adopting JSON is an explicit security/reauthentication decision; do not silently sync the new skeleton.

### Database, containers and model behavior

- MySQL/MariaDB `upsert()` now requires non-empty `uniqueBy`, even though those drivers use DB primary/unique indexes for conflict detection. Trace actual calls and test conflict/update behavior.
- Joined MySQL DELETE now includes ORDER BY/LIMIT instead of silently ignoring them; unsupported engine syntax can now fail. Inspect actual SQL/engine and replace with a safe bounded strategy where required—do not remove limits to make it run.
- `Container::call` now respects nullable class defaults (constructor resolution changed in 12). Manager `extend` callbacks bind `$this` to the manager; capture required provider values explicitly.
- Model boot/trait-boot code may no longer instantiate the same model during its boot cycle. Explicit pivot table names may be required for changed plural inference. Restored serialized Eloquent collections now restore eager-loaded relations: test queued-job behavior/query/data exposure.

### Contracts, events, routing and output

- Review new custom-contract methods in cache Store/Repository (`touch`), Bus Dispatcher (`dispatchAfterResponse`), ResponseFactory (`eventStream`), MustVerifyEmail (`markEmailAsUnverified`) and Queue size/age inspection. Only manual implementations need signature work; do not rewrite every default model/service.
- JobAttempted now exposes `$exception` instead of boolean `$exceptionOccurred`; QueueBusy uses `$connectionName`. Queued notifications respect missing-model deletion settings. Test retries, listener reporting and failure handling.
- Explicit-domain routes take precedence over non-domain routes; compare all valid domains plus an unknown host and cached route behavior. `withScheduling()` registration timing is deferred when used.
- Password reset subject defaults, Bootstrap 3 pagination internal view names, `Js::from` unescaped Unicode and resetting Str factories between tests can affect snapshots/consumers. Explain relevant differences rather than normalize every output away.
- **PHP 8.5 polyfill/global helper collision:** Laravel 13 depends on symfony/polyfill-php85, which may define `array_first`/`array_last` below PHP 8.5. Historical `laravel/helpers::array_first` callback semantics are different. Replace actual legacy helper callers with `Arr::first` or the appropriate supported API and test behavior; do not rely on bootstrap order.
- `Request::get()` deprecation is confirmed in framework source, but `get()` and `input()` are not identical across all request bags. Inspect semantics before replacing; this is not a reason for a global regex rewrite.

### Cumulative input-key limit — verified in source, undocumented

**Verified in source, undocumented:** at tag **v13.38.0**, [TransformsRequest source snapshot](official/13.x/TransformsRequest-v13.38.0.php) sets `protected $maxKeyBytes = 20 * 1024 * 1024;` (line 16). It adds the nested prefix length and each key's byte length (lines 78–81), throwing `PostTooLargeException` / HTTP **413** when the cumulative total is **greater than 20 MiB** (lines 83–84). This is not a request-value/body-size limit; long/nested/multibyte keys can reach it. The default global `TrimStrings` and `ConvertEmptyStringsToNull` processing uses this base class, including query parameters and form/JSON input.

This comes from commit `1b8b12d307` (2026-10-20, “limit bytes”), is absent in v13.37.0 and v12.70.1 per the independent source review, and is not mentioned in the v13.38.0 changelog or upgrade guide. Commit `31dbc2b9b0` (“adjust parsing”) is after the tag in Unreleased; inspect the next actual release tag before carrying assumptions forward.

**Gate when large forms/JSON or many/long/nested keys are relevant:** compare B/P/C with the same synthetic valid input below/at the limit and an over-limit case, include a normal successful request control, and record whether proxy/PHP limits reject the request before Laravel. Test bytes rather than character count and account for repeated nested key prefixes. Do not disable or raise protection blindly to preserve an old unbounded input contract. See [verification.md](verification.md).

Project-specific backup/dompdf fixes and error-page differences still need reproduction here. Framework error pages/503 can change at any hop; use output gates instead of universally copying overrides.

## Closing each modern hop

Apply the tiered B/P/C checks and both pair comparisons: Level 0, audited critical Level 1, and risk-required Level 2. Only named pre-approved Level 1/2 gaps allow PARTIAL continuation; missing Level 0 cannot auto-advance. Track actual platform/artifact checks, security/advisory status and deployment/rollback readiness separately. Keep optional renderer/DB/front-end/package modernization scoped separately. No broken boot, unresolved regression or security weakening may be called verified.
