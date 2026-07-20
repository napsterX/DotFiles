# Repository Verification Standard V1

Status: Normative.
Version: 1.0.
Scope: Manish's application repositories that adopt the local verification contract.
Owner: This standard lives in the `.files` (DotFiles) repository under `global-claude/standards/repository-verification/` and governs agent and human verification behavior across repositories.

This standard was derived from a read-only audit of three pilot repositories: Hachira (HachiraEngine, Go), Fidem (Next.js / Supabase / Postgres), and Manydoors (Prism, Next.js / SQLite / LLM tutoring).
Each normative requirement below is supported by evidence from those audits, recorded in `audits/` and compared in `pilot-comparison.md`.
Where a requirement is a recommendation rather than a discovered fact, it is stated as such.

Convention in this document: MUST, MUST NOT, SHOULD, and MAY are used in the usual normative sense.

---

## 1. Purpose and authority

### 1.1 Local-first validation

Local validation is the authoritative Definition of Done.
A change is done when the repository's own `./scripts/verify` profiles pass locally at the depth required for its lifecycle stage, and the independent audit clears.
No remote system is the source of truth for correctness.
Evidence: Fidem operates in a declared "reduced mode" with no enforced remote gate, and Manydoors has no CI at all; both rely on local validation as the real gate, confirming local-first is the correct primary.

### 1.2 GitHub-minimal policy

GitHub Actions is a minimal, inexpensive repository-integrity backstop, not the primary gate.
It exists to catch integrity regressions cheaply, using only deterministic, dependency-light checks that need no secrets, services, databases, or browsers.
A repository with no CI configured is an accepted state; this standard does not require CI where none exists, though adopting a `github-minimal` workflow is recommended (it is the single largest improvement available to Manydoors).

### 1.3 Repository adapter responsibility

Each repository provides an executable `./scripts/verify` adapter implementing the interface in Section 2.
The adapter is a thin orchestrator: it selects and sequences the repository's own native tools per profile, classifies their outcomes (Section 8), and returns the exit codes in Section 9.
The adapter's implementation language is chosen by the repository (Bash or Go for Hachira, Node/`tsx` or npm for Fidem and Manydoors are natural fits).

### 1.4 Underlying tool responsibility

The underlying tools do the actual work.
`./scripts/verify` MUST NOT reimplement linters, test frameworks, SAST engines, dependency or software-composition scanners, SonarQube, OWASP standards, or performance-analysis platforms.
It orchestrates them.
Evidence: all three repositories already compose native tools (Go/gofmt/buf; Vitest/Playwright/eslint/gitleaks; tsc/node-test/ajv), and none reimplements a tool; the adapter continues that pattern.

### 1.5 `/audit-and-pr` authority

`/audit-and-pr` will later invoke `./scripts/verify ship` as the repository's authoritative shipping gate.
`/audit-and-pr` retains sole authority over independent audit, security review, risk classification, blocker classification, the PR workflow, merge policy, and the final audit verdict.
A passing `ship` gate is necessary but never sufficient: it does not replace the independent audit, and the audit may still return FAIL or raise blocking findings when `ship` is green.

### 1.6 Human and independent-review authority

Automated gates do not replace human judgment.
Threat modeling, architecture review, penetration testing, product-quality review, and independent audit remain human and independent responsibilities.
Evidence: Manydoors demonstrates the hard boundary - no automated check can prove the product is kid-worthy, visually excellent, accessible, or that tutor output is safe; those rest on LLM judges and human decisions and MUST stay advisory.
The adapter cannot self-authorize waivers, and passing the gate does not approve changes to the gate itself (Section 13).

---

## 2. Required interface

Every adopting repository MUST provide an executable `./scripts/verify` supporting exactly these six subcommands:

```text
./scripts/verify describe
./scripts/verify doctor
./scripts/verify fast
./scripts/verify full
./scripts/verify ship
./scripts/verify github-minimal
```

The interface is standardized; the adapter language and the underlying tooling are repository-selected.
Unknown subcommands or invalid arguments MUST return exit code 2 (Section 9).
The interface is fixed for V1: adapters MUST NOT add alternative top-level verbs that change the contract, though a subcommand MAY accept documented flags (for example `describe --json`, Section 10).
The three-repository audit found no repository that needs a seventh command or a protocol capability outside this interface (Section 15).

