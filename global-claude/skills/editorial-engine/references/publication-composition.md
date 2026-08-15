# Publication composition

Publication composition converts a strong article into a strong **published
reading experience**. It is a separate concern from argument structure and from
the repository renderer itself.

The Editorial Engine owns the composition decision. The repository owns the
brand system, supported components, and implementation of the rendered page.

## Editorial mode is not publication archetype

Editorial mode answers how the piece reasons: analysis, opinion, explainer,
technical, comparison, and so on.

Publication archetype answers how the finished work should be experienced on the
surface. Do not conflate them.

When a repository contract defines supported archetypes, use those definitions.
Without a repository contract, useful generic fallback archetypes include:

- `editorial`: narrative or thought-leadership reading experience with restrained
  navigation and strong pacing;
- `practical-guide`: operational guidance with selective navigation, checklists,
  examples, and warnings where useful;
- `deep-reference`: dense, source-heavy material where persistent navigation,
  tables, appendices, and detailed subsections may be justified;
- `research-analysis`: evidence-forward article with figures, methodology,
  citations, and explicit uncertainty;
- `comparison`: criteria-led evaluation using tables/figures only when they make
  trade-offs clearer;
- `product-education`: explains a product/workflow accurately without collapsing
  into promotional copy.

A repository may narrow, extend, or rename its archetypes through
`.editorial/archetypes.md` as declared by the contract.

## Composition plan

For website publication, create an internal composition plan after the argument
is structurally sound and before final asset execution. The plan should cover:

- selected publication archetype and why it fits;
- hero treatment, if any;
- TOC/navigation behavior and depth;
- major section boundaries and hierarchy;
- where prose is the best information form;
- where another form communicates better than prose;
- visual jobs and asset provenance/type;
- repository components/modules to use;
- supporting material such as FAQ, sources, downloads, video, related reading,
  or CTA only when justified by the article/publication contract;
- responsive considerations that materially affect composition;
- render/review evidence expected before publication readiness.

Do not expose the internal plan unless requested or required by the repository
workflow.

## Information-form selection

Do not ask only `does this article need an image?` Ask what form best communicates
each important idea.

Possible forms include:

- prose;
- short list;
- table;
- deterministic process/workflow figure;
- comparison figure;
- decision tree;
- timeline;
- chart from real data;
- real screenshot/source asset;
- pull quote;
- checklist;
- evidence note;
- caution/warning;
- conceptual illustration;
- photograph;
- interactive or video when the repository supports it and the medium materially
  improves understanding.

Prefer deterministic rendering for precise information and real assets for
evidence. Use generative imagery only where it performs a legitimate conceptual
or aesthetic editorial job.

## Visual cadence without visual quotas

Never require an image every N words or add decoration merely to break up text.
That creates formulaic SEO-blog behavior.

For long-form web publication, explicitly inspect **cognitive transitions,
information density, and page-level cadence**. Look for places where a different
information form improves comprehension, orientation, recall, pacing, or
emphasis. A long section may correctly remain prose; another may need a process
figure after 250 words because the relationship is hard to understand verbally.

The target is controlled variation, not arbitrary variety:

```text
quiet -> information -> emphasis -> quiet -> visual/figure -> information
```

Avoid a monotonous sequence of equally weighted headings, paragraphs, lists, and
boxed callouts.

## Hierarchy and section rhythm

A rendered article should provide obvious landmarks. Major sections need
stronger hierarchy and more separation than minor subsections. Do not create a
heading merely because a paragraph group can be labeled.

Inspect for:

- too many similarly weighted headings;
- repeated `heading -> paragraph -> bullets` architecture;
- uniform section lengths that feel templated;
- H3/H4 proliferation that belongs in reference documentation rather than an
  editorial surface;
- headings that describe categories instead of advancing reader understanding;
- insufficient quiet space before a major conceptual transition.

## TOC and navigation restraint

Navigation is editorial chrome and must earn its visual cost.

- A short editorial article may need no TOC.
- A practical guide may benefit from a compact H2-only TOC.
- A deep reference may justify nested or persistent navigation.
- Do not expose every subsection merely because headings exist.
- Persistent side rails must not compete visually with the article.
- When the repository supports current-section highlighting or progressive
  disclosure, prefer it over permanently showing a very long nested list.

Repository archetype/renderer rules are authoritative when declared.

## Callout restraint

A callout is not a default container for any important sentence. Use a special
component only when changing presentation helps the reader interpret, remember,
or safely act on the material.

Avoid pages where repeated note/warning/info boxes become the dominant visual
language. Distinguish semantic types and keep strong warning treatments rare.

## Component-aware composition

When `.editorial/components.md` is authoritative, compose only with capabilities
the repository actually supports. Use the repository's component names and
semantics rather than inventing presentation that cannot be rendered.

If the article would materially benefit from a missing component, identify that
as a renderer capability gap. Do not silently substitute a misleading generic
box or generated image.

## Brand and visual system

Use `.editorial/visual-system.md` when the repository contract declares it.
Brand-specific palette, illustration grammar, photography rules, diagram
language, component styling, and banned motifs belong there, not in the global
skill.

The packaged `visual-style.md` and optional user-level visual style are fallback
rules only when repository-specific visual direction is absent.

## Responsive composition

Desktop quality is not enough. When the repository's quality gates require
responsive publication review, inspect at least the declared desktop and mobile
surfaces.

Check whether:

- prose measure remains readable;
- heading hierarchy survives;
- figures remain legible and correctly cropped;
- side navigation collapses or reflows appropriately;
- callouts do not dominate small screens;
- tables have an intentional mobile treatment;
- hero and supporting assets preserve their editorial meaning;
- interactive controls remain usable.

Do not claim responsive publication readiness from source code alone when the
contract requires rendered evidence.

## Renderer boundary

Editorial Engine may choose composition and evaluate the result, but it does not
own product CSS, application components, framework code, or design tokens.
Those remain repository implementation concerns.

If renderer changes are required, express the needed editorial behavior against
the repository contract/component system and let the repository implementation
workflow make and verify those changes.
