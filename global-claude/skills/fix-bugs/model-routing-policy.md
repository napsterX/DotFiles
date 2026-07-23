# Model Routing Policy

## Purpose

Choose the implementation model after the orchestrator has fetched one eligible
issue and inspected enough repository context to understand risk, ambiguity, and
change surface. The router chooses; deterministic helpers validate the decision
but do not make it.

## Required routing record

Record:

- issue number;
- implementation expected: yes or no;
- selected model;
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

Use by default when the defect is scoped, acceptance criteria are clear, the
likely change is localized, repository patterns are established, and no
high-impact boundary is involved.

Typical signals:

- one component or a small number of related files;
- deterministic reproduction;
- ordinary application logic;
- established test pattern;
- low architectural ambiguity.

### Opus

Use when correctness depends on deeper reasoning or the change can damage a
material boundary.

Typical signals:

- authorization or authentication;
- tenant isolation;
- security-sensitive code;
- migrations or irreversible data changes;
- concurrency, retries, idempotency, or distributed state;
- payment or financial behavior;
- cross-module behavior;
- unclear root cause with several plausible explanations;
- compatibility or public-contract risk.

### Fable

Use selectively when deep architecture validation or cross-system reasoning has
a clear advantage over routine implementation models.

Typical signals:

- high-impact ambiguous architecture decision embedded in the defect;
- several systems or contracts must be reconciled;
- adversarial design reasoning is central to choosing the safe fix;
- a routine scoped implementation model would materially increase the chance of
  selecting the wrong design.

Do not choose Fable merely because the issue is large or interesting.

### Haiku

Do not use Haiku for source-code implementation. The orchestrator may use cheap
read-only mechanisms for queue metadata, but a selected implementation worker
must use Sonnet, Opus, or Fable.

## Proportionality

Do not choose a model solely from P2/P3 priority, line count, or cost. Choose the
least expensive model that is still adequate for the actual risk and reasoning
burden. Never downgrade when doing so materially increases implementation risk.

## Dispatch

Invoke `bug-fix-worker` with the Agent tool and an explicit per-invocation
`model` parameter matching the routing decision.

The worker frontmatter default does not replace this requirement.

Before dispatch, check only the relevant routing override signal rather than
printing the full environment. A non-empty `CLAUDE_CODE_SUBAGENT_MODEL` value
other than `inherit` can override the per-invocation choice; treat that as
`MODEL ROUTING BLOCKED` unless the resulting model is explicitly known to match
the selected model.

If platform or organization model restrictions prevent the selected model:

1. stop before source edits from that dispatch;
2. make a new explicit routing decision using the best available adequate model;
3. record the unavailable model and the replacement rationale;
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
