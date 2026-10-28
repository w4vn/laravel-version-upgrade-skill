# Minimal deliverable templates

Use the project's documentation language and conventions. Do not scaffold every file for a small audit. Read-only audits return reports in conversation unless writing was requested. Once the user approves a plan, persist its exact text to a new private source file outside the repository before printing a ready-to-run command; a chat-only plan is not durable. An authorized multi-hop execution can use `docs/upgrade/README.md` plus **one document per hop** and one shared difference ledger; keep detailed logs/fixtures as referenced evidence, not a new report per command.

No sample below represents an actual run. Replace placeholders with observed facts; leave missing evidence NOT RUN/BLOCKED. Do not invent counts or dates/approvals to fill a table.

## A. Read-only audit / readiness

```markdown
# Laravel upgrade readiness — <project>

Scope: <requested branch/local app path/target>; audit only.
Local evidence: <SHA and observed user changes>. Remote/production match: <verified or unverified>.
Baseline confidence: <exact-production-matched / repository-locked / reconstructed / unknown>.
Framework: constraint <...>; locked <...>; installed/deployed <unknown unless evidenced>.
PHP: root constraint <...>; repo runtime hints <...>; real CLI/FPM/workers <unknown/observed>.

| Category | Evidence (file:line/source) | Finding / applicability | Safe next action | Status |
|---|---|---|---|---|
| Runtime | ... | ... | ... | ... |
| Dependencies / lock | ... | ... | ... | ... |
| Security / support | ... | ... | ... | ... |
| Tests / critical behavior | ... | ... | ... | ... |
| Operations / rollback | ... | ... | ... | ... |

Required hops: <each 5.x minor if applicable, then every major>.
Runtime bridges to validate: <framework/lock/dev tools, not a floor-only recipe>.
Critical characterization cases: <actual auth/money/documents/delivery/etc>.
Unknowns / decisions: <baseline, deployment PHP, services, package replacements, acceptance>.
Verdict: READY TO PLAN / PARTIAL / BLOCKED.
Not performed: <app execution/tests/network advisory checks as applicable>.
```

## B. Draft or approved upgrade plan

### Draft identity — before approval

Use this header while the plan is still being reviewed. Do not invent an approved source, version or hash, save it as an approved source file, or print a READY execution command. The shared hop/scope body below still applies.

```markdown
# Upgrade plan draft — <project>

Original baseline B: <observed reference, or explicitly unknown>.
Approved source: none (draft)
Plan version / SHA-256: N/A until approval
Approval: pending — NOT READY TO RUN.
```

### Approved identity and shared plan body

Only after actual approval, persist the exact approved text outside the repository and replace the draft identity with the real absolute source/version/hash below. Approval to save a plan does not start execution.

```markdown
# Upgrade plan — <project>

Original baseline B: <source identity, lock hash, confidence, runtime>.
Approved source: <existing absolute path outside repo, default expanded ~/.claude/laravel-upgrade-notes/<project>/plan-<date>.md>.
Plan version / SHA-256: <version and exact source bytes hash; do not overwrite prior versions>.
Target/support source checked: <official URL/commit, retrieval date, supported destination>.
Scope: <framework + necessary compatibility only>; excluded: <DB/frontend/optional package rewrites>.

| Step | Source → target (patches to resolve) | PHP/Composer/test runtime | Required package changes | Guide / app hotspots | Gates | Rollback / stop condition |
|---|---|---|---|---|---|---|
| ... | ... | ... | ... | ... | ... | ... |

Source-line patching: <separate step if needed>.
Baseline characterization: <cases and safe fixture/environment requirements>.
Bridge policy: obsolete versions are isolated engineering checkpoints, not production destinations.
Range authorization: <only if explicitly issued as `/laravel-upgrade-step <x>-><y>`; otherwise one hop / no execution authorization>.
Pre-approvals for every hop in the continuous range: <all intermediate hops; PHP/Docker image ref + digest; exact package removals/replacements; security, session and CSRF policy decisions; named Level 1/2 PARTIAL exceptions with reason and approval reference>.
Execution boundary: <own worktree on `upgrade/laravel-<x>-to-<y>` from immutable B; user worktree untouched; command authorizes only local commit per closed hop; attribution per the user's policy; no push, PR or deploy>.
Other approvals: <installs/tooling and any allowed external access; production access remains unauthorized unless explicitly stated>.
Release strategy: <tested rolling vs coordinated cutover>; queue/session/schema compatibility: <...>.
Rollback feasibility: <old artifact/runtime + persisted data/jobs/schema limits>.
Completion: Level 0 + applicable Level 1 + risk-required Level 2; approved named Level 1/2 gaps remain PARTIAL; missing Level 0 cannot auto-advance; terminal C↔B comparison and no unresolved regression.
```