---

## 3. Profile semantics

A profile is lifecycle depth, not a check category.
Profiles are ordered by increasing assurance: `fast` < `full` < `ship`, with `github-minimal` a separate cheap backstop scope.

### 3.1 `fast`

Purpose: the tight inner-loop check run continuously while editing.
Minimum behavior: the cheapest meaningful correctness-and-quality signal, scoped to changed files or the affected package where the tooling supports it.
MUST be deterministic and dependency-light.
MUST NOT require external services, databases, browsers, or credentials.
Typically: formatting check, lint, type check, and fast unit tests.
Evidence: Fidem's `validate:fast` (~1 minute, offline) is a near-ideal reference; Hachira's static tier and Manydoors' typecheck+test+validate are the equivalents.
Cost target: short.

### 3.2 `full`

Purpose: the complete local assurance for a change before it is considered mergeable, independent of shipping and governance ceremony.
Minimum behavior: everything in `fast`, plus the full local test suites (unit, integration, and the repository-native architecture, data-integrity, security, reliability, and performance checks that have deterministic, measurable outcomes), at repository scope.
MAY require local services (database, local stack) declared by `doctor`.
Evidence: Hachira's `full` must include the docker `local-stack` group and the eight lint self-tests that CI runs but `make validate` omits - closing the local-versus-CI divergence is a primary reason the standard exists.
Cost target: moderate to long.

### 3.3 `ship`

Purpose: the authoritative release gate invoked by `/audit-and-pr`.
Minimum behavior: `ship` MUST include the complete mandatory `full` assurance required for release, plus shipping and governance prerequisites (Section 12): working-tree/branch/base state checks, issue-reference and implementation-log governance where the repository requires them, generated-file consistency, and any release-only checks.
`ship` is the union of "all mandatory `full` assurance" and "shipping/governance prerequisites."
`ship` MUST fail if any required check fails, is required-but-skipped without permission, or is required-but-unavailable (Section 8).
A green `ship` authorizes the shipment gate to proceed but does not by itself authorize merge; `/audit-and-pr` and its independent audit own that.

### 3.4 `github-minimal`

Purpose: the cheap CI backstop that runs in GitHub Actions.
Minimum behavior: a strict subset of deterministic, dependency-light checks that need no secrets, services, databases, or browsers, chosen to catch repository-integrity regressions cheaply.
MUST be a subset of what `full`/`ship` already enforce locally; it MUST NOT add CI-only checks that cannot be reproduced locally.
Evidence: Fidem's `validate:ci:minimal` (`validate:fast` + build with stub env) is the reference; Hachira's no-docker static tier and Manydoors' offline deterministic set are the equivalents.
Cost target: trivial to short.

### 3.5 Profile ordering invariant

Anything that fails `fast` MUST also fail `full` and `ship`.
`github-minimal` need not be a subset of `fast`, but every check it runs MUST also be enforced somewhere in `full`/`ship`.

---

## 4. Assurance domains

A domain classifies the type of assurance a check provides.
Profiles and domains are orthogonal:

```text
profile = lifecycle depth (fast / full / ship / github-minimal)
domain  = assurance category (what kind of confidence the check provides)
```

The seven domains:

1. Correctness: the change does what was asked and existing behavior still holds (tests, build/compile, type checks).
2. Quality: maintainability and hygiene (formatting, lint, static analysis, complexity, duplication, dead code, coverage where enforced).
3. Security: protection of secrets, data, authn/authz, tenancy, supply chain, and repository-specific security invariants (Section 5).
4. Architecture and data integrity: module boundaries, dependency direction, schema/migration validity, generated-artifact consistency.
5. Governance: repository-mandated process controls (documentation registries, issue references, implementation logs, ownership/CODEOWNERS, protected paths).
6. Reliability: concrete, deterministic behavior under failure (retries, idempotency, recovery, race conditions, cancellation, resource handling, failure paths). Included only when objectively testable.
7. Performance: measurable budgets (bundle size, binary size, benchmark regression, startup time, allocations, query counts, stable latency budgets). Included only when objectively measurable.

A single tool may span domains; classification is by the assurance it provides, not by the tool that provides it.

---

## 5. Security model

