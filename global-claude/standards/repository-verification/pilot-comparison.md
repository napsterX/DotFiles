# Pilot Comparison and Synthesis

A cross-repository synthesis of the read-only audits of Hachira (HachiraEngine, Go), Fidem (Next.js / Supabase / Postgres), and Manydoors (Prism, Next.js / SQLite / LLM tutoring).
It establishes whether one six-command `./scripts/verify` interface is technology-neutral across all three, and recommends an implementation order.
Facts come from the three baselines in `audits/`; recommendations are labelled.

---

## 1. Common protocol requirements

Requirements that all three repositories share and that the standard makes normative:

- A cheap, offline, deterministic inner-loop gate exists in every repo (Fidem `validate:fast`, Hachira static tier, Manydoors typecheck+test+validate). This is `fast`/`github-minimal`.
- A deeper local gate exists or is needed in every repo, and in two of three it is stronger than what runs remotely (Hachira CI is stronger than `make validate`; Fidem local is stronger than the reduced-mode remote). Unifying these is `full`/`ship`.
- Every repo has environment-gated checks whose true assurance cannot run offline (Fidem RLS/commercial suites, Hachira docker local-stack, Manydoors billed model paths). All three require the `unavailable` outcome and exit code 4 so a missing environment never reads as a pass.
- Every repo has repository-specific architecture/governance invariants expressed as concrete checks (boundary lints, ownership registries, content/curriculum validation, migration validators). These are the `architecture and data integrity` and `governance` domains.
- Every repo mandates an implementation-log and an issue/ticket reference; all three want these enforced at `ship`.
- Every repo already composes native tools and reimplements none; the adapter-orchestrates-tools rule fits all three without friction.

## 2. Meaningful repository differences

- Language and toolchain: Go + Make + buf + docker (Hachira); Next.js + npm + Supabase/Postgres + Vitest/Playwright (Fidem); Next.js + npm + SQLite/Drizzle + node:test + `tsx` + a bespoke art pipeline (Manydoors).
- CI maturity: Hachira has a real three-job CI; Fidem has rich CI but in dispatch-only "reduced mode"; Manydoors has no CI at all.
- Security surface: Fidem is the heaviest (multi-tenant RLS, uploads, Stripe webhooks, storage privacy); Hachira is backend-security-sensitive (RLS fail-closed, provider seam, SAML); Manydoors is lighter at the repo layer (session/PIN/cookie-authority) but has a real kid-safety product surface that is human/LLM-judged, not gateable.
- Data layer: Postgres + 165 migrations + RLS (Fidem); Postgres migrations + role model (Hachira); SQLite + Drizzle, no RLS (Manydoors).
- Determinism profile: Hachira and Fidem's blocking checks are almost entirely deterministic; Manydoors' most product-critical checks (tutor safety, kid-worthiness) are inherently non-deterministic and must stay advisory.
- Quality tooling: Fidem and Hachira have linters/formatters and static analysis; Manydoors has no ESLint or Prettier at all.

## 3. Is the interface technology-neutral? (evidence)

Yes.
The audit found that the six commands, four profiles, seven domains, six outcomes, and six exit codes map cleanly onto all three repositories despite their sharply different stacks:

- `fast` binds to `validate:fast` (Fidem), the no-docker static tier (Hachira), and typecheck+test+validate (Manydoors).
- `full` binds to `validate:local:full` + env suites (Fidem), the CI union including docker and self-tests (Hachira), and the offline set + build + eval-evidence (Manydoors).
- `github-minimal` binds to `validate:ci:minimal` (Fidem), the no-docker static subset (Hachira), and the offline deterministic set (Manydoors, which has no CI today).
- `doctor` is read-only in all three when it probes and reports rather than starting services.
- Exit code 4 (`unavailable`) is exercised by all three env-gated tiers.