Do not put unverified exact package pins into the approved plan as if they have resolved. Mark version candidates and the resolution/approval gate. Guides' estimated upgrade minutes are not project estimates.

## C. One hop / completion review

```markdown
# <Laravel/PHP/package step> — <source → target>

## Summary
<What this step achieves, why needed, and what users/consumers will notice.>
B: <original source/lock/runtime/confidence>.
P: <previous source/lock/runtime>; C: <candidate identity/lock/runtime>.
Uncommitted candidate identity: <recorded snapshot/diff digest if no commit was authorized>.

## Dependency changes
| Package | Before locked | After locked | Constraint change | Why required / upstream source |
|---|---|---|---|---|
| ... | ... | ... | ... | ... |
<Explain significant transitive additions/removals/downgrades and deliberate pins; lock holds exhaustive detail.>

## Source changes
| File or justified group | Change | Required because / caller evidence | Behavior gate |
|---|---|---|---|
| ... | ... | ... | ... |
<Every changed/new/deleted file accounted for; optional cleanup excluded.>

## Official-guide applicability ledger
| Guide heading / package change | Applies? | File/caller evidence or N/A reason | Required fix / no change needed | Test / evidence |
|---|---|---|---|---|
| ... | ... | ... | ... | ... |

## Verification
Environment / fixture / clock / tool versions: <...>.
Level 0 complete: <manifest/lock + actual platform; isolated boot; B/P/C route-list diff; entire suite + identities/statuses; per-role main-page HTTP smoke on throwaway synthetic DB; conditional real-CSRF check if middleware changed>.
Critical Level 1 features: <audit list and results>.
Risk-required Level 2 gates: <list and results>.
| Level / gate and exact scope | B result | P result | C result | C↔B | C↔P | Evidence / approval ref |
|---|---|---|---|---|---|---|
| ... | ... | ... | ... | ... | ... | ... |
<Compare JUnit with `python3 -I <path-to-compare_junit.py> left.xml right.xml`; retain the original full-suite command, exit, warnings and logs. State identities/counts and CLI exits; report failures, risky/warnings, skips/incomplete and deprecations separately.>
<For PDF: files/pages, renderer/DPI/fonts, metric/threshold/operator, minimum per-page score,
page count/text/amount/marker results and diff artifacts for both pair comparisons.>
<Evidence reused only when valid within this closing round; mark reused vs newly run.>

## Differences and decisions
- Fixed upgrade regressions: <trigger → baseline → regression → verified fix>.
- Pre-existing defects: <shared ledger reference; original outcome not disguised as PASS>.
- Accepted differences: <owner approval reference and scope>.
- Unresolved / blocked / not run: <reason and next action>.

## Operations / rollback / limits
<Actual runtime/config/artifact requirements; queues/session/cache/schema compatibility;
staging/restore/rollback evidence and pending deployment checks.>
<No broad production parity claim beyond observed scope.>

Verdicts separately:
- Behavior parity: <verified scope / partial / blocked>.
- All-green suite: <yes/no/not run, with limitations>.
- Security: <advisory date/tool/lock + findings / unverified>.
- Deployment readiness: <environment + pending approvals/rehearsal>.
Overall hop: VERIFIED IN <environment> / PARTIAL / BLOCKED. VERIFIED requires Level 0, applicable Level 1 and risk-required Level 2 complete, with no unresolved regression; a named pre-approved Level 1/2 exception is PARTIAL, and missing Level 0 is BLOCKED.
Next hop: <allowed after closure, or PARTIAL only for the exact pre-approved exception; never with missing Level 0>.
Commit / deploy: <only the local per-hop closure commit authorized by the approved range command; no attribution, push, PR or deploy>. Do not imply a schedule.
```

