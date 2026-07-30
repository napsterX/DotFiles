# Skill Audit

## Scope

This audit covers argument parsing, P3/P2 queue bounds, issue-type neutrality,
model routing, bounded implementation retry, per-issue time budget, durable run
journaling and resume, execution locking, transient infrastructure retry,
FirstMate notification, worker isolation, acceptance proof, commit integrity,
clean-tree enforcement, GitHub behavior, interruption and partial failure,
cumulative verification, delegated `/audit-and-pr` finalization, untrusted issue
content, shell safety, credential exposure, loop bounds, and honest reporting.

## Findings and controls

- **Prompt injection through issue content:** issue bodies, comments, labels,
  logs, links, and screenshots are untrusted data and cannot override skill or
  repository authority.
- **Issue-type underreach:** removed. Eligibility depends on open P3/P2 priority,
  not a `bug` label.
- **Silent model fallback:** explicit per-attempt routing records,
  per-invocation Agent model parameters, environment-override checks, mismatch
  rejection, and honest runtime reporting.
- **Parent implementation fallback:** prohibited. The orchestrator may inspect,
  route, verify, commit accepted candidates, and report, but must not edit source
  code.
- **False completion:** a code edit is not accepted without a defined acceptance
  proof, targeted post-change evidence, diff review, repository-native
  validation, and a live budget check.
- **Unbounded implementation retry:** maximum three attempts per selected issue
  and no retry without material new evidence or plan.
- **Unbounded issue duration:** default 60-minute wall-clock budget, absolute
  worker deadline, command timeouts capped by remaining budget, no commit after
  expiry, and safe timeout cleanup before the next issue.
- **Crash and context loss:** atomic current state plus an append-only fsync'd
  transition journal supports exact resume validation and interrupted-issue
  recovery.
- **Concurrent batch collision:** atomic lease lock keyed by repository family,
  task worktree, and branch; explicit stale-lock recovery only.
- **Transient infrastructure fragility:** three bounded operation attempts with
  15/60-second backoff, strict retry classification, budget awareness, and
  mutation read-after-write reconciliation.
- **Duplicate remote mutation:** stable idempotency markers and reconciliation
  before retrying comments, issue creation, or an authorized push.
- **Commit noise:** attempts remain uncommitted; exactly one retained logical
  commit is created after issue acceptance.
- **Unbounded processing:** positive integer validation, hard cap `10`, and
  selected-issue slot accounting prevent quota drift. Timed-out issues consume a
  slot.
- **Cross-issue contamination:** one issue per worker, queue refresh after each
  slot, clean-tree checkpoints, and diff-tree validation.
- **Dirty work contamination:** unattended mode requires a clean task worktree.
- **Shell injection:** issue-controlled values must be passed as data or separated
  arguments; `eval` and unsafe interpolation are prohibited.
- **Credential exposure:** do not print the full environment or secret values.
- **Duplicate PR/audit work:** `/fix-issues` creates no PR and delegates exactly
  once to `/audit-and-pr` through a validated finalization manifest.
- **Verification weakening:** test deletion, blanket skips, threshold lowering,
  broad allowlists, and advisory reclassification are prohibited as green-making
  tactics.
- **Silent unattended completion:** one terminal FirstMate notification is
  attempted and journaled. Notification failure is non-blocking and never
  misreported as delivery.

## Accepted platform limitations

Claude Code may not expose deterministic resolved-model metadata for every
subagent invocation. The skill distinguishes requested model from runtime proof.

Some Claude Code versions may not expose hard preemption for an already-running
Agent call. The worker receives and must honor an absolute deadline, and all
shell/tool operations use remaining-budget timeouts, but the final report must
state when platform preemption could not be independently proven.

A long unattended run still depends on the Claude Code process, network access,
GitHub availability, repository dependencies, and host sleep/power settings.
The journal makes progress recoverable; it cannot keep a process running while
the host is suspended or powered off.