No repository required a seventh command, an extra profile, or a capability outside V1.
The one adapter-language difference (Bash/Go versus Node/npm) is exactly what "the interface is standardized, the tooling is repository-specific" is designed to absorb.
Conclusion: the interface is technology-neutral on the evidence of three materially different repositories.

## 4. Required V1 changes discovered by the audit

None to the protocol.
The interface, profiles, domains, outcomes, and exit codes are adequate as specified (see `v1-specification.md` Section 15.1).
The audit did confirm two design choices that were previously open:

- `describe --json` is deferred (optional in V1): no repo emits a machine describe, and `/audit-and-pr` uses bounded discovery, not a machine contract (spec Section 10.1).
- `doctor` stays strictly read-only, defined as probe-and-report, because every repo has a live tier that must not be auto-started (spec Section 11).

All other findings are repository-tooling gaps to close during adapter implementation, not standard changes.

## 5. Profile comparison across the three repositories

| Profile | Hachira | Fidem | Manydoors |
|---|---|---|---|
| `fast` | go build/vet, gofmt, unit test, migrate validate, 6 boundary lints | `validate:fast` (typecheck, lint, unit, static, chaos, migrations, architecture, rls-posture, artifacts, tracking) | typecheck, unit test (incl. control-char SAST), content `validate`, living-atlas asset validators |
| `full` | `fast` + shellcheck, self-tests, seed-release-gate, saml-fuzz, buf gate, doc-registry, docker local-stack (RLS/roles/identity) | `validate:local:full` + env RLS/commercial/integration/schema-drift | `fast` + eval-evidence-verify, build, map-art-proof, cost/budget tests |
| `ship` | `full` + ticket/PR governance, clean tree, merge-base, generated-artifact consistency, impl-log | `full` + clean tree, artifact/schema consistency, tracking, docs-impact, impl-log; env security suites mandatory-when-relevant | `full` + clean tree, merge-base, issue-ref, impl-log, Drizzle drift; LLM/human checks stay advisory |
| `github-minimal` | no-docker static subset (build/vet/gofmt/test/migrate-validate/boundary lints/seed-determinism/shellcheck/doc-registry/buf lint) | `validate:ci:minimal` (`validate:fast` + build, stub env) | offline deterministic set (typecheck/test/validate/eval-evidence/asset validators) - first CI for this repo |

## 6. Security-domain comparison

Generic checks (commodity, and absent or weak in all three):

- Secret scanning: Hachira none; Fidem present but fail-open locally with an uncommitted allowlist; Manydoors none despite a prior real leak.
- SAST: absent in all three (Fidem and Hachira have bespoke structural lints, not taint analysis; Manydoors has a one-test control-char SAST).
- SCA/dependency scanning: absent in all three.
- Container/IaC scanning: absent (Hachira has a compose stack; not scanned).

These are the standard's recommended cheap additions in every repository.

Application-specific invariants (cannot be proved by a generic scanner, and are the true security gate):

- Fidem: RLS cross-tenant denial, service-role-bypass guard, storage-key org-namespacing, upload MIME/magic-byte/size, webhook replay/idempotency.
- Hachira: RLS fail-closed, migration-role separation, provider-seam confinement, XML-parser containment, SAML fuzz.
- Manydoors: session HMAC, PIN gate, cross-learner cookie-authority; kid-safety is grounding-contract + LLM-judged + human, not gateable.

A cross-cutting finding: static source-string "security" scans (common in Fidem) prove a guard is present in source, not that it behaves; the blocking security assurance must come from the runtime tests, which are environment-gated in both Fidem and Hachira.

## 7. Quality-domain comparison

- Hachira: go vet, gofmt gate, go test, shellcheck, lint self-tests; absent: staticcheck, coverage, `-race` in CI.
- Fidem: eslint (flat config), dual-tsconfig typecheck, large unit + static-invariant suites, axe-core a11y; residual legacy `.eslintrc.json`.
- Manydoors: node:test suite (130 files) but no ESLint and no Prettier at all - a missing native tool, not a reason for a platform.