Every repository adoption audit MUST evaluate each of the following and record it as present, absent, or not-applicable with a reason:

- secret scanning;
- SAST (static application security testing);
- dependency and software-composition analysis (SCA);
- infrastructure-as-code scanning, where the repository contains IaC;
- container image scanning, where the repository builds container images;
- authentication tests;
- authorization tests;
- tenant-isolation tests, where the system is multi-tenant;
- workflow and supply-chain controls (pinned actions, least-privilege workflow permissions, protected-branch posture);
- secure file handling, where the repository accepts uploads or serves generated files;
- repository-specific security invariants that generic scanners cannot prove.

Evidence: the three-repository audit found that all three lack enforced secret scanning that fails closed, real SAST, and SCA (Hachira has none; Fidem's secret scan is fail-open and its `.gitleaks.toml` is uncommitted; Manydoors has none despite a prior real secret leak).
These are the generic, commodity checks and are the highest-value cheap additions in every repository.

### 5.1 What scanners can and cannot establish

- OWASP Top 10 is a risk taxonomy, not a checklist a tool can "pass."
- CWE Top 25 is a weakness taxonomy.
- OWASP ASVS can inform concrete, testable controls, and specific ASVS requirements MAY be mapped to specific tests.
- Scanners cannot establish general "OWASP compliance"; a passing scanner is evidence of the absence of known patterns, not proof of security.
- Automated gates do not replace threat modeling, architecture review, penetration testing, or independent audit.

### 5.2 Application-specific invariants

The highest-value security checks are repository-specific invariants that no generic scanner can prove.
These MUST be expressed as concrete tests or checks with explicit assertions, not as vague "verify security" gates.
Evidence: Fidem's tenant-isolation (RLS cross-tenant denial, service-role-bypass guard), storage-key org-namespacing, upload MIME/magic-byte/size validation, and Stripe webhook replay/idempotency are exactly such invariants; Hachira's RLS fail-closed, provider-seam confinement, and role-model separation are the same class.
A distinction the audit surfaced and the standard adopts: a static source-string scan that asserts a guard is present in source proves a quality-structural property, not runtime security behavior; the blocking security assurance MUST come from the runtime tests (which in both Fidem and Hachira are environment-gated), not from the static scan alone.

---

## 6. Quality model

Repository-native tools MAY cover: static bugs, coding standards, linting, maintainability, complexity, duplication, dead code, unsafe patterns, coverage, and dependency hygiene.

SonarQube is NOT required.
A repository MAY use SonarQube or an equivalent platform where it is already justified, but this standard does not mandate it, and `./scripts/verify` MUST NOT reimplement it.
Evidence: none of the three repositories uses or needs SonarQube; their native tools (Go vet/gofmt and bespoke lints; eslint/typescript and custom validators; tsc/node-test) already cover the quality concerns, with the notable gap that Manydoors has no linter or formatter at all - which is a missing native tool to add, not a reason to introduce a platform.

---

## 7. Reliability and performance

### 7.1 Reliability

Reliability checks MUST test concrete behavior, such as: retries, idempotency, recovery, race conditions, cancellation, resource handling, and failure paths.
A reliability check is eligible to gate shipping only when it is deterministic.
Nondeterministic reliability checks remain advisory (Section 8).
Evidence: Fidem's env-gated extraction/idempotency/lease-recovery/ledger-replay suites and Hachira's `seed-determinism-check` are deterministic and gate-eligible; Manydoors' `eval:evidence:verify` is a strong deterministic reliability gate.

### 7.2 Performance

Performance checks MUST use measurable thresholds, such as: bundle size, binary size, benchmark regression, startup time, allocations, query counts, and stable latency budgets.
Vague optimization gates (for example "verify performance optimization") are prohibited.
A performance check may gate shipping only when its budget is stable and deterministic in the execution environment.
Unstable performance checks (wall-clock timings on shared runners, Lighthouse scores subject to environmental noise) remain advisory.
Evidence: none of the three has a web-performance budget; Hachira's `migrate rehearse` 60s wall-clock budget and Manydoors' AI dollar-cost budgets are the only performance-shaped gates, and both are measurable; a screenshot-diff or Lighthouse gate would be environment-sensitive and MUST stay advisory.

---

## 8. Check outcomes

Every check reports exactly one outcome:

- pass: the check ran and succeeded.
- fail: the check ran and did not succeed.
- skipped: the check was intentionally not run under this profile.
- unavailable: the check could not run because a required dependency, environment, service, or secret was missing.
- not-applicable: the check does not apply to this repository or change.
- advisory: the check ran and produced findings but is non-blocking by policy.

Rules:

- A required check that reports fail fails the profile.
- A required check that reports skipped fails the profile, unless the profile explicitly permits skipping it.
- A required check that reports unavailable is not a success; it fails the profile (or, where the profile permits, downgrades the result), and it MUST be reported distinctly from fail so operators can tell "broken" from "could not run."
- A not-applicable outcome MUST carry a reason.
- Advisory outcomes never fail a profile; they are reported.
- Repository adapters MUST NOT self-authorize waivers: an adapter cannot silently reclassify a required check as advisory or not-applicable to make a profile pass.

Evidence: the `unavailable` outcome is essential and validated by all three repositories, whose true security/reliability proofs are environment-gated (Fidem RLS/commercial suites, Hachira docker local-stack, Manydoors billed paths); those MUST report `unavailable` when the environment is absent, never a false pass.
Fidem's browser lanes already enforce a minimum-executed-count floor for exactly this reason, and the standard adopts that intent.

---

## 9. Exit behavior

`./scripts/verify` uses a compact, portable exit-code model:

```text
0 = successful command or profile
1 = one or more required checks failed
2 = invalid invocation or unsupported argument
3 = adapter or protocol/configuration error
4 = required dependency, environment, service, or secret unavailable
5 = interrupted or timed out
```

Distinguishing 1 (a real failure), 3 (the adapter itself is misconfigured), and 4 (the environment could not satisfy the check) is required so callers, including `/audit-and-pr`, can react correctly: a 4 is an environment gap to resolve or declare, not a code defect.
The three-repository audit confirmed this model is adequate: every discovered check maps cleanly onto one of these codes, and no repository needs a code outside this set.

---

## 10. `describe`

`describe` MUST produce human-readable output enumerating, at minimum:

- adapter version;
- the profiles it supports;
- the checks it runs, grouped by profile;
- each check's assurance domain;
- each check's blocking or advisory status;
- high-level dependencies (which checks need a database, browser, network, or credentials).

### 10.1 Machine-readable `describe --json`

`describe` SHOULD support a `--json` flag emitting the same information as structured data.
In V1 this is optional, not required, and MAY be deferred.
Evidence and rationale: no pilot repository emits a machine describe today, and `/audit-and-pr` currently maps checks to obligations through bounded repository-native discovery rather than a machine contract; locked decision 4 also excludes a central `.engineering/verification-contract.json`.
Therefore V1 keeps the human-readable `describe` as the MUST and treats `--json` as a recommended addition that becomes required only when a programmatic consumer (a future `/audit-and-pr` integration) actually parses it.
When implemented, `describe --json` MUST be secret-free (it names dependencies such as credentials by category, never values), consistent with Fidem's existing secret-free evidence manifest.

---

## 11. `doctor`

`doctor` performs read-only environment-readiness checks.
It MAY inspect: executable availability, supported tool versions, daemon availability, configuration-file presence, environment-variable presence (name only, never value), service reachability, and temporary-directory writability.

`doctor` MUST NOT: install dependencies, modify configuration, apply migrations, mutate databases, expose secret values, or run the full test suite.

The three-repository audit confirms `doctor` can remain strictly read-only in every pilot, provided it probes and reports rather than acts:

- Hachira: read-only for the entire static tier; it MUST exclude the docker `local-stack` group (which mutates a throwaway local Postgres) and instead report whether docker and the stack are available.
- Fidem: read-only for the deterministic tier; it MUST NOT run `supabase start` (Docker) or any live lane, and instead probe ports 54321/3000 and report which live lanes would run - mirroring the repository's existing "envScripts are never auto-run" rule.
- Manydoors: read-only for typecheck/test/validate/eval-evidence and the asset validators; it MUST exclude every `db:*` and billed path and may only report Drizzle drift, never regenerate it.

In all three, service "reachability" MUST be a passive probe, not a start action.

---

## 12. Ship-state rules

`ship` MUST evaluate repository state, not only code checks:

- Dirty working tree: uncommitted modifications to in-scope tracked files MUST block, because the audited artifact must match the committed artifact. Unrelated pre-existing changes MUST be preserved and reported, never discarded.
- Staged but uncommitted files: treated as a dirty tree for the shipped scope and MUST block.
- Unexpected untracked files: MUST be surfaced; the adapter reports them and MUST NOT delete them.
- Generated output: generated artifacts MUST be consistent with their sources (regeneration produces no diff); an inconsistency MUST block. Evidence: Fidem already guards this (`validate:artifacts` + schema snapshot); Hachira (buf-generated) and Manydoors (Drizzle migrations) currently lack a drift check and should add one.
- Branch and base state: `ship` MUST confirm the change is on an appropriate non-default branch with a determinable merge-base, per repository convention.
- Issue references: where the repository requires an issue/ticket reference, `ship` MUST enforce it (Hachira's ticket/issue guard, Fidem's `validate:tracking`, Manydoors' commit convention).
- Implementation logs: where the repository requires an implementation-log entry, `ship` MUST enforce it (all three mandate one).

`ship` MUST NOT introduce signed evidence, cached ship evidence, or any central execution-state store.
Each `ship` invocation validates the current state directly.

---

## 13. Governance-sensitive changes

Changes to the verification machinery are governance-sensitive and require stronger review:

- `scripts/verify` itself;
- verification helper scripts;
- scanner configuration;
- skip logic;
- thresholds and budgets;
- `github-minimal` workflows;
- any rule that weakens validation.

Passing the gate does not independently approve a modification to the gate.
A change that alters what the gate enforces MUST be reviewed as a governance change, not merely allowed because the modified gate still returns 0.
The adapter cannot grant its own waiver, raise its own thresholds, or mark its own required checks advisory to pass.
This aligns with the `/audit-and-pr` remediation policy, which already forbids auto-fixing architecture boundaries, protected zones, and branch-protection settings.

---

## 14. Unadopted repositories

When `./scripts/verify` is absent, future `/audit-and-pr` behavior is:

- report the adapter as absent;
- use bounded repository-native validation discovery (discover the repository's real formatting, lint, type-check, test, static-analysis, and build commands) rather than inventing commands;
- do not silently create files in the repository;
- do not automatically block solely because adoption is missing;
- report the governance gap so adoption can be scheduled.

Absence of the adapter is a governance gap to record, not automatic grounds to fail an otherwise-sound change.
Evidence: `/audit-and-pr` already delegates command discovery to `minimal-sufficient-testing`, whose policy is to "discover actual repository commands" and "not invent commands"; this behavior is exactly the bounded-discovery fallback and requires no new mechanism.

---

## 15. Explicit exclusions (deferred capabilities)

V1 deliberately excludes the following:

- a standalone central `repo-governance` executable;
- `.engineering/verification-contract.json` or any central machine contract file;
- portfolio inventory, global repository dashboards, or cross-repository roll-ups;
- signed evidence, cached ship evidence, or any attestation store;
- central execution state or a shared results database;
- global schema-migration infrastructure across repositories;
- unnecessary cross-platform abstraction layers;
- mandatory SonarQube or any mandated commercial quality platform;
- any vague gate ("verify performance optimization", "verify security", "verify OWASP compliance", "ensure code quality").

### 15.1 V1 changes required by the three-repository audit

None to the protocol.
The audit found that the six-command interface, the four profiles, the seven domains, the six-outcome model, and the six exit codes cover all three repositories without gaps, and that no repository needs a capability outside V1.
The audit did surface repository-level gaps (absent SCA/SAST/enforced-secret-scan across all three; Hachira's `make validate`-versus-CI divergence and unwired doc-registry; Manydoors' absent CI, linter, and unwired asset validators; Fidem's fail-open secret scan and missing bundle budget), but these are adapter-implementation and repository-tooling gaps to close during adoption, not changes to this standard.

### 15.2 Deferred, revisitable in a later version

- `describe --json` as a hard requirement (Section 10.1), once a programmatic consumer exists.
- A standardized machine-readable outcome record, if and only if `/audit-and-pr` later needs to consume `ship` results programmatically; it MUST remain local and uncached if introduced.
