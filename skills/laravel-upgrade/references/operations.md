# Operational readiness, cutover and rollback

Planning these steps does not authorize running them. Real environment access, deployment, destructive actions and outward-facing calls require explicit scope/approval. Read [Laravel deployment](https://laravel.com/docs/13.x/deployment), [queues](https://laravel.com/docs/13.x/queues), and the project's actual runbook; APIs/options vary across old releases.

## Isolate upgrade work

Use separate source trees and exact dependency/runtime combinations for B/P/C, created only under approved repository/worktree policy. Never move or overwrite the user's current edits. Separate writeable DB/cache/session/queue/buckets and provide local mail/webhook stand-ins. Do not copy production personal data. Approved schema/settings metadata is different from customer records and must not contain credentials.

Unsupported intermediate PHP/Laravel versions run in isolated, non-public engineering environments only. Do not weaken TLS or dependency security globally to resurrect an old install. Prefer retained trusted artifacts/lock metadata and document retrieval/security blockers. The goal is a supported final runtime, not publishing each bridge to production.

## Artifact and runtime contract

- Pin the **deployment** PHP patch family/extensions and the approved Composer version before resolving. `config.platform` is a solver input, not a runtime installation. Verify the actual artifact under actual CLI/FPM runtime and `check-platform-reqs`; no `--ignore-platform-reqs`.
- Align FPM, CLI, scheduler cron, queue/Horizon workers and deployment commands. An updated web PHP with old worker/cron PHP is an incomplete upgrade. Rebuild OPcache/process state through the existing service manager after cutover as approved.
- Keep production assets if that is the current release policy. If a build is required, use its lock and compatible Node toolchain; check manifest paths/browser behavior. Do not replace Mix/Elixir with Vite during a framework-only hop.
- Confirm document fonts, GD/Imagick, ICU/libxml, locales/timezone, file ownership/temp directories, upload limits and PDF executables. Trial image success does not prove server parity.

## Config and caches

Retain the existing deploy config-cache policy. `env()` outside config is fragile under cached config; inspect before introducing caching. Unit tests must not inherit cached real-service configuration. Do not dump all config values; compare approved non-secret keys and redacted structure.

Inspect config/route/view cache artifacts and warm/rebuild only in controlled candidate/release scope. Do not blindly run modern `optimize`/`optimize:clear` on old versions. Application cache may contain throttle counters, OTPs, locks, session-like state or serialized objects. `optimize:clear` may include application cache clearing. No blanket `cache:clear`; enumerate affected keys, state impact, owner approval and preservation strategy.

Config files may omit keys that newer framework/package defaults merge in. Diff new keys and unpublished package defaults, not just tracked config. Never `vendor:publish --force` over custom config/views. Cache prefix defaults, `APP_NAME`, serialization classes and Redis clients can affect compatibility without a source-code change.

## Queues and schedules

- Inventory serialized payload classes, closure jobs, model identifiers, retry/backoff/timeout/failure policy, after-commit dispatch, unique-job/overlap locks, encryption and queue version compatibility.
- Choose and document either compatibility-tested rolling deployment or a coordinated maintenance/drain cutover. **Do not mandate switching every instance simultaneously** when rolling compatibility is proven; do not allow mixed workers when serialized payloads cannot interoperate.
- Plan what happens to long-running/delayed/retrying jobs: drain, retain, translate, or explicitly requeue using approved idempotent handling. Draining a queue is not permission to delete payloads. Old jobs consumed by new workers and new jobs after rollback must be tested or isolated.
- Stop duplicate scheduler ownership and preserve locks. A restart does not guarantee all old jobs have completed. Restart workers/Horizon using the supported version/runbook after artifact/runtime cutover.
- Mail, backup, notification and API jobs use stand-ins in rehearsal; validate the first approved real run after cutover through normal monitoring, not an unsolicited test email/webhook.

## Sessions, authentication and security

Keep APP_KEY and session/cookie domain/name/store consistent; check encryption/MAC/serialization compatibility in both directions. Test B-issued sessions and remember-me cookies on C. Check password rehash writes and token expiration/time units. If a one-time logout is necessary, obtain approval and communicate it rather than silently changing keys.

Preserve security defaults unless a documented, reviewed policy change is required. Laravel 13 origin-aware CSRF is not automatically a regression to override. Trusted proxies must match actual load-balancer boundaries; trusting arbitrary forwarded headers can expose HTTPS/IP-based controls. Keep debug off and cookie flags correct in staging/production-mode gates.

## Database changes are a separate axis

A framework upgrade does not inherently require a DB-server-major upgrade. Check target driver/server requirements and vendor support status separately. A technically accepted old DB version may be past security support.

Review every migration and application data write before any run. `migrate --pretend` can boot arbitrary project code and migration callbacks; it is **not a universal read-only sandbox**. Execute migrations only on disposable DBs first, and only in approved staging/production maintenance scope later.

For required schema evolution prefer backward-compatible expand/contract across the rollback window. Record DDL locking, indexes, modifier retention, data conversion, generated UUIDs and reversibility. Do not rewrite historical migrations casually or run fresh/refresh against persistent state. Schema dumps may be useful but must be reviewed and must not discard migration history needed for supported install/rollback paths.

For MySQL/MariaDB/PostgreSQL/SQLite/SQL Server changes, use the actual vendor upgrade guide. Check client/server authentication, SQL mode, reserved words, collation/order ties, timezone and TIMESTAMP instants, spatial/numeric types, backup/restore tools. `mysql_native_password` availability differs between **8.0, 8.4 and 9.x**; “MySQL 8 disables it” is too broad. Never infer a shifted timestamp solely from displayed text; compare stored instant and session timezone.

## Rehearsal and go/no-go

Before deployment, require:

- Approved release artifact and complete verification matrix, unresolved/accepted changes with owners.
- Staging with target PHP/extensions, deploy/cache mode, DB settings/fonts and local integration stand-ins.
- Restore-tested backup, old artifact + old compatible runtime available, and explicit schema/data/job rollback limits.
- Traffic/maintenance strategy, queue/scheduler ownership and worker restart sequence.
- Observable error rate/latency, failed jobs, delivery/storage failures, login/authorization and business-output checks, with stop/rollback criteria and the responsible operator.

## Rollback is not always “switch code back”

Code-only rollback is safe **only if** schema, persisted data, encryption/session/cache entries and queued payloads remain compatible with the old artifact/runtime. New schema semantics, password writes, UUID/data formats or messages produced after cutover may prevent this. Retaining a previous Git commit is not sufficient.

Document rollback triggers, exact old artifact/runtime, traffic/worker order, whether new jobs must be isolated, data reconciliation/restore procedure, expected downtime/data-loss window, and approvals. Prefer forward-fix only when the owner accepts its risk and rollback truly cannot be safe. Never restore a production backup or delete newly written data without explicit authorization.

After rollout, report what actually happened, which checks ran and which remain pending. Do not call local success a confirmed deployment.