Explain non-trivial fixes in cause/effect language. A package list or “Carbon fix / PDF 99% / parity OK” is not enough to review user-visible risk. Reconcile the document with the final diff and real evidence; correct stale counts in the same document rather than creating duplicate reports.

## D. Shared difference / defect ledger

```markdown
| ID | Originating hop | Trigger / baseline behavior | Candidate behavior | Classification | Decision owner / approval evidence | Regression gate | Current status |
|---|---|---|---|---|---|---|---|
| ... | ... | ... | ... | upgrade regression / baseline defect / accepted change / unresolved | ... | ... | ... |
```

Carry accepted changes forward; do not “fix” them back in a later hop. A regression found late is attributed to its originating hop, fixed in the current authorized scope, and the earlier verification limitation corrected explicitly. Do not claim that later evidence existed at the earlier completion.

## E. Optional human QA / cutover checklist

Create only when requested or established project practice requires it. Include role/fixture, baseline/candidate result columns, safe GET URLs or action instructions, expected outcome, actual outcome, evidence and a glossary for domain/technical terms. Cover positive and denied auth paths, critical state transitions, outputs and accepted differences.

Cutover runbook must name artifact/runtime, operator, approvals, staging evidence, backup/restore evidence, traffic strategy, queue/scheduler ownership, cache/session preservation, stop/rollback criteria and data/job/schema rollback limits. Do not include production secrets or invent deployment commands before the environment is known.

## F. Approved continuous-range execution and resume

A range is authorized by the actual user's manual `/laravel-upgrade-step` invocation with its range and **absolute external source-plan path**, bound to that source's SHA-256 and invocation time in `approvals.range_invocation`. Persist the approved source first at the expanded private-notes path (or user-chosen external path), then copy exact bytes to the worktree and verify equal hashes. A file only inside the future worktree or plan text only in chat cannot start a run. The grant covers the explicit complete plan; unresolved decisions still block preflight. Record up front for each hop: PHP/Docker image reference and digest; exact package removals/replacements; security, session and CSRF decisions; and any specifically named Level 1/2 PARTIAL exceptions with reason and approval reference. It does not authorize a security regression, real-service access, production work, push, PR or deployment.

Execution uses an isolated worktree created from immutable B on `upgrade/laravel-<x>-to-<y>`; do not alter the user's worktree. The range command authorizes only one local commit per closed hop, containing that hop's code, verification document, updated run-state and ledger changes. Follow the user's commit attribution policy. Do not push, open a PR or deploy.

Persist one `docs/upgrade/run-state.json` for the range. A gate round is one full verification/repair cycle for a hop. The limit is three rounds total per hop across invocations and sessions. Atomically save the incremented round count before starting any checks; if that save fails, do not start the round. Never reset the count on reinvocation or a new session. On exhaustion, stop. Reset only after an intervention and explicit user permission; record the previous count, intervention, reason, approval reference and evidence in reset history.

Hard stops are: an unapproved decision; a security regression; real-service access; an exposed secret; destructive schema work; or lost B evidence. After a hard stop, resume only once the cause is resolved and state/approval references are updated; an exhausted counter also requires the explicit retry reset above. A security regression is never an acceptable PARTIAL exception.

For the exact same range command, discover a matching existing worktree with read-only `git worktree list`; before resuming, verify project/range identity, B SHA/evidence, schema and the latest approved plan source/archive/active-copy hashes with append-only approval/version history, branch/path, HEAD lineage, lock hash, PHP image/ref/digest and dirty status. The original command's source path may be an older immutable history entry: use it to identify the run, then validate the latest approved version rather than require its old hash to equal the revised plan. Continue only in the matching worktree. Permit only the recorded in-progress changes for the current hop; unexplained dirty paths or any mismatch is a stop. Never reset, overwrite, create another branch/worktree, or discard changes to force a match. Skip a hop only when its closure commit and required documents/state/evidence can be proven from Git. Record each hop's predecessor SHA (HEAD immediately before its one closure commit); derive the closure commit from Git on resume and never embed that commit's own not-yet-known SHA in the state file. Before closing the final hop, run the terminal C↔B comparison and write the final summary/intended complete state into that hop's commit. Treat the complete flag as pending until Git proves the closure commit succeeded; resume an interrupted closure without a duplicate or extra completion commit. Do not run two sessions concurrently in the same upgrade worktree.

