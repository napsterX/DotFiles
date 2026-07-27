# Claude Code Operational Handoff

## Handoff Metadata

- Schema version: 2
- Generated at: `<UTC timestamp>`
- Session ID: `<session id>`
- Label: `<label or none>`
- Handoff ID: `<filled by publication receipt>`
- Invocation directory: `<absolute canonical path>`
- Repository family: `<canonical git common-dir identity>`
- Active task worktree: `<absolute canonical path>`
- Project key: `<derived key>`
- Branch: `<branch or not applicable>`
- HEAD: `<full SHA or not applicable>`
- Previous handoff ID: `<id or none>`

## Resume Contract

Locate the exact latest verified handoff for this repository family, validate its
identity and content digest, compare it with the recorded active task worktree,
report drift, and stop for user instructions.

## Active Objective

`<precise objective>`

## Definition of Done

- `<observable completion condition>`

## Applicable Requirements and Constraints

- `[VERIFIED | SESSION EVIDENCE | INFERRED | UNKNOWN] <requirement>`

## Verified Repository and Filesystem State

- `[VERIFIED] <state>`

## Changes Since Previous Handoff

- `[VERIFIED] <commit/change/task transition accounted for, or none>`

## Completed Work

- `[VERIFIED | SESSION EVIDENCE] <completed item and evidence>`

## Changed and Relevant Files

| Path | Role | Current state | Evidence |
|---|---|---|---|
| `<path>` | `<purpose>` | `<committed/staged/unstaged/untracked/unchanged>` | `<class>` |

## Decisions and Invariants

- `[VERIFIED | SESSION EVIDENCE] <decision or invariant>`

## Validation Evidence

| Command or procedure | Result | Evidence | Code state | Coverage / limitation |
|---|---|---|---|---|
| `<command>` | `<result>` | `<class>` | `<commit/tree>` | `<what it proves and does not prove>` |

## Unresolved Failures and Blockers

- `[VERIFIED | SESSION EVIDENCE | INFERRED | UNKNOWN] <failure or blocker>`

## Rejected or Superseded Approaches

- `<approach>` — `<why it must not be repeated>`

## Runtime and External State

- `<known process, port, lock, service, worktree, temporary state, or none>`

## Assumptions Requiring Reverification

- `<assumption and verification method, or none>`

## Next Exact Action

`<one bounded, executable action>`

## Subsequent Actions

1. `<next ordered action>`

## Relevant Files to Read First

1. `<path>` — `<why>`

## Deferred Context

- `<unfinished but intentionally out-of-scope thread, or none>`
