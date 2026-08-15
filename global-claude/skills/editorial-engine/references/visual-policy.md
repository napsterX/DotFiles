# Visual editorial policy

Visual utility outranks visual quantity. A candidate visual must perform a
useful editorial job. `Make the page less text-heavy` is normally insufficient.

For long-form rendered publication, also inspect **cognitive transitions,
information density, and page-level cadence**. This is not a visual quota: never
require an image every N words. Instead ask whether a diagram, comparison, real
source asset, checklist, table, chart, quote, photograph, or conceptual visual
communicates a specific idea better than another paragraph. Use
`publication-composition.md` for page-level composition rules.

## Classification

### Explanatory

Architecture, workflow, process, comparison, timeline, relationship, or other
precise explanatory graphics. Prefer deterministic SVG, Mermaid, HTML/CSS,
programmatic diagrams, or charts when precision matters.

### Evidentiary

Screenshots, actual UI, documents, historical material, real-data charts, or
product interfaces. Never fabricate evidence. Use the real asset/source.

### Photographic

People, places, physical products, events, buildings, or historical locations.
When authenticity matters, prefer legitimate real photography over a generated
fake equivalent.

### Editorial / conceptual illustration

Abstract concepts that cannot literally be photographed, such as identity as a
security perimeter, autonomous agents operating infrastructure, digital trust,
or future workplace systems. This is the primary generative-image category.

### Infographic

Use generative imagery cautiously. Prefer deterministic rendering for accurate
information and especially for text-heavy graphics.

## Art brief

When generative imagery is justified, use `image-brief-template.md`. Specify the
editorial purpose and idea, placement, composition, visual language, required
subjects/relationships, explicit avoid list, text policy, aspect ratio, and
authenticity constraints.

Never send a generic request such as `Make an image about cloud security`.

## Delegation contract

Generated-image work is delegated to `local-image-generation`. Pass:

- art brief path/content;
- purpose/role;
- aspect ratio;
- quality expectation;
- output target;
- whether explicitly configured cloud escalation is allowed.

Do not include raw backend syntax or model names unless the user explicitly
provided a technical runtime override and the local-image-generation contract
requires it.

## Editorial image review

Inspect the actual image. Evaluate:

- editorial relevance;
- information value;
- prompt/brief adherence;
- composition and visual hierarchy;
- visual quality;
- authenticity/factual appropriateness;
- brand/style consistency;
- obvious AI artifacts;
- anatomy and object duplication;
- impossible geometry;
- gibberish or inaccurate text;
- incorrect UI or fabricated evidence;
- misleading symbolism;
- mobile/crop suitability;
- whether it materially improves the article.

Suggested forcing rubric:

- Editorial relevance /10
- Information value /10
- Prompt adherence /10
- Composition /10
- Visual quality /10
- Authenticity /10
- Brand consistency /10
- AI artifacts PASS/FAIL
- Text accuracy PASS/FAIL/N/A
- Factual appropriateness PASS/FAIL

Qualitative judgment can override arithmetic; the rubric exists to prevent
automatic acceptance.

## Retry behavior

When inadequate:

1. diagnose the failure;
2. revise the brief/prompt;
3. regenerate;
4. reinspect.

Maximum three local quality-directed attempts by default. Do not repeatedly
submit the same prompt. After the bound, reject the visual or use another
backend only when that backend is configured and escalation was explicitly
allowed.

## Accepted asset metadata

For accepted assets produce, as applicable:

- descriptive filename;
- alt text describing useful content, not keywords;
- caption only when it adds information;
- source/attribution metadata;
- placement;
- asset path/article reference.


## Repository visual-system precedence

When a valid repository publication contract declares a repository visual system
as authoritative, apply that product-specific palette, illustration grammar,
photography policy, diagram language, crop behavior, component semantics, and
banned motifs beneath the universal authenticity/truth rules.

Do not copy those product-specific rules into this global policy. The packaged
and user-level visual-style files are fallback art direction only when the
repository does not declare its own authoritative visual system.

## Page-level visual audit

When reviewing a rendered article, do not evaluate assets in isolation. Also ask:

- Does the page have useful density variation or is every viewport equally busy?
- Are visuals placed at genuine conceptual transitions?
- Are repeated callouts/boxes doing work, or merely adding chrome?
- Does a visual form improve comprehension enough to justify its footprint?
- Are deterministic figures used instead of generated imagery where labels,
  values, or precise relationships matter?
- Does the visual system remain coherent across hero, inline figures, related
  content, and responsive crops?

A technically strong image can still be rejected when it damages the page's
composition or feels generic relative to the repository publication identity.