## G. Persistent run-state template — `docs/upgrade/run-state.json`

Create this schema-2 file only for an explicitly approved range. The actual user invocation with an **absolute external source-plan path** approves that exact plan SHA-256; record its text/time/hash as `range_invocation`, rather than requiring inaccessible previous chat on resume. Later revisions require actual user decisions, recorded verbatim when non-sensitive or redacted with omissions listed. A model-written approval or a bare hash is not consent. Replace placeholders with observed values; never store secrets/personal data. Write paths under the user's home directory as `~/…` here and in the recorded command, so a pushed upgrade branch does not reveal local usernames; `check.py --run-state` expands `~`. Older state needs an approved migration retaining all progress, evidence and counters, not a fresh run.

```json
{
  "schema_version": 2,
  "run_id": "<stable UUID>",
  "project": {
    "identity": "<canonical repository identity>",
    "root_path": "~/projects/app"
  },
  "baseline": {
    "original": {
      "commit_sha": "<immutable B SHA>",
      "composer_lock_sha256": "<sha256>",
      "lock_content_hash": "<original lock content-hash>",
      "computed_content_hash": "<original manifest content hash>",
      "lock_in_sync": null,
      "config_hashes": {
        "<relevant config path>": "<sha256>"
      },
      "confidence": "<exact-production-matched|repository-locked|reconstructed|unknown>"
    },
    "reconciled": null
  },
  "range": {
    "source": "<x>",
    "target": "<y>"
  },
  "approved_plan": {
    "version": 1,
    "source_path": "~/.claude/laravel-upgrade-notes/project/plan-2026-10-26.md",
    "path": "docs/upgrade/plan.md",
    "sha256": "<sha256>"
  },
  "plan_versions": [
    {
      "version": 1,
      "source_path": "~/.claude/laravel-upgrade-notes/project/plan-2026-10-26.md",
      "copy_path": "docs/upgrade/plans/plan-v1.md",
      "sha256": "<sha256>",
      "approved_at": "<actual invocation time with timezone>",
      "approval_ref": "approval-001"
    }
  ],
  "approvals": {
    "range_ref": "approval-001",
    "range_invocation": {
      "id": "approval-001",
      "kind": "range-command",
      "invoked_at": "<actual invocation time with timezone>",
      "command": "/laravel-upgrade-step ~/projects/app \"5.8 -> 13\" \"~/.claude/laravel-upgrade-notes/project/plan-2026-10-26.md\"",
      "plan_source_path": "~/.claude/laravel-upgrade-notes/project/plan-2026-10-26.md",
      "plan_sha256": "<sha256>"
    },
    "decisions": [],
    "decision_refs": [],
    "allowed_partials": [
      {
        "hop": "<source->target>",
        "gate": "<specific Level 1/2 gate>",
        "reason": "<specific limitation>",
        "approval_ref": "<reference>"
      }
    ]
  },
  "workspace": {
    "branch": "upgrade/laravel-<x>-to-<y>",
    "path": "~/projects/app-laravel-upgrade"
  },
  "progress": {
    "current_hop": "<source->target or null>",
    "next_hop": "<source->target or null>",
    "last_closed_hop": null,
    "closed_hops": []
  },
  "hop_attempts": {
    "<source->target>": {
      "rounds_used": 0,
      "max_rounds": 3
    }
  },
  "runtime_by_hop": {
    "<source->target>": {
      "php_version": "<observed version>",
      "image_ref": "<approved PHP/Docker image reference>",
      "image_digest": "sha256:<approved digest>",
      "composer_lock_sha256": "<sha256>"
    }
  },
  "in_progress": {
    "hop": null,
    "expected_dirty_paths": [],
    "diff_sha256": null
  },
  "status": "<planned|running|partial|blocked|stopped|ready_for_review|complete>",
  "hard_stop": null,
  "retry_reset_history": []
}
```

