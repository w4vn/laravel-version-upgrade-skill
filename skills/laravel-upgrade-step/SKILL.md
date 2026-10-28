---
name: laravel-upgrade-step
description: "Execute an explicitly approved Laravel hop or continuous range, including each 5.x minor. Supports 8 -> 9 or 5.8 -> 13, isolated PHP/Docker runtimes, per-hop gates, persistent retry limits and resumable range work with local per-hop commits. Starts only when the user invokes this command."
argument-hint: '[absolute-project-path] ["source -> target"] [absolute-approved-source-plan-path]'
disable-model-invocation: true
---

# Execute an approved hop or continuous Laravel range

Request: `$ARGUMENTS`. This skill can change application files. **Do not start from an audit/plan, skill installation, a model invoking a companion, or merely reading this file. The user must manually invoke `/laravel-upgrade-step`.**

One boundary (e.g. `"8 -> 9"`) is a single-hop request. Multiple boundaries (e.g. `"5.8 -> 13"`) are a continuous range: keep executing approved hops until the target or a hard stop, without asking again for decisions already granted. Enumerate every 5.x minor and later major; do not jump boundaries. Installing/editing this suite is never an execution request.

Read [shared rules](../laravel-upgrade/SKILL.md), [Docker/runtime instructions](../laravel-upgrade/references/runtime-and-dependencies.md), [verification levels](../laravel-upgrade/references/verification.md), [state/templates](../laravel-upgrade/references/templates.md) and [operations](../laravel-upgrade/references/operations.md). These are instructions, not permission to weaken isolation/security.

## 1. Preflight: gather all decisions before starting

Resolve the app root, source, target, immutable B and **existing absolute source-plan path outside the repository**. The default source location is the user's private `~/.claude/laravel-upgrade-notes/<project>/plan-<date>.md`, expanded to an absolute path before invocation. Chat-only text, a missing file, a relative path or a future worktree-only plan is not enough: stop and have the approved plan saved durably first. Read its bytes once and compute SHA-256. The user's manual range invocation with that source path is approval of those exact bytes; record the actual invocation text/time and source hash, without requiring the old chat again on resume. Root constraints are not locked versions. If source=target, report no framework hop is needed; do not change patch scope. Confirm:

- The plan covers **every** hop and any source-line patch preparation, approved framework/package version constraints, PHP/Docker image references/digests, extensions, Composer/test-tool runtimes and artifact ownership.
- Every dependency has its maximum supported Laravel major / blocked hop identified. Required removals/replacements and their behavior gates are approved before the blocked hop; abandoned is not the same as incompatible.
- Security/session/CSRF choices, including origin-aware middleware and PHP-versus-JSON session serialization when relevant, are explicit. Baseline drift and any B-reconciled reference have separate approval and before/after hashes; never rewrite B.
- Audit-critical Level 1 gates, risk-required Level 2 gates and each exact permitted PARTIAL exception are named. **Level 0 and minimal real-CSRF on middleware-changing hops are not waivable for automatic advancement.** Security regressions cannot be accepted.
- Tool/dependency installation and bounded network access are covered by the approved plan. Inspect Git hooks (`core.hooksPath`, `.git/hooks`, hook managers) and signing integrations **before creating the worktree**: `post-checkout` runs on `git worktree add`, and `pre-commit`/`commit-msg` run on hop commits. Approve up front whether they may run; if not, create the worktree and commit with `git -c core.hooksPath=/dev/null …` and record that decision. Never let hooks gain network access implicitly or bypass them silently. No `~/.ssh`, Composer auth, Docker socket or live-service mounts/access without their own explicit approval. Networked Composer resolution has `--no-scripts --no-plugins`; tests use `--network none` or an internal disposable DB/Redis network.
- Existing user changes remain untouched and out of scope. All owner decisions still missing are asked in **one batch before execution**. Do not ask repeatedly between successfully pre-approved hops; an unforeseen decision is a hard stop instead of an assumption.

## 2. Own branch/worktree, never the user's working tree

For the range, create `upgrade/laravel-<x>-to-<y>` from B in a **separate worktree**, using the project's worktree policy. If using an approved B-reconciled execution reference, keep its explicit reconciliation history/evidence without replacing B. Do not checkout/switch the user's branch, modify their worktree or copy their uncommitted edits into the range implicitly. Inspect any colliding branch/path first; never overwrite, reset, force-delete or create a second conflicting run.

