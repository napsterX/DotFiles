# Hachira Verification Baseline

Repository: `HachiraEngine` (Go modular monolith), audited read-only at branch `main`, clean tree.
Method: file reading and read-only shell only; no build, test, format, or generator was executed against the repository, which is byte-for-byte unchanged.
Evidence tags: FACT = read from a file; INTERP = interpretation; REC = recommendation; OPEN = unresolved question.

This baseline informs `../v1-specification.md`.
It does not implement `scripts/verify` and proposes no change to Hachira.

## 1. Architecture and toolchain summary

FACT.
Go, module `github.com/napsterX/HachiraEngine`, `go 1.26` (CI pins `1.26`).
Modular monolith: `internal/` holds domain modules (`identity`, `inventory`, `governance`, `compliance`, `evidence`, `assessment`) plus `apibff`, `controlplane`, and cross-cutting `platform`; `pkg/substrate` is a four-interface provider seam (`BlobStore`, `KeyWrapper`, `SecretStore`, `DnsAndLb`) with no bindings; `cmd/` holds `migrate` and `seed`; `db/migrations/` holds 10 expand/contract SQL migrations; `proto/` is a placeholder Buf module.
Stage: milestone M0 reached, mid-Phase-2 (identity, tenancy, residency, authz built; no API server, no product schema or RLS product tables, no connector runtime yet).
Toolchain exercised by checks: `go`, `gofmt`, `jq`, `python3`, `shellcheck`, `buf` (installed in CI via `go install ...@v1.71.0`), `docker`/`docker compose`, `gh`, and `psql` inside the Postgres container.
Governance corpus is unusually deep: frozen Architecture v1.0, engineering contracts, a machine-readable document registry (`docs/governance/document-registry.json`, ~132 KB) with a Python validator, CODEOWNERS, a ticket taxonomy, and `implementation-logs/`.

## 2. Current validation entry points

FACT.
There are three non-equivalent entry points, which is the central problem a unified `scripts/verify` would solve:

1. `make validate` (local): `go build`, `go vet`, gofmt `-l` check, `go test`, then the static scripts `archlint`, `check-module-boundaries`, `provider-seam-lint`, `xml-parser-containment-lint`, `dataaccess-import-lint`, `check-codeowners-coverage`, `seed-determinism-check`, `seed-release-gate`, and `migrate validate`.
2. `.github/workflows/ci.yml` (three jobs) is the real definition of done (Section 4).
3. Manual / on-demand: `check-doc-registry.sh`, `go test -race` (referenced only in a handoff doc, wired nowhere), and the docker-backed targets.

INTERP.
`make validate` omits every lint self-test, `shellcheck`, `bash -n`, the Buf gate, the SAML fuzz smoke, the doc-registry validator, the ticket/PR governance guards, and all integration tests.
A green `make validate` therefore does not imply a green CI.
This gap is exactly what a standardized `full`/`ship` profile should close.

## 3. Complete check inventory

The full field-by-field classification table (Check ID, command, source, domain, scope, cost, dependencies, context, candidate profiles, blocking, determinism, duplication, gap) is preserved in the raw audit and summarized here.
Static, no-docker, blocking checks: `go-build`, `go-vet` (quality), `gofmt-check` (quality, read-only `-l`), `go-test-unit` (correctness), `archlint` and `check-module-boundaries` (architecture), `provider-seam-lint`, `xml-parser-containment-lint`, `dataaccess-import-lint` (security/architecture), `check-codeowners-coverage` and `check-ticket-reference` (governance), `migrate validate` (architecture-data), `seed-determinism-check` (reliability), plus `bash -n` and `shellcheck` (quality, CI-only today).
Heavier no-docker checks: `seed-release-gate` (reliability/performance flavor), `saml-fuzz-smoke` (security, ~90s, timing-sensitive), `buf-governance` + `buf-breaking-tripwire` (governance), and the eight lint `_test.sh` self-tests (meta, CI-only).
PR-context governance: `check-pr-governance` (needs `gh` auth and an open PR).
Docker + Postgres (+ PgBouncer), environment-sensitive: `stack-health` (`dev-up`), `migrate rehearse`, `migrate check-roles`, `dataaccess-integration` (RLS fail-closed), `identity-integration` (OIDC/session).
Advisory / ungated today: `check-doc-registry` and its self-test (Python, standard library only) - the subject of issue #122.