When reconciliation was separately approved, set `baseline.reconciled` to a named **B-reconciled** object with its commit/snapshot identity, original locked `content-hash`, original computed content hash, reconciled computed content hash, lock SHA256 before/after, exact manifest diff, relevant config hashes and approval reference; otherwise leave it `null`. B always remains the original commit. A non-installable B cannot supply direct runtime evidence: label C↔B-reconciled explicitly, document the direct-B limitation and approved proxy rationale, and never call that production-exact. Each `progress.closed_hops` record contains source/target, `predecessor_sha`, `plan_version`, `plan_sha256`, verification-document path, evidence paths and ledger path. A later plan revision must not rewrite the approval/evidence under which an earlier hop closed. The matching closure commit contains the code, document, state and ledger updates. Keep its own SHA out of that commit's state; derive it from Git using the recorded predecessor when resuming. Keep state changes and expected in-progress dirty paths current, and never store secrets.

## H. Retry reset record

Append an entry only after intervention and explicit user permission:

```json
{
  "hop": "<source->target>",
  "previous_rounds_used": 3,
  "intervention": "<what changed before retry>",
  "reason": "<why another round is needed>",
  "approval_ref": "<explicit user permission>",
  "evidence_path": "<path proving intervention/resolution>"
}
```

The reset history is append-only. Update `rounds_used` only after the recorded intervention and explicit user retry/reset permission; `max_rounds` remains 3. Record the new counter/budget in the reset entry as well, preserving all prior usage/history. A repeated command, a new session, a file edit or an approved plan revision alone is not reset permission. Unresolved security/identity/evidence stops remain blocked even if a retry budget was reset.

## I. Plan revisions and approval records

After a real user decision changes the plan:

1. Record the actual reply and approval time. Keep non-sensitive text verbatim. If it contains secrets or personal data, store only the redacted wording with `redactions` listing omissions; never commit the sensitive original. Model-generated acceptance is not approval.
2. Create a **new** external file, e.g. `plan-<date>-v2.md`, preserving v1. Apply only the approved delta; show the delta if its interpretation is not explicit. Compute the new SHA-256 and bind it to that decision record.
3. Write an immutable versioned worktree copy `docs/upgrade/plans/plan-v2.md` and verify its hash equals the source. Append a sequential `plan_versions` row with both paths, SHA-256, `approved_at` and `approval_ref`; preserve all old rows/source/archive files.
4. Update `approved_plan` and the active `docs/upgrade/plan.md` copy to the new bytes. Complete publication before further app changes; if interrupted, inconsistent hashes block until the known approved publication is reconciled. Do not silently recalculate hashes over an edited plan to make it pass.
5. Validate against the latest approved version on resume, even when the original user command still points at v1. Keep counters and closed-hop plan/evidence bindings unchanged. A new explicit command using v2 can supply the actual revision approval; attach it to the existing run, never create a fresh budget/branch.

Append this decision to `approvals.decisions` and this version to `plan_versions`, substituting real values:

```json
{
  "decision": {
    "id": "approval-002",
    "kind": "user-decision",
    "approved_at": "<actual user decision time with timezone>",
    "user_response": "<verbatim non-sensitive answer, or explicitly redacted answer>",
    "redactions": [],
    "plan_sha256": "<v2 sha256>"
  },
  "plan_version": {
    "version": 2,
    "source_path": "~/.claude/laravel-upgrade-notes/project/plan-2026-10-26-v2.md",
    "copy_path": "docs/upgrade/plans/plan-v2.md",
    "sha256": "<v2 sha256>",
    "approved_at": "<same actual user decision time>",
    "approval_ref": "approval-002"
  }
}
```

For example, the initial invocation remains bound to v1; after this approved revision, `approved_plan.version` is 2 and its source/hash identify v2 while `approved_plan.path` stays `docs/upgrade/plan.md`. Old source/archive hashes must still match. Missing history/approval or a silent source/copy edit is BLOCKED, not a request to restart. Existing schema-1 states require explicit migration approval preserving counters/progress and actual approval evidence; do not invent an old invocation.

Read-only consistency check (not authentication of human intent, full Git-state validation or app readiness):

```bash
python3 -I <laravel-upgrade-dir>/scripts/check.py --run-state /absolute/upgrade-worktree/docs/upgrade/run-state.json --plan-source ~/.claude/laravel-upgrade-notes/project/plan-2026-10-26.md
```

This accepts the preserved original source argument while validating the latest approved version. It never boots the app or modifies state.
