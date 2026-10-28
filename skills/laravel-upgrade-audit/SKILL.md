---
name: laravel-upgrade-audit
description: "Read-only readiness audit before a Laravel 5.x–13 upgrade: locked framework/PHP, dependencies, infrastructure, tests, risky integrations and missing evidence. Use for audit nâng cấp Laravel or upgrade blockers. Does not boot or modify the application."
argument-hint: "[absolute-project-path] [target-version]"
---

# Laravel upgrade audit — no application execution

Request: `$ARGUMENTS`.

1. Read the [audit procedure](../laravel-upgrade/references/audit.md) and follow this skill's read-only scope. Do not read the upgrade-step skill or use it to bypass `disable-model-invocation`; this companion audit never authorizes application execution or modification.
2. Resolve the requested app directory and local instructions. Prefer a connected, fresh code index (for example tokensave); otherwise disclose fallback and inspect source read-only. Do not update an index for an audit.
3. Run the suite-owned static helper if Python is available. `<laravel-upgrade-dir>` is the sibling `../laravel-upgrade` of this skill's base directory:
   ```bash
   python3 -I <laravel-upgrade-dir>/scripts/inventory.py /absolute/app/path --scan --target 13 --brief
   ```
   Replace path/target with the request. Never run `composer`, PHP, Artisan, tests or project scripts for this audit; inspect manifests/locks/config source instead. Do not read `.env` or expose registry URLs, credentials, config values, or business data.
4. Verify the helper's hints against source/callers and read the next official guide. Identify actual locked versions separately from manifest constraints; installed/vendor and production consistency remain unverified unless separately evidenced. Read [runtime-and-dependencies.md](../laravel-upgrade/references/runtime-and-dependencies.md) for package/runtime planning.
5. Return baseline confidence, required hops, deployment runtime evidence, package blockers, critical behavior gates, test gaps, security/EOL risks and unanswered decisions. Each concrete finding needs `file:line` or an official source, applicability and its cheapest safe next action.
6. Use the audit section of [templates.md](../laravel-upgrade/references/templates.md). Report `READY TO PLAN`, `BLOCKED`, or `PARTIAL`; never `UPGRADE VERIFIED` from a static scan. Write a report into the repository only when requested; otherwise return it in the conversation.

Freshness and official source provenance: [sources.md](../laravel-upgrade/references/sources.md). Local official snapshots are reference material, not live audit results.
