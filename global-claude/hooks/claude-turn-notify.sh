#!/bin/bash
# Desktop notification when a tmux-hosted Claude Code session needs the captain.
#
# Wired to three global hook events in ~/.claude/settings.json, so every Claude
# Code session is covered automatically - including sessions and tmux sessions
# created long after this was installed. No discovery, no polling.
#
#   Stop          the turn finished; ready for the next prompt   -> attention
#   StopFailure   the turn died and needs restarting              -> urgent
#   Notification  blocked mid-turn, waiting on the captain        -> routine
#
# The levels differ on purpose. "A prompt finished" is the alert the captain
# actually asked for and keeps the middle level. "Claude is blocked on you" is
# real but secondary, so it sits at routine and is distinguishable at a glance
# rather than looking identical to a finished turn.
#
# Deliberately NOT wired to SubagentStop. Claude Code routes subagent completion
# to that separate event, so an internal thread finishing can never reach this
# script; only the top-level turn ending does.
#
# Safety: this runs inside turn teardown and notification dispatch. Every path
# exits 0 so a problem here can never block or fail a turn.

set -u

HOOK_DIR="$HOME/.claude/hooks"
LOG="$HOOK_DIR/turn-notify.log"
IGNORE="$HOOK_DIR/turn-notify-ignore"

NOTIFY="$HOME/.local/bin/firstmate-notify"
if [ ! -x "$NOTIFY" ]; then
  NOTIFY="$(command -v firstmate-notify 2>/dev/null || true)"
fi

log() {
  printf '%s %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*" >>"$LOG" 2>/dev/null || true
}

# Keep the log bounded; it is a debugging aid, not a record of value.
if [ -f "$LOG" ] && [ "$(wc -c <"$LOG" 2>/dev/null || echo 0)" -gt 262144 ]; then
  tail -n 500 "$LOG" >"$LOG.tmp" 2>/dev/null && mv "$LOG.tmp" "$LOG" 2>/dev/null || true
fi

input="$(cat 2>/dev/null || true)"

jqf() {
  printf '%s' "$input" | jq -r "$1" 2>/dev/null || true
}

event="$(jqf '.hook_event_name // "Stop"')"
cwd="$(jqf '.cwd // ""')"
reason="$(jqf '.stop_reason // ""')"
ntype="$(jqf '.notification_type // ""')"
transcript="$(jqf '.transcript_path // ""')"
sid="$(jqf '.session_id // ""')"

# True when this session still has background work running - a background agent
# or a background shell that will wake the session back up on its own. A turn
# that ends in that state is not waiting on the captain, even when the work was
# dispatched several turns ago and a sibling worker is what just reported back.
#
# Two independent conditions must both hold, because either alone fails badly:
#
#   1. The work was launched and has never reported back. Claude Code records a
#      <task-id> notification when async work reports, for agents and shells
#      alike, so this pairing is exact. On its own, though, a completion record
#      that never arrives would suppress that session's alerts forever - and
#      silence is indistinguishable from "still working", the worst failure this
#      can have.
#   2. Its output file was touched recently. That measures whether the worker is
#      actually alive rather than trusting bookkeeping, which bounds the damage
#      of condition 1 to the liveness window.
#
# The output path is read from the launch record rather than constructed: work
# launched before a session resume lives under a different session's directory,
# so a constructed path would silently miss it.
#
# Every failure path returns false, so an unreadable, reshaped, or unfamiliar
# transcript degrades to alerting rather than to silence.
BACKGROUND_LIVENESS_SECONDS="${BACKGROUND_LIVENESS_SECONDS:-1800}"

background_work_in_flight() {
  [ -n "$transcript" ] && [ -r "$transcript" ] || return 1

  local reported launches now id file mtime
  reported="$(grep -o '<task-id>[A-Za-z0-9_-]*</task-id>' "$transcript" 2>/dev/null \
    | sed 's/<[^>]*>//g' | sort -u)"

  launches="$(
    {
      grep '"status": *"async_launched"' "$transcript" 2>/dev/null \
        | jq -r '.toolUseResult | select(.agentId != null)
                 | "\(.agentId)\t\(.outputFile // "")"' 2>/dev/null
      grep -o 'Command running in background with ID: [A-Za-z0-9_-]*\. Output is being written to: [^ ]*\.output' \
        "$transcript" 2>/dev/null \
        | sed -E 's/.*ID: ([A-Za-z0-9_-]+)\. Output is being written to: (.*)$/\1	\2/'
    } | sort -u
  )"
  [ -n "$launches" ] || return 1

  now="$(date +%s)"
  while IFS="$(printf '\t')" read -r id file; do
    [ -n "$id" ] || continue
    printf '%s\n' "$reported" | grep -qxF "$id" && continue
    [ -n "$file" ] && [ -e "$file" ] || continue
    mtime="$(stat -L -f %m "$file" 2>/dev/null)" || continue
    [ -n "$mtime" ] || continue
    if [ "$(( now - mtime ))" -le "$BACKGROUND_LIVENESS_SECONDS" ]; then
      BACKGROUND_WORKER_ID="$id"
      return 0
    fi
  done <<LAUNCHES
