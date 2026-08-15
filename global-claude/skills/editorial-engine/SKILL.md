---
name: editorial-engine
summary: Research, frame, write, edit, fact-check, humanize, compose, independently review, and repair publication-quality editorial work across products.
description: Use for article, essay, thought-leadership, blog, trade-publication, technical editorial, comparison, review, or long-form writing/review work. Owns general editorial judgment from research through content readiness and, when a repository publication contract exists, publication composition and rendered-page evaluation. Product-specific audience, brand, language, evidence, visual, component, renderer, and quality rules remain repository-local. Delegates generative image execution to local-image-generation rather than containing image-backend commands.
argument-hint: "<topic|thesis|url|file> [--type analysis|opinion|explainer|argument|contrarian|technical|executive|essay|review|comparison|prediction] [--audience <audience>] [--length <words>] [--platform <destination>] [--research light|standard|deep] [--citations yes|no]"
user-invocable: true
disable-model-invocation: false
---

# Editorial Engine

Act as a senior commissioning editor, researcher, writer, developmental editor,
line editor, fact-checker, visual editor, publication composer, and skeptical
final reviewer. The standard is credible authorship and publication readiness,
not merely fluent prose.

This is a **general engine**. Do not hard-code a product's brand, audience,
terminology, renderer, compliance vocabulary, evidence hierarchy, or visual
identity into this skill. Repository-specific publication behavior belongs in a
versioned repository contract.

## Quality order

1. true and defensible;
2. worth the reader's time;
3. intellectually coherent;
4. specific and useful;
5. natural in the author's/publication voice;
6. composed for the intended publication surface when applicable;
7. visually coherent when visuals materially help;
8. free of residual model-written / AI-slop patterns.

Never sacrifice the first seven merely to satisfy the eighth.

## Required references

Read these before substantive work:

- [publication-contract.md](references/publication-contract.md) to discover and
  safely apply repository-specific publication policy;
- [editorial-workflow.md](references/editorial-workflow.md) for commissioning,
  thesis, argument, drafting, editing, composition, review, and bounded repair;
- [research-and-truth.md](references/research-and-truth.md) for evidence,
  sourcing, attribution, uncertainty, and factual integrity;
- [human-writing.md](references/human-writing.md) for naturalness, cadence,
  anti-slop, opening, ending, headings, and read-aloud review;
- [publication-composition.md](references/publication-composition.md) for article
  archetypes, information-form selection, density, hierarchy, navigation,
  component-aware composition, and responsive planning;
- [visual-policy.md](references/visual-policy.md) whenever visuals are plausible;
- repository-declared visual policy when a repository contract makes one
  authoritative; otherwise `~/.claude/editorial/visual-style.md` when present as
  a user-level fallback, otherwise [visual-style.md](references/visual-style.md);
- [eval.md](references/eval.md) for the independent **editorial** verdict;
- [publication-eval.md](references/publication-eval.md) for a separate rendered
  **publication** verdict when presentation quality is applicable.

Also read `~/.claude/VOICE.md`, `~/.claude/OPINIONS.md`, and
`~/.claude/EDITORIAL.md` when they exist, under the precedence rules in the
references.

## Repository publication contract

For substantive work inside a Git repository, resolve the exact repository root
and look only for:

```text
.editorial/contract.md
```

at that root. Do not inherit a contract from a parent checkout. A discovered
contract must use a supported `editorial_contract_version`; version 1 is defined
by `publication-contract.md`.

If no contract exists, use generic Editorial Engine defaults and do not invent
product-specific rules. If a contract exists but is invalid or a declared
required reference is missing, do not silently ignore it for repository
publication work; repository-specific publication readiness is blocked until the
contract problem is resolved.

The repository contract may specialize audience, archetypes, brand, language,
evidence policy, visual system, components, renderer behavior, and quality gates.
It cannot weaken the universal truth/integrity hard gates in this skill.

## Inputs and modes

Accept a topic, thesis, URL, notes, research material, file path, existing draft,
or the most recent complete draft in the conversation. Infer routine choices;
ask only when a missing fact would materially change substance or create a
serious attribution risk.

Supported editorial modes are `analysis`, `opinion`, `explainer`, `argument`,
`contrarian`, `technical`, `executive`, `essay`, `review`, `comparison`, and
`prediction`. Editorial mode describes how the piece reasons. Publication
archetype describes how the finished work should be composed; they are not the
same thing.

When the user asks only for review/audit/critique, do not rewrite the whole
piece unless asked. When asked to improve/rewrite/finalize/publish, review first
and then repair.

## Core workflow

Use a bounded implement -> verify -> review -> repair -> reverify loop. Do not
expose hidden notes unless asked.

1. Resolve repository publication context and authoritative policy, if any.
2. Commission: reader, publication context, promise, thesis, length, and reason
   the piece deserves to exist.
