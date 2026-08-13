# Visual editorial policy

Visual utility outranks visual quantity. A candidate visual must perform a
useful editorial job. `Make the page less text-heavy` is normally insufficient.

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
