#!/usr/bin/env bash
#
# block-manual-push.sh - PreToolUse(Bash) hook.
#
# Denies a raw `git push` so every change ships through the no-mistakes gate
# (`/no-mistakes --yes`: validate, push, PR, CI) instead of a manual push.
# Escape hatch: set ALLOW_MANUAL_PUSH=1 for a deliberate, one-off manual push.
#
# It is deliberately FAIL-OPEN: on any parse trouble (missing jq, unexpected
# payload) it exits 0 and allows the command, so a bug here never bricks the
# agent's shell. It only ever blocks a command it is confident is a `git push`.
#
# Detection walks each shell segment (split on ; && || | &) so that a real push
# is caught even inside a compound command (`git add -A && git push`), while a
# non-push that merely mentions the word is not (`git log --grep push`,
# `echo git push`). Within a segment it finds the git invocation, skips git's
# global options (including `-C <path>` / `-c <kv>` which consume a value token),
# and blocks only when the resulting subcommand is exactly `push`.

payload="$(cat 2>/dev/null)" || exit 0

# Escape hatch (session-wide): ALLOW_MANUAL_PUSH=1 exported into the Claude Code
# environment disables the guard for the whole session.
[ "${ALLOW_MANUAL_PUSH:-}" = "1" ] && exit 0

# Only inspect Bash tool calls; allow anything else.
tool="$(printf '%s' "$payload" | jq -r '.tool_name // "Bash"' 2>/dev/null)" || exit 0
[ "$tool" = "Bash" ] || exit 0

cmd="$(printf '%s' "$payload" | jq -r '.tool_input.command // empty' 2>/dev/null)" || exit 0
[ -n "$cmd" ] || exit 0

# Escape hatch (per-command): an inline `ALLOW_MANUAL_PUSH=1 git push ...` sets
# the variable for git, not for this hook process, so the hook cannot read it
# from the environment - it reads it from the command TEXT instead. A command
# that carries the assignment is a deliberate opt-out and is allowed through.
case "$cmd" in
  *ALLOW_MANUAL_PUSH=1*) exit 0 ;;
esac

is_git_push() {
  local norm segment i t sub
  # Turn shell command separators into newlines so each command runs through the
  # walker on its own.
  norm="$(printf '%s\n' "$1" | sed -E 's/\&\&/\n/g; s/\|\|/\n/g; s/[;|&]/\n/g')"
  while IFS= read -r segment; do
    # shellcheck disable=SC2206
    local tokens=($segment) # word-split on whitespace
    i=0
    # Skip leading VAR=value assignments and common command prefixes.
    while [ "$i" -lt "${#tokens[@]}" ]; do
      t="${tokens[$i]}"
      if [[ "$t" =~ ^[A-Za-z_][A-Za-z0-9_]*= ]]; then i=$((i + 1)); continue; fi
      case "$t" in
        env | command | sudo | nice | nohup | time) i=$((i + 1)); continue ;;
      esac
      break
    done
    [ "$i" -ge "${#tokens[@]}" ] && continue
    # Is this a git invocation (`git`, `/usr/bin/git`, ...)?
    case "${tokens[$i]}" in
      git | */git) ;;
      *) continue ;;
    esac
    i=$((i + 1))
    # Skip git's global options to reach the subcommand.
    sub=""
    while [ "$i" -lt "${#tokens[@]}" ]; do
      t="${tokens[$i]}"
      case "$t" in
        -C | -c | --git-dir | --work-tree | --namespace | --exec-path | --super-prefix)
          i=$((i + 2)); continue ;; # consumes the next token as its value
        -*) i=$((i + 1)); continue ;;
        *) sub="$t"; break ;;
      esac
    done
    [ "$sub" = "push" ] && return 0
  done <<<"$norm"
  return 1
}

if is_git_push "$cmd"; then
  cat <<'JSON'
{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"Manual git push is disabled. Ship through the no-mistakes gate: run /no-mistakes with --yes (validate, push, PR, CI). For a deliberate one-off manual push, set ALLOW_MANUAL_PUSH=1."}}
JSON
  exit 0
fi

exit 0
