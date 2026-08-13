---
name: article
summary: Compatibility entry point for the editorial-engine skill.
description: Use only as a compatibility alias for previous /article invocations. Editorial logic lives exclusively in editorial-engine.
argument-hint: "<same arguments accepted by editorial-engine>"
user-invocable: true
disable-model-invocation: false
---

# Article compatibility shim

This skill contains no independent editorial policy.

Immediately invoke `editorial-engine` with the user's original article request
and arguments. Do not reproduce, fork, or override editorial behavior here.

`editorial-engine` is the single source of truth for research, drafting,
humanization, fact-checking, visual planning, final review, and publication
readiness.
