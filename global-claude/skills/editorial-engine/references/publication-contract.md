# Repository publication contract

The Editorial Engine is global and product-agnostic. A repository may specialize
publication behavior through a versioned repository-local contract without
forking the engine or weakening its universal editorial integrity rules.

## Canonical location

The canonical entry point is:

```text
<repository-root>/.editorial/contract.md
```

`.editorial` is intentionally a dot-directory because these files are
**repository control-plane metadata**, not article content. The directory plays
the same role as `.github`, `.claude`, or other tool configuration: it keeps the
repository root clean, makes machine discovery unambiguous, and avoids collisions
with a future `editorial/` content directory. Git and normal IDEs still track and
show the directory. Do not search for or inherit a contract from a parent
repository or neighboring checkout.

A repository may use another location only when the user explicitly supplies it
for the current invocation. Automatic discovery uses `.editorial/contract.md`
only so behavior remains deterministic across products.

## Repository-root discovery

When substantive work is being done in a Git repository, resolve the exact Git
repository root before loading publication policy. Read only the contract at
that root. Worktrees count as their registered repository/worktree root for
content resolution; never allow an unrelated parent directory to inject an
editorial contract.

When there is no repository contract, continue with the generic Editorial Engine
and clearly avoid inventing product-specific brand, language, evidence, or
renderer rules.

If `.editorial/contract.md` exists but is malformed, references a missing
required file, or declares an unsupported contract version, do **not** silently
fall back to generic behavior for a repository publication task. Report the
contract problem and treat repository-specific publication readiness as blocked.

## Contract version

Version 1 contracts start with YAML front matter containing at least:

```yaml
---
editorial_contract_version: 1
product: <stable product/repository name>
publication: <publication or content-system name>
---
```

The contract may then declare repository-relative authoritative references,
supported publication archetypes, renderer/preview information, and required
quality gates. All paths supplied by the contract must remain inside the same
repository unless the general engine explicitly defines a user-level fallback.

## Standard specialization files

Version 1 recommends these repository-local files:

```text
.editorial/
├── contract.md
├── brand.md
├── audience.md
├── archetypes.md
├── visual-system.md
├── components.md
├── evidence-policy.md
├── language.md
└── quality-gates.md
```

Only `contract.md` is universally required. The contract declares which sibling
files are mandatory for that product. A small repository may inline some rules
in `contract.md`; a mature publication should split durable concerns into the
standard files above.

The standard responsibilities are:

- `brand.md`: publication personality, positioning, tone boundaries, and brand
  behavior;
- `audience.md`: primary/secondary readers, knowledge level, reader jobs, and
  important sensitivities;
- `archetypes.md`: repository-supported publication archetypes and their
  presentation expectations;
- `visual-system.md`: palette, illustration/photography/diagram language,
  visual prohibitions, crop and responsive rules;
- `components.md`: actual renderer components/modules available to article
  composition and their correct/incorrect uses;
- `evidence-policy.md`: domain-specific source hierarchy, claim classes,
  evidence thresholds, citation/attribution requirements, and uncertainty rules;
- `language.md`: product terminology, prohibited or legally/product-sensitive
  phrasing, capitalization, naming, and vocabulary;
- `quality-gates.md`: repository-specific render, accessibility, terminology,
  factual, testing, and publication acceptance commands or checks.

## Precedence and inheritance

Apply policy in this order:

1. universal truth, anti-fabrication, source-integrity, and Editorial Engine hard
   gates;
2. repository `.editorial/contract.md` and the authoritative files it names;
3. user-level author/voice preferences where compatible with 1 and 2;
4. packaged generic defaults.

A repository contract **specializes** the engine; it cannot weaken universal
integrity rules. For example, it cannot authorize fabricated evidence, knowingly
unsupported claims, fake screenshots, or omission of a material contradiction.
A user-level preference likewise cannot override repository safety/claim
boundaries.

Repository-specific visual policy takes precedence over the generic/user-level
visual fallback when the repository contract declares it authoritative.

## Contract isolation

Do not copy product-specific rules back into the global skill merely because one
repository needs them. If a rule is useful only for one product, audience,
brand, renderer, compliance domain, or vocabulary system, it belongs in that
repository contract.

Promote a rule into the global engine only when it is genuinely publication-
general and should remain true across unrelated products.

## Minimum contract behavior

Before claiming repository publication readiness, the engine must know:

- who the intended publication/audience is;
- which publication archetypes are supported;
- which repository rules are authoritative;
- what renderer/components are available when composition depends on them;
- what evidence/language restrictions apply when declared;
- which repository-specific quality gates must pass;
- whether rendered-page review is required and how it can be performed.

If any contract-declared required input is unavailable, preserve the content work
that can still be done, but do not claim repository publication readiness.
