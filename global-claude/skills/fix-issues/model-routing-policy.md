# Model Routing Policy

## Purpose

Choose the implementation model after the orchestrator has fetched one eligible
issue and inspected enough repository context to understand risk, ambiguity, and
change surface. Re-evaluate routing before every retry. The router chooses;
deterministic helpers validate the decision but do not make it.

## Required routing record

Record:

- issue number;
- attempt number;
- implementation expected: yes or no;
- selected model;
- previous model when retrying;
- risk: low, medium, high, or critical;
- complexity: localized, multi-file, cross-module, or cross-system;
- sensitive domains involved;
- ambiguity level;
- alternatives considered;
- concise rationale;
- dispatch evidence status.

The selected model must be explicit. `inherit` is invalid.

## Selection rubric

### Sonnet

Use by default when the work is scoped, acceptance criteria are clear, the
likely change is localized, repository patterns are established, and no
high-impact boundary is involved.

### Opus

Use when correctness depends on deeper reasoning or the change can damage a
material boundary, including authorization, tenancy, security, migrations, data
integrity, concurrency, retries, payments, compatibility, or cross-module state.

### Fable

Use selectively when deep architecture validation or cross-system reasoning has
a clear advantage and choosing the correct design is the central difficulty.
Do not choose Fable merely because the issue is large.

### Haiku

Do not use Haiku for source-code implementation. The orchestrator may use cheap
read-only mechanisms for queue metadata, but implementation workers must use
Sonnet, Opus, or Fable.

## Proportionality

Do not choose a model solely from P3/P2 priority, line count, or cost. Choose the
least expensive model that is still adequate for the actual risk and reasoning
burden. Never downgrade merely to save tokens when doing so materially increases
implementation risk.

## Retry routing

A retry must not be a blind repeat.

- Keep the same model when the first failure is mechanical, the root cause is
  still clear, and the new plan materially changes the implementation or proof.
- Escalate Sonnet to Opus when the failure reveals ambiguity, cross-module
  coupling, concurrency, security, data, or contract risk.
- Use Fable only when architecture selection or cross-system reconciliation is
  now the main blocker.
- Do not downgrade after a failed attempt unless the previous model was
  unavailable before source edits and a new explicit decision proves a lower
  model remains adequate.

Record the exact first causal failure and what will be different in the next
attempt.

## Dispatch

Invoke `issue-fix-worker` with the Agent tool and an explicit per-invocation
`model` parameter matching the routing decision.

The worker frontmatter default does not replace this requirement.

Before dispatch, check only the relevant routing override signal rather than
printing the full environment. A non-empty `CLAUDE_CODE_SUBAGENT_MODEL` value
other than `inherit` can override the per-invocation choice; treat that as
`MODEL ROUTING BLOCKED` unless the resulting model is explicitly known to match
the selected model.

If platform or organization restrictions prevent the selected model:

1. stop before source edits from that dispatch;
2. make a new explicit routing decision using the best available adequate model;
3. record the unavailable model and replacement rationale;
4. never allow an implicit inherited fallback.

If no adequate available model remains, classify the issue `blocked`.

## Runtime evidence

Capture when available:

- requested model alias;
- subagent name;
- dispatch identifier;
- reported or observed resolved model;
- whether the platform exposed deterministic runtime confirmation.

If the platform exposes a different resolved model, reject the worker result.
If the platform does not expose deterministic model identity, report
`REQUESTED_NOT_RUNTIME_VERIFIED`; do not falsely claim proof.
