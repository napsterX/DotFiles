# Editorial workflow

Use this as the detailed editorial operating procedure. The sequence is bounded;
individual passes may be combined when doing so does not reduce deliberate
review or required evidence.

## Repository publication context

Before substantive repository work, use `publication-contract.md`.

1. Resolve the exact repository root.
2. If `<repository-root>/.editorial/contract.md` exists, validate its
   `editorial_contract_version` and load every contract-declared required
   repository-relative reference.
3. Apply repository specialization beneath the universal truth/integrity rules.
4. If no contract exists, continue with generic defaults and do not invent
   product-specific brand, audience, terminology, evidence, renderer, or visual
   rules.
5. If a contract exists but is invalid or incomplete, preserve work that does
   not depend on it, but block repository-specific publication readiness rather
   than silently falling back.

Do not allow a parent repository, neighboring checkout, or unrelated global file
to act as an implicit product contract.

## Author profiles

Before writing or materially rewriting:

1. Read `~/.claude/VOICE.md` when present. Treat its `Never do this` section as a
   hard constraint unless it conflicts with repository safety/claim boundaries.
   If absent, use a neutral experienced editorial voice and do not invent a
   personal profile.
2. Read `~/.claude/OPINIONS.md` only when the article argues a position or speaks
   on the user's behalf. Never manufacture a preference from it when the brief
   is neutral.
3. Read `~/.claude/EDITORIAL.md` when present. It may specialize general writing
   preferences but cannot override universal integrity rules or a repository's
   authoritative product/safety contract.

## Editorial modes

- `analysis`: evidence-led explanation with a clear conclusion;
- `opinion`: strong but defensible editorial position;
- `explainer`: make complexity understandable without flattening it;
- `argument`: prove or disprove a specific claim;
- `contrarian`: challenge a common view only when evidence supports doing so;
- `technical`: mechanisms, constraints, tradeoffs, and precision over rhetoric;
- `executive`: high information density, implications early, limited digression;
- `essay`: more reflection and voice, still disciplined;
- `review`: evaluate a product, idea, book, paper, approach, or draft;
- `comparison`: explicit criteria, real tradeoffs, decisive synthesis;
- `prediction`: distinguish known facts, assumptions, scenarios, and forecasts.

Platform changes presentation, not intellectual standards. A website article,
newsletter essay, social long-form piece, and trade-publication article should
not share one mechanical template.

Editorial mode is distinct from **publication archetype**. Publication archetype
is selected later using `publication-composition.md` and the repository contract.

## 1. Commission the article

Determine the intended reader, reader knowledge level, publication context,
article type, approximate length, reader problem/question, article promise, and
what the reader should understand, believe, question, or do afterward.

When a repository contract exists, use its declared audience, brand, language,
evidence, and archetype constraints rather than making up equivalents.

When the brief lacks a strong thesis, generate 2-4 candidates internally and
choose the best combination of truth, usefulness, novelty, specificity, and
defensibility. A topic is not a thesis. Reject interchangeable framing such as
"AI is transforming business" or "technology has benefits and challenges."

## 2. Stress-test the thesis

Ask:

- Could this appear in hundreds of interchangeable articles?
- Would a knowledgeable reader consider it obvious?
- What evidence could falsify it?
- What is the strongest informed objection?
- Is the argument describing a mechanism or merely correlation?
- Is the thesis narrow enough to defend?
- Is this one argument or several unrelated observations?
- Can the thesis be stated cleanly in one sentence?

Refine before drafting when necessary.

## 3. Research to test the argument

Use `research-and-truth.md` plus any repository-declared evidence policy.
Research around claims, not keywords. Build an internal evidence map containing
claim, support, contradiction, source/date, source quality, confidence, and
effect on the thesis. If evidence weakens the original thesis, change the thesis
rather than decorating a predetermined conclusion.

Repository evidence policy may raise domain-specific thresholds or source
hierarchies. It cannot authorize fabrication or knowingly weaker claim-to-
evidence fit than the universal standard.

## 4. Find the strongest counterargument

Model the smartest informed critic, not a straw man. Decide whether the
objection invalidates the thesis, narrows it, exposes an assumption, belongs in
the article, or is real but immaterial.

## 5. Design argumentative structure

Build around intellectual progression. Useful section functions include
observation, tension, thesis, mechanism, evidence, example, consequence,
qualification, counterargument, implication, and recommendation.

Do not default to `Introduction -> Benefits -> Challenges -> Best Practices ->
Future -> Conclusion`. Every section must advance understanding. Section lengths
may be uneven. Omit decorative sections.

This is the **argument structure**, not yet the rendered page layout.

## 6. Draft for argument

Write the first complete draft for meaning, evidence, movement, and voice rather
than style-rule compliance. Use concrete nouns and verbs, precise domain jargon,
natural sentence/paragraph variation, transitions only where needed, evidence-
required qualifications, and legitimate first person only when attributable.

Controlled irregularity is fine. Manufactured errors, random fragments, slang,
or awkwardness are not evidence of humanity.

SEO is subordinate to editorial quality unless explicitly requested. Never
keyword-stuff.

## 7. Structural and developmental edit

Ignore micro-style at first. Ask:

