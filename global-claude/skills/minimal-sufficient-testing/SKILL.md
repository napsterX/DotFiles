---
name: minimal-sufficient-testing
description: Decide what testing a code change actually needs - the smallest test plan that gives strong confidence the change is correct, safe, and maintainable, proportional to risk. Use when the user asks what tests to write or run for a change, asks for a test plan, or when another skill (e.g. audit-and-pr) needs to decide test coverage for changed behavior.
user-invocable: true
---

# Minimal Sufficient Testing

You decide what testing is necessary for a code change.

Your goal is to create the smallest test plan that gives strong confidence the
change is correct, safe, and maintainable.

Do not blindly recommend every possible test type. Do not skip tests just to
move fast. Use engineering judgment.

## Core Principle

Testing should be proportional to risk.

A change that only affects isolated logic does not need a full end-to-end
suite.

A change that affects persistence, permissions, external integrations, async
workflows, critical user journeys, or production safety requires stronger
tests.

Think before deciding.

## What To Analyze

Before recommending tests, inspect the change and determine:

1. What behavior is being added, changed, or removed.
2. Which files, modules, APIs, components, database objects, workflows, or
   contracts are affected.
3. Whether the change touches user-visible behavior.
4. Whether the change touches data persistence.
5. Whether the change touches security, authorization, roles, ownership,
   tenancy, or privacy.
6. Whether the change touches external services, queues, jobs, workers,
   webhooks, emails, payments, file handling, or generated content.
7. Whether the change affects a critical product journey.
8. Whether the change fixes a bug that should never return.
9. What existing tests already cover nearby behavior.
10. What risks would remain if no test were added.

## Decision Standard

Recommend tests only when they protect meaningful behavior or reduce
meaningful risk.

Prefer targeted tests over broad suites.

Prefer existing test patterns over inventing new infrastructure.

Prefer realistic integration tests when the risk is at a boundary.

Prefer unit tests when the risk is isolated logic.

Prefer end-to-end tests only for critical workflows, not every feature.

Prefer regression tests when fixing bugs.

Prefer manual verification only when automation would be expensive or
low-value, but make the manual check specific.

## Allowed Test Categories

You may recommend any of the following when justified:

- Static checks
- Type checking
- Linting
- Build verification
- Unit tests
- Component tests
- Integration tests
- Contract tests
- Security or authorization tests
- Migration or schema tests
- Worker, queue, retry, or async tests
- File handling tests
- External integration tests with mocked provider boundaries
- End-to-end tests
- Smoke tests
- Regression tests
- Manual verification

You are not required to use every category.

## Required Output

For every implementation task, produce a concise testing decision using this
format:

### Testing Decision

**Risk Level:** Low / Medium / High
**Reason:** Explain the risk in plain engineering terms.

### Tests Required

List only the tests that should be added, updated, or run.

For each test, include:

- Test type:
- What it protects:
- Why it is necessary:
- Suggested location:
- Positive case:
- Negative or failure case, if relevant:

### Tests Not Required

List test categories that are intentionally skipped and why.

### Commands To Run

Use the project's existing scripts when available. Do not invent commands
unless necessary.

### Manual Verification

Describe the minimum manual check needed, if any.

### Stop Conditions

Stop and report instead of pretending the task is complete if:

- The change affects behavior but no testable behavior can be identified.
- The change affects persistence but no integration test or equivalent
  verification exists.
- The change affects authorization/security but no negative access test
  exists.
- The change fixes a bug but no regression test is added or justified.
- Existing related tests fail.
- Build/typecheck/lint fails.
- The recommended tests require infrastructure that does not exist and cannot
  reasonably be added in this task.

## Operating Rules

Use judgment.

Do not create test bloat.

Do not give fake confidence.

Do not rely only on unit tests when the risk is integration.

Do not rely only on manual testing when the risk is repeatable and important.

Do not add end-to-end tests unless the workflow is critical enough to justify
the cost.

Do not test implementation details when observable behavior is the real
contract.

Do not make brittle tests for unstable output, generated text, timestamps,
random IDs, or external provider responses unless those are normalized.

Do not update snapshots blindly.

When unsure, choose the narrowest test that protects the highest-risk
behavior.
