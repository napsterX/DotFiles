# PR Change Summary and Changelog Policy

## Purpose

Every PR created or updated by `/audit-and-pr` must contain a concise,
changelog-style summary derived from the final audited implementation. This is a
review artifact, not automatically a permanent release changelog.

The summary must help a reviewer answer:

- what behavior was added, changed, fixed, or removed;
- whether users, operators, APIs, schemas, configuration, or compatibility are
  affected;
- whether any breaking action is required;
- which confirmed P2/P3 findings were deferred to open GitHub issues;
- when applicable, exactly how an already-red mandatory lane improved without
  introducing any new or unattributed failure.

## Final-state authority

Generate the summary from:

- the objective and acceptance criteria;
- the final audited diff and exact committed `HEAD`;
- tests and verification evidence;
- API, schema, migration, configuration, operational, and compatibility changes;
- retained P0/P1 remediation;
- the final deferred-finding tracking ledger.

Do not derive the summary from commit messages alone. Do not describe an earlier
HEAD after remediation, recommit, or final-gate retry changes the candidate.

A draft may be prepared while the final ship gate runs, but it is not final until:

1. the exact committed HEAD receives `NORMAL_GREEN`, successful legacy
   validation, or a complete `FAILED_PRE_EXISTING_BASELINE` classification;
2. the branch is pushed successfully;
3. deferred P2/P3 issue tracking is complete or not applicable.

If the final audited HEAD changes, regenerate the managed summary before PR
creation or update.

## Managed PR section

Use one managed block:

```markdown
<!-- audit-and-pr:change-summary:start -->
## Change summary

### Added
- ...

### Changed
- ...

### Fixed
- ...

### Removed
- ...

## User-facing impact
- ...

## Breaking changes
- ...

## Deferred findings
- #123 — P2: ...
<!-- audit-and-pr:change-summary:end -->
```

Rules:

- Include only non-empty `Added`, `Changed`, `Fixed`, and `Removed` categories.
- Always include `User-facing impact`; use `No externally visible behavior
  change.` when that is accurate.
- Include `Breaking changes` only when a breaking or required operator action
  exists. State the migration, deployment, configuration, compatibility, or
  rollback requirement explicitly.
- Include `Deferred findings` only when confirmed P2/P3 findings exist. Every
  bullet must link to the equivalent open issue established by the tracking
  gate.
- Never list deferred P2/P3 findings as fixed.
- Do not print empty headings or unresolved placeholders.
- Preserve user-authored and repository-template content outside the managed
  block.
- When updating an existing PR, replace the one existing managed block. Reject
  unmatched or duplicate managed markers rather than risking destructive body
  edits.

The repository's required PR template remains authoritative. Insert the managed
block at the most relevant location and retain all other required fields.

## Content quality

Write concrete behavioral statements. Prefer:

```text
Added idempotency protection that prevents duplicate extraction jobs after a
retry.
```

Avoid unsupported claims such as:

```text
Significantly improved reliability.
```

Keep facts and interpretation separate. Mention internal refactoring only when
it materially affects review, risk, maintenance, or operations.

## Sensitive content

Never include:

- secrets, tokens, credentials, private keys, or full environment values;
- private service URLs or internal account identifiers;
- customer or applicant data;
- exploit instructions or sensitive security reproduction details;
- raw logs containing confidential values.

Summarize security changes at the minimum useful level, for example:

```text
Tightened tenant-scoped authorization for report access.
```

## Baseline-restoration section

When the final shipment classification is `FAILED_PRE_EXISTING_BASELINE`, add a
distinct `Baseline restoration` section inside the managed block. This section
contains the complete Base-versus-branch failure ledger. Generate it
from the final audited HEAD and complete ledger, not from narrative claims.
Include:

- target failure fixed;
- canonical base and exact base commit;
- exact canonical-base command and truthful result;
- exact final branch commit, command, and truthful result;
- aggregate ship command and nonzero exit `1`;
- the full table with failure identity, base result, branch result, owner, and
  disposition;
- links to every canonical issue;
- explicit confirmation that no new or unattributed failure appeared;
- manual maintainer/user merge requirement;
- statement that the exception is scoped and not precedent;
- statement that normal green-gate policy resumes when the lane is restored.

Reject rendering when the ledger contains `NEW_REGRESSION`, `UNATTRIBUTED`, a
missing issue link, no `FIXED_BY_BRANCH` row, or an aggregate exit other than
`1`. Never rewrite `FAILED_PRE_EXISTING_BASELINE` as PASS.

## Permanent repository changelogs

Do not create a permanent changelog system merely because a PR is being created.
The presence of `CHANGELOG.md` alone does not authorize automatic edits.

Inspect repository instructions and established tooling for conventions such as:

- Changesets under `.changeset/` with repository configuration;
- Towncrier configuration and its declared fragment directory;
- a documented custom changelog-fragment directory;
- explicit instructions requiring an update to `CHANGELOG.md`.

When no established requirement applies, use the PR-body summary only.

When an established workflow requires an entry:

1. determine whether the change qualifies under repository policy;
2. verify an existing required fragment or entry against the final audited diff;
3. never describe deferred P2/P3 work as completed;
4. create or edit the artifact only when repository instructions explicitly
   authorize this workflow and prescribe a deterministic format;
5. treat the artifact as audited shipment metadata, include it in scope, and run
   targeted validation plus independent re-audit before the final commit and ship
   gate;
6. otherwise block shipment with the exact missing changelog action instead of
   inventing format, package impact, release level, or wording.

Any permanent changelog edit made after final verification invalidates that
verification and requires the normal re-audit, recommit, and final ship sequence.

## Evidence and reporting

Record:

- final HEAD used to generate the summary;
- managed-block action: created, replaced, unchanged, or blocked;
- included categories;
- user-facing impact classification;
- breaking-change status;
- deferred issue links included;
- baseline-restoration classification, target, exact commands/results, complete
  ledger, issue owners, and manual-merge statement when applicable;
- detected permanent changelog convention;
- permanent artifact action and validation result.
