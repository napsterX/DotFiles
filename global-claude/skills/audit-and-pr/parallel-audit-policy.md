# Parallel Audit Policy

Parallelism is an optimization, not a relaxation of audit authority. Use a
single dependency-aware workflow with read-only concurrent lanes and sequential
mutation and shipment gates.

## Operating principle

Parallelize work only when tasks are independent and bound to the same immutable
audit state. Keep these operations sequential:

- repository/worktree safety and canonical-base resolution;
- deterministic preflight decisions;
- remediation writes;
- commit creation;
- final exact-HEAD ship gate;
- push, PR mutation, CI disposition, merge, and cleanup.

Never allow two workers to edit the same worktree concurrently.

## Automatic lane selection

Use `scripts/audit_parallelism.py` as the executable reference when helpers are
available. Default mode is `AUTO`.

- Documentation-only or no more than five low-risk files in one domain: one
  integrated lane.
- Medium change, commonly 6–20 files or two affected domains: two lanes.
- High-risk, more than 20 files, or at least three affected domains: three
  lanes.
- Verification-governance-sensitive change: add a dedicated verification lane,
  up to a hard maximum of four concurrent lanes.
- When the host cannot run concurrent workers, use one integrated sequential
  audit. Never claim parallel execution occurred.

Explicit invocation may request sequential or parallel mode, but the hard
maximum remains four and mutation remains single-writer.

## Parallel preparation

After adapter validity and `doctor` pass, the main deterministic `fast`
preflight may run concurrently with read-only packet preparation when the host
supports it.

Preparation tasks may include:

- objective, issue, PR, and repository-instruction collection;
- changed-file and dependency map;
- affected-domain and risk classification;
- prior evidence collection;
- verification-governance-sensitive path detection;
- audit-packet construction.

Preparation must not modify files, execute remediation, or issue a final audit
verdict. If preflight blocks, cancel or discard unfinished preparation and stop.

## Immutable audit packet

Every audit lane must receive the same packet:

- repository path;
- exact `HEAD`;
- canonical base and merge-base;
- complete audited diff/range;
- objective and linked ticket;
- applicable repository instructions;
- working-tree and unrelated-change boundaries;
- deterministic preflight evidence or legacy mode;
- evidence plan and prior evidence ledger;
- risk and affected-domain classification;
- verification-governance-sensitive flag;
- known constraints.

Before synthesis, confirm every lane reviewed that exact `HEAD`, base, and scope.
A lane result from another code state is stale and must not be merged into the
verdict.

## Standard read-only lanes

### Correctness and behavior

Review objective coverage, logical correctness, interfaces, state transitions,
error handling, concurrency, idempotency, and backward compatibility.

### Security and data boundaries

Review authentication, authorization, tenancy, ownership, privacy, secrets,
persistence, migrations, destructive operations, and privileged boundaries.

### Architecture, evidence, and operations

Review architecture consistency, test sufficiency, CI enforcement, operational
behavior, observability, recovery, rollout, rollback, contracts, docs, and
governance.

### Verification governance

Activate only for verification-governance-sensitive diffs. Review adapter and
profile changes, required-check membership, applicability and skip behavior,
blocking/advisory classification, allowlists, baselines, thresholds, timeouts,
exit codes, reconciliation, and false-green paths.

Two-lane mode combines correctness with security and combines architecture with
evidence and operations. One-lane mode performs all dimensions together.

## Lane contract

Each lane is read-only. It may inspect repository content and existing evidence,
but it must not:

- edit files;
- commit, push, create or update a PR, merge, or clean branches;
- run broad duplicate test suites;
- produce the authoritative final verdict;
- remediate findings;
- change verification machinery.

Each lane returns:

- exact `HEAD`, base, and scope reviewed;
- assigned dimensions completed;
- findings with severity and direct evidence;
- missing evidence or test obligations;
- uncertainties and conflicts;
- no-change confirmation.

Testing execution remains centralized through `minimal-sufficient-testing` so
parallel lanes do not duplicate expensive commands or contend for shared ports,
databases, generated outputs, coverage directories, browser state, or Docker.

## Authoritative synthesis

One audit lead owns the final result. It must:

1. reject stale or incomplete lane results;
2. deduplicate findings;
3. resolve conflicting conclusions;
4. directly verify every proposed P0 and P1;
5. add omitted cross-lane risks;
6. reconcile the evidence plan;
7. preserve severity independently of remediation convenience;
8. classify P0/P1 remediation candidates and exclude every P2/P3 from code
   modification;
9. produce one authoritative finding ledger, deferred P2/P3 issue-ready ledger,
   verdict, risk, testing confidence, CI enforcement confidence, and provisional
   merge eligibility.

Parallel lanes never create competing final verdicts.

## Remediation and re-audit

Use exactly one remediation writer, and provide it only eligible P0/P1
findings. P2/P3 findings remain read-only deferred records. After tracked files
change:

1. run targeted validation;
2. rerun `fast --base <resolved-base>` only when the remediation invalidates the
   preflight evidence, repository policy requires it, or verification machinery
   changed;
3. run focused conformance evidence for verification machinery changes;
4. create a new immutable audit packet for the current state;
5. rerun the applicable audit lanes and synthesis.

Do not run the full `ship` profile after every remediation round. The mandatory
ship gate is reserved for the final committed audited `HEAD`.

Validation commands may run concurrently only when the repository or
`minimal-sufficient-testing` explicitly proves that they do not share mutable
state or outputs. Otherwise execute them sequentially.

## Final-gate overlap

While final `ship --base <resolved-base>` runs, read-only drafting may prepare a
PR body and final report skeleton from already-audited evidence. Do not push,
create or update a PR, file deferred-finding issues, merge, or clean branches
until the final gate passes for the exact committed SHA. After the gate, issue
search, deduplication, and creation remain centralized; parallel lanes never
mutate GitHub independently.

## Failure handling

- A failed or invalid preflight blocks the deep audit; no legacy fallback is
  allowed for a present adapter.
- A lane failure does not silently disappear. Synthesis records it and either
  reruns that lane sequentially or blocks when its required dimensions remain
  uncovered.
- A worker timeout or interruption is an audit-process blocker for that lane.
- Any tracked-file mutation during read-only parallel work invalidates the packet
  and stops the parallel audit.
