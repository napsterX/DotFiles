# Editorial workflow

Use this as the detailed editorial operating procedure. The sequence is bounded;
individual passes may be combined when doing so does not reduce deliberate
review.

## Author profiles

Before writing or materially rewriting:

1. Read `~/.claude/VOICE.md` when present. Treat its `Never do this` section as a
   hard constraint. If absent, use a neutral experienced editorial voice and do
   not invent a personal profile.
2. Read `~/.claude/OPINIONS.md` only when the article argues a position or speaks
   on the user's behalf. Never manufacture a preference from it when the brief
   is neutral.
3. Read `~/.claude/EDITORIAL.md` when present. It may specialize this standard
   but cannot authorize fabrication.

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
Substack essay, LinkedIn article, and trade-publication piece should not share one
mechanical template.

## 1. Commission the article

Determine the intended reader, reader knowledge level, publication context,
article type, approximate length, reader problem/question, article promise, and
what the reader should understand, believe, question, or do afterward.

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

Use `research-and-truth.md`. Research around claims, not keywords. Build an
internal evidence map containing claim, support, contradiction, source/date,
source quality, confidence, and effect on the thesis. If evidence weakens the
original thesis, change the thesis rather than decorating a predetermined
conclusion.

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

Use `research-and-truth.md`. Replace unsupported abstractions with concrete
mechanisms, names, dates, numbers, or examples only when the evidence supports
them. Protect useful specifics. Do not invent detail to make prose feel vivid.

## 10. Line and naturalness edit

Use `human-writing.md`. Fix diction, sentence control, rhythm, repetitive
structures, AI-pattern clusters, openings, endings, headings, formatting, and
read-aloud problems without turning the article into choppy or artificially
quirky prose.

## 11. Visual-need review

Use `visual-policy.md` and `visual-style.md`. Determine whether any visual adds
information, evidence, comprehension, or a useful conceptual frame. No visual is
required merely because the page is text-heavy.

For generated imagery, produce an art brief using `image-brief-template.md` and
delegate to `local-image-generation`. Inspect the returned asset itself before
acceptance. Visual generation success is not editorial acceptance.

## 12. Compress once

Remove material that does not change meaning, evidence, voice, rhythm, or
necessary context. Preserve useful caveats, texture, evidence, and legitimate
digressions. Do not optimize for minimum word count.

## 13. Fact/source audit

Use `research-and-truth.md`. Confirm externally verifiable claims, dates,
numbers, names, titles, units, quotations, causal language, prediction framing,
and accidental source-language copying.

## 14. Title selection

Generate several candidates internally. Choose the title that best balances
accuracy, specificity, genuine curiosity, publication fit, and fidelity to the
actual article. Avoid clickbait and stock forms such as `The Ultimate Guide`,
`Everything You Need to Know`, or `Why X Is a Game Changer` unless the
publication requires that style.

## 15. Independent final review

Use `eval.md` from a skeptical fresh-reader perspective. When a fresh sub-agent
or independent review lane is available, use it and do not provide the writer's
hidden reasoning. Empty reviewer praise is not evidence.

## 16. Bounded repair

Publication threshold is 85/100 with every hard gate passing. Repair specific
failures and re-review. Maximum two repair cycles. If a material issue remains,
return the strongest defensible version and disclose the residual concern rather
than claiming publication readiness.

## Review-only mode

When the user authorizes review but not rewrite:

1. identify thesis and intended reader;
2. thesis/originality audit;
3. structure/logic audit;
4. evidence/factual audit;
5. voice/human-writing audit;
6. visual review when relevant;
7. line-edit audit;
8. score using `eval.md`;
9. return prioritized findings and the smallest material improvement set.

Do not rewrite the entire article unless asked.