- Is there one real argument?
- Is the claim interesting and defensible?
- Does the article fulfill its promise?
- Does each section advance the thesis?
- Is necessary evidence missing?
- Is anything repeated?
- Is a stronger opening buried later?
- Is any section generic coverage rather than analysis?
- Does ordering create intellectual momentum?
- Does the ending follow from the argument?

Repair structure before sentences.

## 8. Argument/logic and "so what?" edit

Every important paragraph must advance the argument, provide evidence, explain
mechanism, introduce tension, qualify a claim, answer an objection, provide a
useful example, change understanding, or establish a consequence/decision.
Delete or rewrite paragraphs that merely describe the topic.

## 9. Evidence and specificity edit

Use `research-and-truth.md` and repository evidence policy. Replace unsupported
abstractions with concrete mechanisms, names, dates, numbers, or examples only
when the evidence supports them. Protect useful specifics. Do not invent detail
to make prose feel vivid.

## 10. Line and naturalness edit

Use `human-writing.md`. Fix diction, sentence control, rhythm, repetitive
structures, AI-pattern clusters, openings, endings, headings, formatting, and
read-aloud problems without turning the article into choppy or artificially
quirky prose. Apply repository language policy when declared.

## 11. Publication archetype and composition plan

For a rendered publication surface, use `publication-composition.md` after the
article's argument is structurally sound.

Select the repository-supported publication archetype, then create an internal
composition plan covering:

- hero treatment;
- TOC/navigation depth and behavior;
- major hierarchy and section rhythm;
- prose versus other information forms;
- component/module choices from the repository contract;
- visual jobs;
- supporting modules only when justified;
- responsive composition requirements;
- render evidence and quality gates required for final publication readiness.

Do not force the same composition on unrelated article archetypes. Do not invent
components the repository cannot render.

## 12. Visual and information-form review

Use `visual-policy.md`, `publication-composition.md`, and the authoritative
repository visual system when present. Determine whether any idea is better
communicated as a deterministic figure, real source asset, table, checklist,
comparison, chart, photograph, conceptual illustration, or another supported
form.

No visual is required merely because the page is text-heavy. At the same time,
long-form web composition must explicitly inspect cognitive transitions,
information density, and page-level cadence. A different form should be used
only when it improves comprehension, orientation, recall, pacing, emphasis, or
trust.

For generated imagery, produce an art brief using `image-brief-template.md` and
delegate to `local-image-generation`. The `ai-image` executable/configuration is
an externally managed runtime prerequisite; Editorial Engine does not own or
modify it. Inspect the returned asset itself before acceptance. Visual generation
success is not editorial acceptance.

## 13. Compress once

Remove material that does not change meaning, evidence, voice, rhythm, or
necessary context. Preserve useful caveats, texture, evidence, and legitimate
digressions. Do not optimize for minimum word count.

## 14. Fact/source audit

Use `research-and-truth.md` plus repository evidence policy. Confirm externally
verifiable claims, dates, numbers, names, titles, units, quotations, causal
language, prediction framing, and accidental source-language copying.

## 15. Title selection

Generate several candidates internally. Choose the title that best balances
accuracy, specificity, genuine curiosity, publication fit, and fidelity to the
actual article. Avoid clickbait and stock forms such as `The Ultimate Guide`,
`Everything You Need to Know`, or `Why X Is a Game Changer` unless the
publication explicitly requires that style.

## 16. Independent editorial review

Use `eval.md` from a skeptical fresh-reader perspective. When a fresh sub-agent
or independent review lane is available, use it and do not provide the writer's
hidden reasoning. Empty reviewer praise is not evidence.

Editorial threshold is 85/100 with every editorial hard gate passing.

## 17. Rendered publication review

When the repository contract or user request makes a rendered publication
surface part of acceptance:

1. run the repository-declared renderer/preview path;
2. capture or inspect the actual full page at every required breakpoint;
3. inspect complex figures/components closely when a full-page view is
   insufficient;
4. run repository-declared quality gates;
5. evaluate independently with `publication-eval.md`.

Source markup, Markdown, or CSS inspection alone cannot produce
`PUBLICATION_READY` when rendered evidence is required. If the surface cannot be
rendered/inspected, use `PUBLICATION_UNVERIFIED`.

## 18. Bounded repair and reverification

Keep editorial and publication repair loops separate so a design repair does not
silently damage the article and a prose repair does not invalidate prior render
evidence.

- Maximum two editorial repair cycles by default.
- Maximum two publication repair cycles by default.
- After every retained repair, rerun the evidence relevant to that gate.
- After a renderer/composition change, re-render; never reuse a pre-repair
  screenshot as acceptance evidence.
- If a material issue remains after the bound, return the strongest defensible
  state and disclose the residual concern rather than claiming readiness.

## Review-only mode

When the user authorizes review but not rewrite:

1. resolve repository publication context when applicable;
2. identify thesis and intended reader;
3. thesis/originality audit;
4. structure/logic audit;
5. evidence/factual audit;
6. voice/human-writing audit;
7. visual/composition review when relevant;
8. line-edit audit;
9. score using `eval.md`;
10. if an actual rendered page is supplied or available and presentation is in
    scope, evaluate separately with `publication-eval.md`;
11. return prioritized findings and the smallest material improvement set.

Do not rewrite the entire article unless asked.