$launches
LAUNCHES

  return 1
}

# Collapse text to one safe, bounded line. iconv drops any partial multibyte
# character left behind by a byte-wise truncation.
one_line() {
  printf '%s' "$1" \
    | tr '\n\r\t' '   ' \
    | tr -d '\000-\037' \
    | sed 's/  */ /g; s/^ //; s/ $//' \
    | cut -c1-180 \
    | iconv -c -f UTF-8 -t UTF-8 2>/dev/null || true
}

# Per-session cooldown for repeated failure alerts.
#
# A session failing in a loop used to alert on every attempt: four urgent
# banners from one session inside 64 seconds was measured on 2026-08-14. The
# captain needs to learn that a session broke, not to be told again each time it
# retries. The window is keyed by session, so a second session failing still
# alerts immediately rather than being hidden behind the first one's cooldown.
#
# The stamp is written when the alert is allowed rather than after delivery, so
# a burst is bounded to one banner per window regardless of what the notifier
# does. Every error path returns 0 (alert anyway): silence about a dead session
# is a worse failure than one extra banner.
FAILURE_COOLDOWN_SECONDS="${FAILURE_COOLDOWN_SECONDS:-300}"
STATE_DIR="$HOOK_DIR/.turn-notify-state"

# Did a turn originate from the captain, or from a background worker waking the
# session?
#
# Both end with a Stop event, which is why "a sub-agent finished" was audible:
# when a worker reports back, the session writes a short report and that turn
# ends, firing Stop exactly as a real prompt would. The existing background
# check only stays quiet while OTHER work is still running, so the LAST worker
# finishing always produced an alert the captain never asked for.
#
# UserPromptSubmit is the one event that only the captain can cause, so it is
# the structural separator - the same reasoning that kept SubagentStop unwired
# rather than filtering subagents by heuristic.
#
#   prompt-<sid>  a captain prompt is in flight and has not been answered yet
#   seen-<sid>    this session has produced at least one UserPromptSubmit, so
#                 the absence of a pending marker is meaningful rather than
#                 simply unknown
#
# The seen marker is what keeps this fail-open. Without it, a session that
# started before this tracking existed - or any case where UserPromptSubmit does
# not arrive - would go permanently silent, and silence is indistinguishable
# from "still working". Absent evidence that tracking works for a session, the
# alert is sent.
prompt_state_file() {
  local kind="$1" key
  [ -n "$sid" ] || return 1
  key="$(printf '%s' "$sid" | sed 's/[^A-Za-z0-9._-]/_/g' 2>/dev/null)"
  [ -n "$key" ] || return 1
  mkdir -p "$STATE_DIR" 2>/dev/null || return 1
  printf '%s/%s-%s' "$STATE_DIR" "$kind" "$key"
}

mark_captain_prompt() {
  local p s
  p="$(prompt_state_file prompt)" || return 0
  s="$(prompt_state_file seen)" || return 0
  : >"$p" 2>/dev/null || true
  : >"$s" 2>/dev/null || true
  # Bound growth: session markers older than a week cannot belong to a live
  # session, and leaving them would slowly fill the state directory.
  find "$STATE_DIR" -type f -mtime +7 -delete 2>/dev/null || true
}

# 0 = this turn traces back to a captain prompt (or we cannot tell, so alert).
turn_is_captain_initiated() {
  local p s
  p="$(prompt_state_file prompt)" || return 0
  s="$(prompt_state_file seen)" || return 0
  [ -f "$s" ] || return 0
  [ -f "$p" ]
}

clear_captain_prompt() {
  local p
  p="$(prompt_state_file prompt)" || return 0
  rm -f "$p" 2>/dev/null || true
}

failure_alert_allowed() {
  local key stamp last now
  key="$(printf '%s' "$sess" | sed 's/[^A-Za-z0-9._-]/_/g' 2>/dev/null)"
  [ -n "$key" ] || return 0
  mkdir -p "$STATE_DIR" 2>/dev/null || return 0
  stamp="$STATE_DIR/fail-$key"
  now="$(date +%s 2>/dev/null)" || return 0
  [ -n "$now" ] || return 0
  if [ -f "$stamp" ]; then
    last="$(cat "$stamp" 2>/dev/null)"
    case "$last" in
      '' | *[!0-9]*) last="" ;;
    esac
    if [ -n "$last" ] && [ "$(( now - last ))" -lt "$FAILURE_COOLDOWN_SECONDS" ]; then
      return 1
    fi
  fi
  printf '%s' "$now" >"$stamp" 2>/dev/null || true
  return 0
}