None resembles a SonarQube need; the concerns SonarQube would cover (complexity, duplication, dead code, coverage) are either already handled by native tools or are better addressed by adding the specific missing native tool.
Answer to "does any repo need SonarQube?": no; native tools are sufficient, and the standard must not mandate it.

## 8. Reliability and performance comparison

Reliability (deterministic, gate-eligible):

- Hachira: `seed-determinism-check`, `seed-release-gate`; runtime recovery is docker-gated.
- Fidem: unit chaos/lifecycle + env-gated idempotency/lease-recovery/ledger-replay suites.
- Manydoors: `eval:evidence:verify` (offline evidence-integrity) and cost/budget tests.

Performance (measurable versus subjective):

- Measurable budgets that exist: Hachira `migrate rehearse` 60s wall-clock budget; Manydoors AI dollar-cost budgets.
- Absent in all three: a web-performance/bundle budget.
- Subjective/flaky and must stay advisory: Manydoors screenshot-diff proof and any future Lighthouse/axe run; wall-clock timings on shared CI runners.

Conclusion: performance gates are viable only as measurable, deterministic thresholds (bundle size, binary size, benchmark regression, dollar-cost); the standard prohibits vague optimization gates and keeps unstable checks advisory.

## 9. GitHub-minimal recommendations