## 4. Existing GitHub Actions usage

FACT.
`.github/workflows/ci.yml`, `permissions: contents:read, pull-requests:read`, triggered on push to `main` and PRs to `main`; no scheduled runs, no matrix.
Three jobs:

- `definition-of-done` (no docker): `bash -n` and `shellcheck` over scripts and hooks; `go build`; `go vet`; gofmt `-l` gate; `go test`; `make saml-fuzz-smoke` (6 fuzz targets, 15s each); `migrate validate`; `seed-determinism-check`; `seed-release-gate`; the six boundary lints each paired with its `_test.sh` self-test; and, PR-only, the ticket-reference guard and `check-pr-governance.sh`.
- `protobuf-governance`: pinned `buf@v1.71.0` via `go install` (checksum-verified by the Go module DB, no third-party Action), `buf lint` + additive-only `buf breaking`, plus `buf-breaking-tripwire_test.sh`.
- `local-stack` (docker, 20-min cap): image pull with 3x retry, `dev-up` health wait, `migrate rehearse` (60s wall-clock budget), `migrate check-roles`, dataaccess integration (RLS fail-closed), identity OIDC integration, teardown.

FACT (documented known limitation).
A named check is not automatically a required status check; marking `definition-of-done` required on `main` is an unset branch-protection setting (single real contributor).

## 5. Existing local validation behavior

FACT.
`make validate` is the documented local gate, weaker than CI (Section 2).
`scripts/git-hooks/commit-msg` delegates to `check-ticket-reference.sh` but is not auto-installed (requires manual `core.hooksPath`).
`HACHIRA_SKIP_TICKET_GUARD=1` bypasses the ticket guard (documented as exceptional).
The eight lint self-tests run only in CI, so a developer editing a lint locally gets no self-test feedback.

## 6. Security coverage

Present (FACT): three import-boundary security lints (provider-seam confinement of cloud SDKs to `pkg/substrate`, denylist so fail-open; XML-parser containment to `internal/identity/samlsp`, allowlist so fail-closed; data-access chokepoint confining `pgx`/`internal/platform/db`), docker-gated runtime security tests (RLS fail-closed, migration-role separation, `check-roles` role-model assertions, OIDC/tenant-session integration), SAML XML-surface fuzz smoke, the Buf additive-only breaking gate, and secret hygiene by construction (`.gitignore` plus a `SecretStore` seam that accepts no secret literal).

Absent (FACT, no evidence in any file): secret scanning (gitleaks/trufflehog), SAST (gosec/semgrep/CodeQL), dependency/SCA vulnerability scanning (govulncheck/osv-scanner/Dependabot; no `dependabot.yml`), and container/IaC image scanning (trivy/grype).
This is the largest security-tooling gap for a security-sensitive backend.

INTERP.
The present security checks are mostly application-specific invariants (boundary confinement, RLS fail-closed, role model) that a generic scanner cannot prove; the absent checks are the generic, commodity ones.

## 7. Quality coverage

Present (FACT): `go build`, `go vet`, gofmt `-l` gate, `go test`, `bash -n`, `shellcheck` (CI only), and eight fixture-based lint self-tests proving each governance lint actually catches its violation.

