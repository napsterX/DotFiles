---
name: humanize
description: Rewrite text in Manish's voice so it reads as human-written, not AI-generated. Use whenever Manish asks to humanize, de-AI, or rewrite text, asks to make something "sound like me" or "less like AI", or whenever drafting any outward-facing prose on his behalf (email, Slack, social posts, docs, announcements). Takes the text inline, as a file path, or from the most recent draft in the conversation.
---

# Humanize

Rewrite the given text so a colleague would assume Manish typed it himself.
This skill exists so he never has to re-explain his voice or the AI-writing tells; everything is codified here and in the files below.

## Required reading, in order

1. `~/.claude/VOICE.md` - the canonical voice profile. The "Never do this" section is a hard ban list built from Wikipedia's "Signs of AI writing" guide plus Manish's own rules. If this file is missing, stop and tell him instead of improvising.
2. `~/.claude/OPINIONS.md` - only when the text argues a position or makes a recommendation, so the substance matches how he thinks, not just how he sounds.

## Input

Accept any of:

- Text pasted directly with the invocation.
- A file path; read the file and rewrite its prose (leave code blocks, data, and quoted material untouched).
- Nothing; humanize the most recent draft I produced in this conversation.

If there is genuinely no text to work on, ask for it.

## Process

### 1. Identify the medium

Email, Slack, social post, doc, or something else.
The per-medium rules in VOICE.md change the output substantially (greeting-and-close in email, lowercase openings in Slack, sentence-per-line in Markdown docs).
If the medium is ambiguous and it matters, make the obvious assumption and say what you assumed; do not interrogate him about it.

### 2. Extract the intent, then rewrite from scratch

Do not line-edit the original.
Identify what the text is actually trying to say (the ask, the news, the argument), then write it fresh in Manish's voice:

- Warm but efficient; the point arrives early.
- Flowing, layered sentences with natural unevenness, not staccato fragments and not uniform lengths.
- Opinions carry their reasoning.
- Disagreement or bad news leads with genuine acknowledgment, then the concern, delivered early rather than buried.
- Plain words unless jargon is the precise term for a technical audience.
- At most one dry aside, and only if it arrives naturally.

### 3. Run the ban-list pass

Re-scan the draft against every item in VOICE.md's "Never do this" section.
This pass is mandatory; these patterns are reflexive and will appear in first drafts.
The highest-frequency offenders to check for:

- AI vocabulary ("delve", "pivotal", "underscore", "leverage", "seamless", "robust", "landscape", "additionally", "foster").
- Negative parallelisms ("not just X, but Y" / "it's not X, it's Y" / reflexive "X rather than Y").
- Rule-of-three lists used as rhythm filler.
- "Serves as" / "features" / "offers" where "is" or "has" would do.
- Trailing "-ing" analysis clauses ("...highlighting the importance of...").
- Elegant variation; repeat the word instead.
- Throat-clearing ("It's worth noting", "That being said"), sycophancy, fake collaboration ("let's dive in"), and summary sentences that restate the paragraph.
- Inflated significance ("stands as a testament", "plays a crucial role").
- Em dashes (use a plain dash), Title Case headings, bold-header bullet patterns, emoji as structure, curly quotes in plain-text media, exclamation-point enthusiasm.

Anything caught gets rewritten, not patched around.

### 4. Verify the mechanics

- Nothing invented: no fabricated names, numbers, links, or quotes that were not in the source text. If the original contains a claim that looks wrong, flag it rather than laundering it.
- Facts, commitments, dates, and amounts from the original are all preserved.
- Length is proportional to the ask; humanizing usually means shortening.
- Emoji and exclamation points: zero by default, one at most.
- No profanity. Clean grammar, except lowercase openings are fine in Slack/chat.

### 5. Deliver

Output the rewritten text ready to copy-paste, with nothing above it except a one-line note only when something needs flagging (an assumption made, a claim that looks wrong, content deliberately cut).
Do not annotate the rewrite with explanations of what changed unless he asks.
If he gave a file path and asks for it in place, edit the file.

## Feedback loop

When Manish says a rewrite does not sound like him, treat the correction as durable: update `~/.claude/VOICE.md` (and this skill, if the process itself was wrong) so the same miss cannot happen twice.