The manually invoked approved **range** authorizes one **local commit per closed hop** with that hop's scoped code/lock/docs/state. No push, PR or deploy. Commit messages follow the user's attribution policy (for example CLAUDE.md). Stage only intended files, not `git add -A`. A single-hop request does not expand scope or imply a commit unless explicitly authorized; otherwise finish with the reviewed diff/evidence and `ready_for_review` run status, not a committed range-closure claim.

Copy the approved source bytes into `docs/upgrade/plan.md` and an immutable `docs/upgrade/plans/plan-v1.md` **inside the owned worktree**, then verify both SHA-256 values equal the external source. Do not generate a replacement plan from memory. Create README, hop doc, ledger and schema-2 `run-state.json` there, recording the source path (paths under the home directory written as `~/…`, also in the recorded command), copy paths, hash/version and actual range-command approval/time. The external source remains outside both the original repo and worktree. Keep logs outside Git or redact/bound evidence; never commit keys/auth/`.env`/personal data.

## 3. Resume before doing anything twice

Reissuing the **same command** resumes, including after compaction or in a new session. Discover the matching worktree using read-only `git worktree list`; load `docs/upgrade/run-state.json`, plan, README, current hop document and ledger. Read only the current hop's full official guide.

Validate run identity, source/target, original B evidence, optional B-reconciled, branch/path, HEAD lineage, closure, lock/runtime and in-progress changes. For plan approval, use the recorded **actual user range invocation + time + exact source SHA-256** initially, and the recorded actual user replies for later revisions. A repeated command resumes that recorded grant; do not demand inaccessible prior chat when the durable record is complete. A bare hash, invented reply or model-authored approval is never consent. The argument may identify the preserved initial plan path; validate the entire history and use **the latest approved version**, not an old hash. Verify its external source, archived copy and active `docs/upgrade/plan.md` agree before doing more work (`<laravel-upgrade-dir>` is the sibling `../laravel-upgrade` of this skill's base directory):

```bash
python3 -I <laravel-upgrade-dir>/scripts/check.py --run-state /absolute/upgrade-worktree/docs/upgrade/run-state.json --plan-source ~/.claude/laravel-upgrade-notes/project/plan-2026-10-26.md
```

This read-only mode checks plan-history consistency only, not human authenticity, Git lineage or gate readiness; still perform the other resume checks. Missing or silently edited plan history is BLOCKED. Migrate an old schema only with user approval and preserved progress/counters; never fabricate missing approval evidence.

- Skip only hops proven closed by their one local commit and matching docs/state/evidence. Use each record's predecessor SHA to derive its closure commit from Git; do not put a commit's own unknowable SHA into the state it commits.
- Resume the first not-closed hop. Keep committed closure state plus the saved in-progress state; interruption after a gate but before its commit does not close a hop. Inspect and finish a safe pending closure rather than create a duplicate commit or rerun earlier hops.
- Preserve counters and pending approved exceptions across invocations. Do not reset the run, erase state, replace locks or discard changes to make identities match.
- Unexplained dirty paths, baseline/plan/lock/runtime mismatch or an ambiguous worktree are hard stops. If edits were interrupted before state was saved, reconcile the actual diff with the user instead of trusting stale evidence.
- If a hard stop remains unresolved, report it and do not resume execution. Once resolved, update its resolution/approval evidence. Exhausted retry budgets additionally need the explicit reset process below.

### Approve and publish a revised plan without losing resume

When an unforeseen decision stops the range, record the actual user answer with its timestamp. Keep non-sensitive wording verbatim; for secrets or personal data store only a redacted answer and an explicit list of omissions. An exposed secret still triggers the security stop; never write it into source plans, state or Git.

Create a **new** external source file (e.g. `plan-<date>-v2.md`) containing only the approved delta from the latest plan; keep all earlier source files unchanged. Bind the new SHA-256 to that decision record. Archive the exact new bytes in `docs/upgrade/plans/plan-v2.md`, verify source/archive hashes, then update the active `docs/upgrade/plan.md` copy and append `plan_versions`/approval history with source path, copy path, hash, approval time and decision ID. Update `approved_plan` to that version; never edit a plan without history, rewrite prior entries or reset hop counters. Closed-hop records keep the plan version/hash under which they were verified.

Before resuming application work, finish this publication and pass `check.py --run-state ...`; an interruption leaving mismatched active copy/state remains BLOCKED until the approved publication is reconciled. Reissuing the **original** command may still use the immutable v1 source path: it identifies the same run, but the effective plan is the latest approved version. If the user explicitly invokes the same range with a new external version path, record that actual invocation as a new revision decision in the existing run, not a new branch or fresh retry budget.

## 4. Per-hop loop — execute → gate → document → commit → next

For each approved next boundary:

1. Load its **entire official upgrade guide**, relevant source/patch evidence and package guides only. Record every heading's applicability. Do not refresh the whole archive or load future guides into every iteration.
2. Select the approved compatible runtime/lock intersection. Keep B/P under their matching images/vendors; do not run old apps on the host's modern PHP. Use the concrete Docker commands in the runtime reference. Review scripts/plugins before any explicit execution.
3. Update only approved candidate constraints/packages. Preview named updates with `--no-scripts --no-plugins --dry-run -W`; inspect additions/removals/downgrades and policy errors. Resolve/install only within approved scope. No platform bypass, lock deletion, insecure-package bypass or arbitrary unrestricted update. Required reviewed discovery/hooks run only in the isolated candidate after resolution.
4. Apply required source compatibility fixes, tracing shared callers; retain the supported old skeleton. Optional Rector must already be approved, version-compatible and next-hop scoped, starting dry-run. No incidental style, DB-major, frontend, authentication or business rewrites.
5. Before each gate round, **atomically persist its incremented counter**, lock/runtime identity and expected in-progress file hashes. Exclude `run-state.json` itself from any diff digest to avoid self-reference; record tracked and untracked scoped edits. If saving state fails, do not start the round.
6. Run Level 0 plus applicable Level 1 and required Level 2 on B/P/C using identical synthetic inputs and isolation. Compare C↔P and C↔B; if B cannot install and an approved B-reconciled is the execution reference, label that comparison explicitly and retain the direct-B limitation. Minimal real-CSRF must exercise representative POSTs, every `$except` and a valid success control through real middleware outside testing bypass when middleware/policy changed.
7. A non-security gate regression may be diagnosed and repaired **within this approved hop**, then rechecked. There are **at most 3 gate rounds total**, including the initial round, not an initial run plus three retries. Persist each failure and invalidate affected stale evidence. After the third failed round, stop; do not make more speculative fixes or silently start another budget. Any immediate hard stop below takes precedence over this repair loop.
8. If Level 0 and all required gates close, verdict is `VERIFIED IN <environment>`. Only pre-approved named Level 1/2 gaps allow `PARTIAL`; preserve the limitation and approval, never relabel it PASS. Known approved B failures may establish parity, not an all-green suite. Missing Level 0 or unresolved regression cannot auto-advance.
9. Update the same hop document and ledger, README and run-state with actual outcomes, code/package changes, lock/image identity, next hop, allowed PARTIALs and evidence. For a range, commit scoped code + lock + documents + closure state together as **one local hop commit**. Record its predecessor in the state and derive the resulting commit from Git on resume. Do not commit a failed/incomplete hop as closed.
10. Continue automatically to the next approved hop. Do not re-ask approved decisions, start the next hop before closure, or treat intermediate EOL versions as deployment destinations.

## 5. Hard stops and authorized recovery

Stop immediately for:

- A gate still failing after **3 total rounds**.
- A needed decision or dependency change not approved in the plan.
- A security regression.
- Unexpected access to a real DB/mail/storage/queue/webhook/service.
- Exposed secrets (do not copy them into docs/state; report exposure through the approved channel).
- Destructive schema changes.
- Lost original-B evidence, unsafe environment, or unexplained identity/worktree/state mismatch.

Persist the current hop, last completed hop, counters, sanitized failure/evidence references, next step and exact resolution/decision required. Report where the run stopped; no push/PR/deploy or destructive cleanup.

A stop is **recoverable**, not a permanent dead end. After an intervention and **explicit user permission to retry/reset**, append a reset-history record with the prior count, what changed, why retry is justified and the approval reference; set a new budget only as authorized. Do not reset automatically because the command was repeated, the context changed, or the user merely fixed a file. An unresolved security issue or missing B remains blocked even with retry permission.

## 6. At the requested target

Run the terminal C↔B comparison with the same tiered scope; distinguish an approved B-reconciled proxy from direct B evidence. Record cumulative drift, accepted differences, remaining PARTIALs, exact target lock/runtime, all-green/security/deployment verdicts and rollback limits. For a single hop without commit authorization, write the final reviewed evidence and return `ready_for_review`; do not claim a Git-closed hop or continue another boundary.

For the continuous range (or an explicitly commit-authorized single hop), prepare the final summary and intended `complete` closure state before the last hop commit, so no extra hop commit is needed. That state is only a pending closure until Git proves the final commit succeeded; if interrupted, resume the pending closure and never claim complete from an uncommitted flag alone. No additional framework hop, push, PR or deployment is implied.