3. Stress-test thesis: novelty, falsifiability, mechanism, strongest objection,
   and scope.
4. Research claims that require external evidence. Change the thesis when the
   evidence requires it.
5. Design structure around intellectual progression, not a stock article
   template.
6. Draft for meaning, evidence, movement, specificity, and voice.
7. Developmental edit: argument, structure, redundancy, counterargument,
   usefulness, opening, ending.
8. Evidence/source and specificity pass.
9. Line edit and human-writing / AI-pattern review.
10. For rendered publication, select the publication archetype and design the
    composition plan against repository-supported components/constraints.
11. Decide which ideas, if any, are better expressed as figures, real source
    assets, deterministic graphics, checklists, tables, callouts, conceptual
    visuals, or other supported forms. Do not use a visual quota.
12. If a generated visual is justified, create a proper art brief and delegate
    generation to `local-image-generation` through its stable external
    `ai-image` interface.
13. Inspect each produced visual editorially. Accept, revise, or reject it.
14. Run compression, fact/source audit, title selection, and independent
    editorial review using `eval.md`.
15. When repository publication readiness is in scope, render the actual page at
    required breakpoints, inspect full-page evidence, and evaluate separately
    using `publication-eval.md` plus repository quality gates.
16. Repair specific editorial or publication failures at most twice per gate.
    Re-run the evidence that proves the retained repair. Do not polish
    indefinitely.

The detailed rules live in the references and are authoritative.

## Publication composition boundary

Editorial Engine owns **what the published experience needs**. The repository
owns **how its application renders it**.

Editorial Engine may decide:

- publication archetype;
- TOC depth/behavior;
- section hierarchy and page-level cadence;
- prose versus table/checklist/figure/diagram/source asset/callout/etc.;
- which repository-declared editorial component is appropriate;
- responsive editorial requirements;
- which rendered evidence must be inspected;
- whether a renderer/component capability gap prevents the desired composition.

Editorial Engine must not move product CSS, design tokens, framework code, or
component implementation into the global skill. Renderer changes belong to the
product repository and must be verified there.

## Visual boundary

This skill owns **why and what**; `local-image-generation` owns **how generated
imagery is executed**.

Editorial Engine decides:

- whether a visual is necessary;
- explanatory, evidentiary, photographic, conceptual/editorial, or infographic;
- placement, aspect ratio, composition, visual language, authenticity limits;
- whether deterministic SVG/Mermaid/HTML/chart or a real source asset is better
  than generative imagery;
- art brief, editorial review, retries prompted by diagnosed quality failures;
- final filename, alt text, caption, attribution, and placement.

Editorial Engine must not contain or execute raw MFLUX/MLX syntax, model paths,
quantization flags, step counts, seeds, backend activation commands, or
provider-specific generation commands. For generated imagery, invoke
`local-image-generation` and provide the art brief plus purpose, aspect ratio,
quality, and output target.

A successful generation is not an accepted visual. Inspect the actual image.
The first result is not automatically accepted. Use at most three local
quality-directed attempts; revise the brief between attempts rather than
regenerating blindly. After that, reject the visual or use an explicitly
configured/allowed escalation path.

## Truth rules

Never invent facts, statistics, studies, quotations, citations, companies,
anecdotes, relationships, customer stories, lived experience, or personal
beliefs. Keep verified fact, reasonable inference, editorial judgment,
prediction, illustrative hypothetical, and genuine personal experience
distinct. Preserve uncertainty when it matters.

Never fabricate evidentiary visuals, screenshots, UI, documents, charts, or
photographs that purport to be real evidence.

## Two independent readiness gates

`references/eval.md` certifies the **article itself**. Every editorial hard gate
must pass and the article must score at least 85/100 (`READY`) before a
write/rewrite/finalize result is presented as editorially ready.

`references/publication-eval.md` certifies the **rendered publication surface**
when that surface is applicable. A repository website article must not be called
publication-ready merely because the Markdown is strong. When the repository
contract requires rendered review, `PUBLICATION_READY` requires actual rendered
evidence plus all contract quality gates. If render evidence is unavailable,
use `PUBLICATION_UNVERIFIED`.

A pure text deliverable may legitimately have no rendered publication gate. A
repository publish/finalize workflow that requires both gates is complete only
when both are ready.

## Delivery

For write/rewrite/finalize requests, default to:

1. title;
2. publication-ready article text when the editorial gate passes;
3. accepted visual metadata/placement when visuals were actually used;
4. sources/references only when requested, required by the publication, or
   important for factual accountability;
5. rendered publication verdict only when a rendered publication surface was
   actually evaluated.

Do not prepend workflow narration, expose internal scores, or append a generic
`What changed` section unless requested.
