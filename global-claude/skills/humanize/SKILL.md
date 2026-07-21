---
name: humanize
description: Rewrite supplied prose so it sounds like Manish wrote it, preserving meaning while removing AI cadence, inflated language, generic transitions, excessive structure, and polished-but-unnatural phrasing. Use when Manish explicitly asks to humanize, de-AI, make text sound like him, or make it less ChatGPT-ish.
argument-hint: "[text-or-file-path]"
user-invocable: true
disable-model-invocation: true
---

# Humanize

Rewrite the supplied text so a real reader would assume Manish wrote it, not a
language model.

The goal is not casual grammar damage, slang injection, fake typos, or random
sentence fragments. The goal is credible human authorship: direct intent,
natural emphasis, uneven but controlled rhythm, specific reasoning, and no AI
performance.

## Required reading

1. Read `~/.claude/VOICE.md`. It is the canonical voice profile and its
   `Never do this` section is a hard constraint. If it is missing, stop and
   state that the voice source is unavailable instead of inventing one.
2. Read `~/.claude/OPINIONS.md` only when the text argues a position, makes a
   recommendation, or speaks on Manish's behalf about a decision.

Never manufacture a preference from `OPINIONS.md` when the source text is
neutral.

## Input

Accept:

- text pasted with the invocation;
- a file path, preserving code blocks, data, legal language, and quotations
  unless the user explicitly asks to rewrite them;
- no argument, in which case use the most recent complete draft produced in the
  current conversation.

If no source text exists, ask for it and stop.

## Non-negotiable preservation rules

Preserve:

- the intended message and requested outcome;
- names, dates, amounts, commitments, caveats, and factual qualifiers;
- technical terms that are genuinely precise;
- the original level of certainty;
- deliberate politeness, disagreement, urgency, or restraint.

Never:

- add facts, examples, praise, apologies, promises, links, or claims;
- strengthen a weak claim into certainty;
- make the speaker warmer, harsher, funnier, or more diplomatic than the source
  requires;
- hide a concern behind generic positivity;
- use deliberate errors as proof of humanity;
- rewrite quoted material without permission.

If the source contains a likely factual error or contradiction, flag it in one
plain line rather than silently laundering it.

## Process

### 1. Identify the real job of the text

Determine:

- medium: email, Slack/chat, social post, document, announcement, or other;
- audience and relationship;
- single primary point;
- action, decision, or response expected from the reader;
- facts and wording that must survive unchanged.

Make the obvious medium assumption when safe. Do not ask a question merely to
avoid making a routine judgment.

### 2. Strip the generated-text scaffolding

Before rewriting, remove the hidden structure typical of AI drafts:

- throat-clearing before the actual point;
- generic framing that could fit any topic;
- repeated summaries of what was just said;
- symmetrical paragraph construction;
- headings for material that does not need headings;
- bullet lists used only to manufacture clarity;
- three-item lists used as rhythm rather than substance;
- conclusion paragraphs that merely restate the opening;
- excessive caveats placed before the position;
- fake collaborative language such as `let's dive in`, `we can explore`, or
  `here's a breakdown`.

Do not preserve the source's structure merely because it is grammatically
correct.

### 3. Rewrite from intent, not sentence-by-sentence

Write the message again from the extracted intent.

Use:

- the point early, usually in the first one or two sentences;
- plain words unless domain jargon is more accurate;
- concrete nouns and verbs;
- sentence lengths that vary naturally;
- transitions only where the reader actually needs one;
- reasoning attached to opinions;
- direct acknowledgment before disagreement or bad news;
- contractions where they fit the medium;
- occasional repetition when a human would naturally repeat the important
  word instead of searching for a synonym.

A human draft is allowed to be slightly uneven. It should not look engineered
for rhythm.

### 4. Run the AI-smell pass

Rewrite every detected instance of the following unless the source genuinely
requires it:

- stock AI vocabulary: `delve`, `pivotal`, `underscore`, `leverage`, `seamless`,
  `robust`, `landscape`, `additionally`, `foster`, `nuanced`, `multifaceted`,
  `transformative`, `comprehensive`, `holistic`, `realm`, `tapestry`;
- inflated verbs and nouns where `is`, `has`, `uses`, `shows`, or `helps` is
  accurate;
- `not just X, but Y`, `it is not X, it is Y`, and reflexive contrast formulas;
- `whether you're X or Y` audience padding;
- `in today's fast-paced...` and other generic scene-setting;
- `it's important to note`, `it's worth noting`, `that said`, and similar
  throat-clearing;
- trailing `-ing` clauses that explain significance after the sentence already
  ended;
- fake precision through unnecessary numbered frameworks;
- adjective stacks and inflated significance;
- rhetorical questions whose answer is obvious;
- overuse of em dashes, semicolons, parentheses, bold text, title-case headings,
  emoji, and exclamation points;
- polished corporate filler such as `moving forward`, `align`, `unlock`,
  `drive impact`, `at scale`, or `best-in-class` unless it is the precise term;
- sycophancy, automatic agreement, and empty praise;
- a closing sentence that announces the takeaway instead of ending naturally.

Use a plain hyphen instead of an em dash in plain-text media unless the source
requires typographic punctuation.

### 5. Run the read-aloud test

Read the rewrite as speech, not as prose on a screen.

Fix any line that:

- sounds like a presentation voice-over;
- has too many balanced clauses;
- contains several abstract nouns in a row;
- would make the speaker pause in an unnatural place;
- sounds more polished than the relationship or medium calls for;
- explains something the audience already knows;
- feels like it was written to impress rather than communicate.

Do not make every sentence short. Choppy uniformity is another AI tell.

### 6. Compress once

Remove anything that does not change meaning, tone, or required context.

Humanizing usually shortens the text. Do not shorten when the user explicitly
needs detail, evidence, diplomacy, or a formal record.

### 7. Final fidelity check

Confirm:

- no fact or commitment changed;
- no content was invented;
- the ask is explicit when an ask exists;
- the first paragraph contains the real point;
- the output fits the medium;
- banned AI patterns are absent;
- the result sounds like one person speaking to another, not a model presenting
  an optimized answer.

## Delivery

Return only the rewritten, copy-ready text.

Add one short note above it only when a factual concern, necessary assumption,
or deliberate omission must be disclosed. Do not explain the editing process
unless asked.

When the user explicitly asks for in-place file editing, edit only the prose
scope requested and preserve the rest of the file.

## Feedback loop

When Manish says a rewrite still does not sound like him, identify the concrete
miss. Update `~/.claude/VOICE.md` only when he explicitly asks to make that
correction durable; do not silently mutate his canonical voice profile.
