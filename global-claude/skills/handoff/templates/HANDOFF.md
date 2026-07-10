# Claude Code Operational Handoff

## Handoff Metadata

- Schema version: 1
- Generated at: `<UTC timestamp>`
- Session ID: `<session id>`
- Label: `<label or none>`
- Project root: `<absolute path>`
- Project key: `<derived key>`
- Working directory: `<absolute path>`
- Branch: `<branch or not applicable>`
- HEAD: `<full SHA or not applicable>`

## Resume Contract

The next session must read current project instructions, verify this handoff
against repository and filesystem state, classify any drift, and continue only
when the documented next action remains valid.

## Active Objective

`<precise objective>`

## Definition of Done

- `<observable completion condition>`

## Applicable Requirements and Constraints

- `[VERIFIED | SESSION EVIDENCE | INFERRED | UNKNOWN] <requirement>`

## Verified Repository and Filesystem State

- `[VERIFIED] <state>`

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
2. `<next ordered action>`

## Relevant Files to Read First

1. `<path>` — `<why>`

## Deferred Context

- `<unfinished but intentionally out-of-scope thread, or none>`

## Context That Must Not Be Carried Forward

- Superseded discussion, duplicate explanations, completed exploration, and
  verbose logs that do not affect the active objective.
