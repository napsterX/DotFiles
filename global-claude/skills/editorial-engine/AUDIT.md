# Editorial Engine architecture audit

## Preserved

- senior-editor posture rather than generic content generation;
- truth/fabrication prohibitions;
- VOICE/OPINIONS/EDITORIAL profile handling;
- topic/thesis/URL/notes/file/draft inputs;
- editorial mode taxonomy;
- thesis stress-testing and counterargument;
- claim-led research and source hierarchy;
- argument-driven structure;
- drafting for meaning before style policing;
- developmental, specificity, line, cadence, opening, ending, heading,
  read-aloud, compression, fact/source, title, and independent-review passes;
- 85/100 editorial READY threshold, hard gates, and bounded repair;
- review-only versus rewrite behavior;
- anti-AI-slop philosophy without detector gaming or fake mistakes;
- visual-need analysis and strict generation delegation to
  `local-image-generation`.

## Added in rv1.14.0

- a versioned repository publication-contract protocol rooted at the exact
  repository's `.editorial/contract.md`;
- explicit isolation: no parent/neighbor contract inheritance and no silent
  fallback when an existing repository contract is invalid;
- standard repository specialization surfaces for brand, audience, archetypes,
  visual system, components, evidence, language, and quality gates;
- precedence rules that allow repository specialization without weakening
  universal truth/integrity hard gates;
- publication archetype as a separate concept from editorial mode;
- publication composition covering TOC/navigation restraint, hierarchy, density,
  page-level cadence, callout restraint, information-form selection, component
  capability, and responsive behavior;
- rendered-page review from actual evidence rather than source markup alone;
- a second independent publication gate with `PUBLICATION_READY`,
  `PUBLICATION_REVISE`, `PUBLICATION_REBUILD`, and `PUBLICATION_UNVERIFIED`;
- tests preventing product-specific rules from leaking into the generic engine;
- a package boundary that treats the `ai-image` executable/configuration as
  externally managed and forbids package ownership of those files.

## Architectural boundaries

The global Editorial Engine owns general editorial reasoning and publication
composition. Product repositories own audience, brand, terminology, domain
evidence rules, visual identity, components, renderer implementation, and
repository-specific acceptance gates.

`local-image-generation` remains the technical generated-image boundary and may
invoke the separately managed `ai-image` runtime. Neither Editorial Engine nor
this package owns the `ai-image` binary/configuration.

## Removed or avoided

- no product-specific publication policy was embedded in the global skill;
- no product renderer/CSS/framework implementation was moved into the skill;
- no arbitrary image-per-word quota was introduced;
- no raw MFLUX/MLX commands or model-specific generation policy was added;
- no duplicate full `article` skill is retained; `article` remains only a
  compatibility shim to the source of truth.