Absent (FACT): `staticcheck`/`golangci-lint`, cyclomatic-complexity/dead-code tooling beyond archlint, test-coverage measurement or threshold (`-cover`), the race detector in CI (`-race` is manual-only), and `actionlint` on workflow YAML (named in issue #122 acceptance but unwired).
`go test` in the DoD job runs without `-count=1`, so cached results can be reused.

## 8. Architecture and data checks

FACT.
`archlint` enforces interface-only cross-module imports (a module is governed iff it declares an `internal/<name>/interface` package; fail-open for never-declared directories by design).
`check-module-boundaries` asserts the seven fixed governed units each keep a private impl plus a published interface package, closing archlint's self-declaring gap.
`provider-seam-lint`, `xml-parser-containment-lint`, and `dataaccess-import-lint` are the import-boundary lints above.
`migrate validate` performs deterministic, database-free migration validation (naming, additive-first expand/backfill/contract sequencing, destructive-DDL and role-switch guards).
`migrate rehearse|check-roles|apply|status` are database-touching and require the docker stack; `rehearse` enforces a 60s (env-overridable) wall-clock budget.

## 9. Governance checks

FACT.
`check-codeowners-coverage` requires every governed path to have an explicit owning CODEOWNERS line.
`check-ticket-reference` requires non-bookkeeping commits to cite a `HCH-P<NN>-<WS>-<NNN>` ticket and a `#<n>` issue.
`check-pr-governance` (CI PR-only, needs `gh`) requires a ticket in the PR title and a body linking an issue, naming a real implementation-log path, and filling the Contracts/Security/Residency/Observability/Tests sections.
`buf-governance` + `buf-breaking-tripwire` enforce the additive-only Protobuf contract gate.
`check-doc-registry` (`.sh`/`.py`, standard-library Python) validates the document-registry invariants and the generated `docs/README.md` index but is not wired into any gate - the issue #122 gap; its `--write` mode mutates, the default check mode is read-only.
CODEOWNERS second-reviewer enforcement is declared but not enforceable (single contributor, unset branch protection).

## 10. Reliability checks

FACT.
`seed-determinism-check` builds `cmd/seed`, runs it twice, and asserts byte-identical output plus a stable self-reported sha256 (no docker).
`seed-release-gate` runs the `release-gate-100k` and `cell-canary` profiles twice each and asserts byte-identical output against pinned golden digests (no docker).
`dev-up` stack-health fails if any service is unhealthy; `migrate rehearse`'s wall-clock budget is a reliability/perf proxy.
INTERP: there is no generic async-job reliability harness yet, because no such runtime exists at M0.

## 11. Performance checks

FACT.
No `go test -bench` anywhere.
The only performance-shaped gates are `seed-release-gate` (proves the 100k-asset scale harness reproduces) and `migrate rehearse`'s 60s wall-clock budget.
INTERP: both are determinism gates with a performance flavor, not latency/throughput benchmarks; true perf benchmarking is future work because no serving path exists.
This is the model the standard endorses: measurable, deterministic budgets, not vague optimization gates.

## 12. Missing or weak coverage

INTERP unless noted.
1. No secret-scan, SAST, SCA, or container scan (FACT) - the largest security gap.
2. No `-race` in CI; concurrency regressions can merge.
3. No coverage measurement or threshold.
4. No `staticcheck`/`golangci-lint`.
5. `check-doc-registry` and its self-test are ungated (issue #122, FACT).
6. No deterministic no-em-dash documentation guard, though the rule is normative (issue #122, FACT that the rule exists).
7. No `actionlint` (issue #122 acceptance names it; unwired, FACT).
8. `make validate` is materially weaker than CI (FACT/INTERP).
9. Branch protection and CODEOWNERS second-reviewer count are unset (FACT, documented).
10. Commit-msg hook is not auto-installed (FACT).
11. Fail-open surfaces: provider-seam-lint denylist and archlint self-declaring boundary (FACT, documented, mitigated by CODEOWNERS + go.mod review).

## 13. Duplicate or misplaced checks

FACT/INTERP.
`migrate validate` runs in three places (`make validate`, CI DoD, inside `migrate.sh`) - intentional layering, minor duplication.
The real misplacement is that the eight self-tests run only in CI, never in `make validate` - the meta-tests belong in a local profile too.
`go build` is largely subsumed by `go vet`/`go test` but kept explicit for a cheaper, clearer failure signal (acceptable).
The five import-boundary lints share a mechanism but each governs a distinct concern - not true duplication.
Documentation drift: `repo-baseline.md` claims the local-stack job re-runs seed-determinism; `ci.yml` does not.

## 14. Recommended `fast` composition

REC (changed-files or package scope where the Go tooling allows; must stay no-docker, no-network, deterministic).
`go build`, `go vet`, `gofmt-check`, `go test` (unit), `migrate validate`, and the six boundary lints (`archlint`, `check-module-boundaries`, `provider-seam-lint`, `xml-parser-containment-lint`, `dataaccess-import-lint`, `check-codeowners-coverage`).
Cost target: short.

## 15. Recommended `full` composition

REC (repository scope, may use docker).
Everything in `fast`, plus `bash -n`, `shellcheck`, the eight lint self-tests, `seed-determinism-check`, `seed-release-gate`, `saml-fuzz-smoke`, `buf-governance` + `buf-breaking-tripwire`, `check-doc-registry` + self-test (closing issue #122), and the docker `local-stack` group (`stack-health`, `migrate rehearse`, `migrate check-roles`, `dataaccess-integration`, `identity-integration`).
REC additions to raise assurance: `-race` on the platform packages, `govulncheck` (SCA), a secret scan, and `actionlint`.

## 16. Recommended `ship` composition

REC.
The complete mandatory `full` assurance above, plus the shipping and governance prerequisites: `check-ticket-reference` over the shipped commits, `check-pr-governance` where a PR exists, a clean working tree, a determinable merge-base against `main`, generated-artifact consistency (buf-generated outputs), and the implementation-log presence Hachira already mandates.
The docker `local-stack` group is mandatory for `ship` (it is the only proof of RLS fail-closed and role separation) but must be declared as environment-dependent so an unavailable stack reports `unavailable` (exit 4), never a false pass.

## 17. Recommended `github-minimal` composition

REC (cheap, deterministic, no docker, no secrets; a subset of `full`/`ship`).
`go build`, `go vet`, `gofmt-check`, `go test` (unit), `migrate validate`, the six boundary lints (optionally with self-tests), `seed-determinism-check`, `bash -n`, `shellcheck`, `check-doc-registry`, and `buf lint`.
All need only `go`, `jq`, `python3`, `shellcheck`, and optionally `buf`; none need docker.
`check-ticket-reference` is cheap and belongs here on the PR path.

## 18. Blocking versus advisory recommendations

REC.
Blocking: the entire static tier, `migrate validate`, `seed-determinism-check`, `seed-release-gate`, the Buf gate, and the docker RLS/role/identity integration tests when the stack is available.
Blocking-when-relevant (conditional): `saml-fuzz-smoke` (timing-sensitive but bounded; keep blocking with a fixed seed budget), `check-ticket-reference`/`check-pr-governance` (PR context), `db:schema`-style drift once it exists.
Advisory until stabilized: coverage reporting, and any future latency benchmark.
`check-doc-registry` should move from advisory to blocking (issue #122).

## 19. Dependencies and environment constraints

FACT.
No docker: `go` toolchain checks, boundary lints (`go`+`jq`), codeowners (`bash`/`grep`), seed determinism/release gate (`go`), `migrate validate` (`go`), doc-registry (`python3`), `shellcheck`, `bash -n`; the Buf gate needs `buf`.
Docker + Postgres (+ PgBouncer): `dev-up` health, `migrate rehearse/check-roles/apply/status`, dataaccess integration, identity integration - the only network/external/timing-sensitive gates.
Network: docker image pulls (rate-limit-prone, 3x retry), `buf` install, `gh` API for PR governance, and the buf-breaking base-ref fetch.
Tool prerequisites: `jq`, `python3`, `shellcheck`, authenticated `gh`, `go 1.26`.
No browser/E2E dependency (no UI).

## 20. Risks and unresolved questions

OPEN.
Is `actionlint` run anywhere today? No file references it; issue #122 lists it in acceptance - treat as expected-but-unwired.
Is `definition-of-done` a required status check on `main`? Not determinable from the repo; documented as an unset admin setting.
Whether `-race` coverage is expected per release: engineering-principles asserts an unset-context zero-rows proof per release, which maps to the docker integration suite, not a `-race` unit run.
The docker `local-stack` job is the flaky/expensive tier (image pulls, 60s rehearsal budget, 20-min cap) and is unsuitable for a fast local loop.

## 21. Recommended future implementation scope

REC (out of scope for this audit; for a later adapter-implementation prompt).
Implement `scripts/verify` as a thin Bash or Go adapter that: composes the profiles above from the existing Make targets and scripts; makes the docker tier declare `unavailable` cleanly via `doctor`; wires the ungated `check-doc-registry` + self-test and `actionlint` (issue #122); and adds the absent commodity security checks (`govulncheck`, a secret scan, optionally `staticcheck` and `-race`) as new native tools the adapter orchestrates rather than reimplements.
The adapter closes the `make validate`-vs-CI divergence by making `full` the single authoritative local definition of done.

Issue #122 (`[HCH-P02-DOCS-011]`, OPEN) is directly aligned: it already asks to wire the doc-registry validator and self-test into the DoD job, add the no-em-dash guard, and pass `actionlint` - all of which the standard would fold into `full`/`ship`.
