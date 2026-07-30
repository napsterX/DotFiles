# FirstMate Notification Policy

Use `scripts/notify_firstmate.py` for terminal unattended-run notifications.
FirstMate is the only notification route. Do not fall back to `osascript`, direct
Notification Center calls, email, or another notifier.

Send one notification for:

- `RUN_COMPLETED`;
- `RUN_STOPPED` because of a repository-wide blocker or unsafe state;
- `MANUAL_ACTION_REQUIRED` when final audit creates a PR but requires user action
  or finalization cannot proceed automatically.

Do not notify for each issue.

The message should contain repository, fixed/blocked/failed/timed-out counts, PR
or finalization disposition when available, and the run ID. Do not include
secrets, full logs, customer data, or exploit details.

The adapter discovers `firstmate-notify` through `FIRSTMATE_NOTIFY_BIN`, `PATH`,
or `~/.local/bin/firstmate-notify`. It probes the CLI and invokes it without a
shell. Notification delivery is non-blocking:

- record `DELIVERED`, `NOT_AVAILABLE`, or `FAILED_NONBLOCKING` in the journal;
- report failure in the final output;
- never change the run verdict or prevent lock release solely because a
  notification could not be delivered.