- Hachira: a no-docker workflow running the static subset (build, vet, gofmt, unit test, migrate validate, boundary lints, seed determinism, shellcheck, doc-registry, buf lint). Cheap, deterministic, no secrets. Also wire the currently-ungated doc-registry validator (issue #122).
- Fidem: keep `ci-minimal.yml` (`validate:fast` + build), and add offline SCA (`npm audit`/`osv-scanner`) as a cheap high-value backstop.
- Manydoors: introduce the first CI as a `github-minimal` workflow running the offline deterministic set (typecheck, test, validate, eval-evidence, asset validators). This is the single largest improvement available to any of the three, because Manydoors merges green today with zero checks.

All `github-minimal` sets must stay a subset of `full`/`ship` and require no secrets, services, databases, or browsers.

## 10. The twenty Phase-5 comparison questions (explicit answers)

1. Genuinely common concepts: an offline fast gate, a deeper local gate, env-gated deep assurance, repo-specific architecture/governance invariants, mandatory impl-log + issue reference, and native-tool orchestration.
2. Repository-specific checks: boundary lints/buf/SAML (Hachira); RLS/upload/webhook/Stripe suites (Fidem); content-registry/eval-evidence/living-atlas/kid-safety (Manydoors).
3. Does the six-command interface fit all three? Yes, with no gaps (Section 3).
4. Any repository needs a protocol capability missing from V1? No.
5. Can `doctor` stay read-only for all three? Yes, defined as probe-and-report; it must never start the live tiers.
6. Can `ship` be authoritative for all three? Yes, provided env-gated true-security suites are mandatory-when-relevant and report `unavailable` when the stack is down.
7. Too expensive/unreliable for `ship`: Fidem full browser suite (20-30 min, flaky) and live Textract corpus (billed); Manydoors LLM-judged evals and live integration; screenshot-diff proofs. Keep pre-release/advisory.
8. Belong only in `full`: Hachira docker local-stack and lint self-tests; Fidem env RLS/commercial/integration and schema-drift; Manydoors build and eval-evidence-verify.
9. Cheap enough for `github-minimal`: the offline deterministic subsets in Section 9, plus SCA.
10. Where a shared standard would create artificial wrappers: forcing a common check runner or a uniform config format would wrap three healthy native toolchains for no benefit; the standard standardizes the interface only.
11. Where profile semantics could drift: `full` versus `ship` boundary (which env checks are mandatory), and whether static "security" scans count as security or quality. The standard pins both (spec Sections 3.3, 5.2, 8).
12. Common requirements that should become normative: the six-outcome model with `unavailable`, ship-state rules, the read-only `doctor` contract, and mandatory impl-log/issue-ref enforcement at `ship`. Done in the spec.
13. Apparent commonality that should stay repository-specific: the actual check commands, config formats, and adapter language; "everyone runs a linter" does not mean "everyone runs the same linter."
14. Generic security checks: secret scanning, SAST, SCA, container/IaC scanning.
15. Application-specific security invariants: RLS/tenant isolation, storage-key namespacing, upload validation, webhook replay/idempotency, provider-seam confinement, role-model separation, cookie-authority (Section 6).
16. Quality checks resembling SonarQube: complexity, duplication, dead code, coverage - all either covered by native tools or better solved by adding the specific missing native tool.
17. Does any repo need SonarQube? No; native tools suffice.
18. Performance checks with measurable budgets: migrate-rehearse wall-clock budget (Hachira), AI dollar-cost budgets (Manydoors); a bundle-size budget is a recommended add for the two Next.js apps.
19. Proposed performance checks that would be subjective/flaky: Lighthouse scores, screenshot-diffs, wall-clock latency on shared runners - advisory only.
20. Reliability checks deterministic enough to gate shipping: seed-determinism (Hachira), env-gated idempotency/recovery suites (Fidem), eval-evidence-verify and cost/budget tests (Manydoors).

## 11. Recommended pilot implementation order

Recommendation: two waves.

- Wave 1 (reference): Fidem.
  It is the most mature (a working `validate:fast`, a risk-based local selector, a secret-free evidence manifest, and CI anti-cheat patterns already in place), so its adapter is mostly "compose existing scripts behind the six commands." Building it first validates the profile boundaries, the outcome model, the `unavailable`/exit-4 behavior, and the read-only `doctor` contract against the hardest security surface, and produces a reference other adapters copy.
- Wave 2 (parallel): Hachira and Manydoors.
  They are technologically independent (Go/Make/docker versus Next/SQLite/`tsx`), share no code, and have no ordering dependency once the contract is proven. Hachira's adapter mainly composes existing Make targets and scripts and wires the ungated doc-registry (issue #122). Manydoors' adapter is the most net-new (first CI, wire the invisible asset validators, add lint/format/SCA/secret-scan) and benefits most from copying a proven reference.

This sequences the riskiest contract-validation once, then parallelizes the bulk.

## 12. Risks of implementing all three adapters simultaneously

- The V1 contract, though unambiguous on paper, is unproven in code; building three adapters against it at once means any contract ambiguity discovered mid-flight has to be reconciled across three implementations rather than fixed once in a reference.
- Divergent interpretations of the `full`-versus-`ship` boundary or of the `unavailable` outcome could set in independently and then need re-alignment.
- Manydoors requires the most net-new work (first CI, new tools); doing it with no reference to copy raises its cost and its risk of drifting from the intended profile semantics.
- Governance-sensitivity (spec Section 13) means each adapter is itself a reviewed artifact; three simultaneous governance-sensitive changes are harder to review well than a proven reference followed by two parallel copies.

These risks are mitigated, not eliminated, by the fact that the repos are independent; the two-wave plan keeps the parallelism while removing the "unproven contract times three" risk.

## 13. Recommendation on how to proceed

Proceed in two waves, not fully parallel and not fully sequential.
Full parallel is defensible on independence grounds but is imprudent for the first implementation of a new contract.
Full sequential wastes the genuine independence of the three repositories.
Two waves (Fidem as reference, then Hachira and Manydoors in parallel) is the recommended path.

The next implementation prompt should scope Wave 1 only: implement and adopt `./scripts/verify` in Fidem as the reference adapter, wire its `github-minimal` workflow, and confirm the six commands, four profiles, outcome model, exit codes, and read-only `doctor` behave as specified - without touching Hachira or Manydoors and without opening a PR unless explicitly authorized.