# Only interactive terminal work is interesting. A Claude session with no tmux
# pane is not one the captain is switching between, so stay silent.
if [ -z "${TMUX:-}" ] || [ -z "${TMUX_PANE:-}" ]; then
  log "skip non-tmux event=$event${ntype:+ type=$ntype} cwd=$cwd"
  exit 0
fi

# Resolve live rather than caching, so renamed or moved panes stay correct.
sess="$(tmux display-message -p -t "$TMUX_PANE" '#{session_name}' 2>/dev/null || true)"
[ -n "$sess" ] || sess="tmux"

if [ -f "$IGNORE" ]; then
  while IFS= read -r line || [ -n "$line" ]; do
    line="${line%%#*}"
    line="$(printf '%s' "$line" | tr -d '[:space:]')"
    [ -n "$line" ] || continue
    if [ "$line" = "$sess" ]; then
      log "skip ignored session=$sess event=$event"
      exit 0
    fi
  done <"$IGNORE"
fi

case "$event" in
  UserPromptSubmit)
    # Only the captain can cause this. It records that a turn he started is in
    # flight and never notifies anything itself.
    mark_captain_prompt
    log "captain prompt session=$sess"
    exit 0
    ;;

  Notification)
    # Filter by exclusion, not by an allowlist: a notification type nobody
    # anticipated is far more likely to mean "the captain is needed" than not,
    # and a missed alert leaves a session stalled indefinitely. Only types known
    # to be redundant or uninteresting are dropped here.
    #
    #   agent_completed        already covered by the Stop event
    #   idle_prompt            fires when the input box sits untouched, which
    #                          would nag a second time about a finished turn
    #   auth_success           informational, needs nothing
    #   elicitation_complete   the dialog is already answered
    #   elicitation_response   the dialog is already answered
    case "$ntype" in
      agent_completed|idle_prompt|auth_success|elicitation_complete|elicitation_response)
        log "skip notification session=$sess type=$ntype"
        exit 0
        ;;
    esac
    title="$sess is waiting on you"
    level="routine"
    body="$(one_line "$(jqf '.message // ""')")"
    [ -n "$body" ] || body="Claude is waiting on you before it can continue."
    ;;

  StopFailure)
    if ! failure_alert_allowed; then
      log "skip failure-cooldown session=$sess window=${FAILURE_COOLDOWN_SECONDS}s"
      exit 0
    fi
    title="$sess stopped with an error"
    level="urgent"
    body="The turn ended early${reason:+ ($reason)} and needs restarting."
    snippet="$(one_line "$(jqf '.last_assistant_message // ""')")"
    [ -n "$snippet" ] && body="$body $snippet"
    ;;

  *)
    # A session still running background work is not waiting on the captain.
    # StopFailure deliberately does not get this exemption: a turn that died needs
    # him regardless of what it had running.
    if background_work_in_flight; then
      log "skip background-work-in-flight session=$sess worker=${BACKGROUND_WORKER_ID:-?}"
      exit 0
    fi
    # The turn ended, nothing is still running, but the captain never started
    # it: a worker reported back, the session summarised it, and the turn
    # closed. That is the sub-agent alert he does not want. Stay silent and
    # leave no pending marker to clear.
    if ! turn_is_captain_initiated; then
      log "skip not-captain-initiated session=$sess (turn woken by background work)"
      exit 0
    fi
    clear_captain_prompt
    title="$sess is ready"
    level="attention"
    body="$(one_line "$(jqf '.last_assistant_message // ""')")"
    [ -n "$body" ] || body="Claude finished this turn and is waiting for your next prompt."
    ;;
esac

if [ -z "$NOTIFY" ]; then
  log "FAILED no firstmate-notify on PATH session=$sess event=$event"
  exit 0
fi

# Clicking the banner jumps to the terminal tab that raised it. The session name
# is percent-encoded so names with spaces or punctuation survive the round trip.
encoded="$(printf '%s' "$sess" | jq -sRr @uri 2>/dev/null || true)"
[ -n "$encoded" ] || encoded="$sess"

"$NOTIFY" notify \
  --source claude-turn \
  --level "$level" \
  --title "$title" \
  --body "$body" \
  --action-type url \
  --action-value "claudejump://$encoded" >/dev/null 2>&1
rc=$?

# A refused click action must never cost the captain the notification itself,
# which is the whole point of this hook.
if [ "$rc" -ne 0 ]; then
  "$NOTIFY" notify \
    --source claude-turn \
    --level "$level" \
    --title "$title" \
    --body "$body" >/dev/null 2>&1
  rc=$?
  [ "$rc" -eq 0 ] && log "jump action refused by notifier; sent plain notification"
fi

if [ "$rc" -eq 0 ]; then
  log "notified session=$sess event=$event${ntype:+ type=$ntype} reason=${reason:-none} cwd=$cwd"
else
  log "FAILED notify rc=$rc session=$sess event=$event${ntype:+ type=$ntype}"
fi

exit 0
