#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PACKAGE_SKILLS="$SCRIPT_DIR/skills"
PACKAGE_AGENTS="$SCRIPT_DIR/agents"
PACKAGE_SESSION_CONTINUITY="$SCRIPT_DIR/session-continuity"
PACKAGE_EDITORIAL_CONFIG="$SCRIPT_DIR/config/editorial"
MANIFEST="$SCRIPT_DIR/MANIFEST"
AGENTS_MANIFEST="$SCRIPT_DIR/AGENTS_MANIFEST"
VALIDATOR="$SCRIPT_DIR/scripts/validate_package.py"
HOOK_REPAIR="$SCRIPT_DIR/scripts/repair_session_hooks.py"
CLAUDE_ROOT="${CLAUDE_ROOT:-$HOME/.claude}"
INSTALL_ROOT="$CLAUDE_ROOT/skills"
AGENTS_INSTALL_ROOT="$CLAUDE_ROOT/agents"
SESSION_CONTINUITY_INSTALL_ROOT="$CLAUDE_ROOT/session-continuity"
EDITORIAL_CONFIG_ROOT="${EDITORIAL_CONFIG_ROOT:-$CLAUDE_ROOT/editorial}"
DOTFILES_REPO="${DOTFILES_REPO:-$HOME/git/DotFiles}"
DOTFILES_SKILLS_REL="global-claude/skills"
DOTFILES_AGENTS_REL="global-claude/agents"
DOTFILES_SESSION_CONTINUITY_REL="global-claude/session-continuity"
DOTFILES_EDITORIAL_CONFIG_REL="global-claude/editorial"
DOTFILES_PACKAGE_TOOLS_REL="global-claude/package-tools"
DOTFILES_SETTINGS_REL="global-claude/settings.json"
DOTFILES_SETTINGS_LOCAL_REL="global-claude/settings.local.json"
LEGACY_SKILL="fix-bugs"
RETIRED_SKILL="implementation-log"
LEGACY_AGENT="bug-fix-worker"
TARGET_BRANCH="${DOTFILES_TARGET_BRANCH:-}"
DRY_RUN=false
TIMESTAMP="$(date -u +%Y%m%dT%H%M%SZ)"
BACKUP_ROOT="$CLAUDE_ROOT/skill-backups/$TIMESTAMP"
TMP_ROOT=""

log() {
  printf '%s\n' "$*"
}

fail() {
  printf 'ERROR: %s\n' "$*" >&2
  exit 1
}

usage() {
  cat <<'USAGE'
Usage: ./install.sh [--dry-run] [--target-branch BRANCH]

Options:
  --dry-run               Validate and report the exact planned changes without
                          modifying installed skills, DotFiles, or the remote.
  --target-branch BRANCH  Override the detected DotFiles default branch.
  -h, --help              Show this help text.

Environment overrides:
  CLAUDE_ROOT             Claude configuration root. Default: ~/.claude
  DOTFILES_REPO           Existing local DotFiles checkout. Default: ~/git/DotFiles
  DOTFILES_TARGET_BRANCH  Same as --target-branch.
  EDITORIAL_CONFIG_ROOT    editorial visual config. Default: ~/.claude/editorial
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run)
      DRY_RUN=true
      shift
      ;;
    --target-branch)
      [[ $# -ge 2 ]] || fail "--target-branch requires a branch name"
      TARGET_BRANCH="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      fail "unknown argument: $1"
      ;;
  esac
done

cleanup() {
  if [[ -n "$TMP_ROOT" && -d "$TMP_ROOT" ]]; then
    rm -rf "$TMP_ROOT"
  fi
}
trap cleanup EXIT

command -v python3 >/dev/null 2>&1 || fail "python3 is required"
command -v git >/dev/null 2>&1 || fail "git is required"
command -v rsync >/dev/null 2>&1 || fail "rsync is required"

[[ -d "$PACKAGE_SKILLS" ]] || fail "package skills directory not found: $PACKAGE_SKILLS"
[[ -d "$PACKAGE_AGENTS" ]] || fail "package agents directory not found: $PACKAGE_AGENTS"
[[ -x "$PACKAGE_SESSION_CONTINUITY/bin/session_state.py" ]] || fail "session continuity helper missing or not executable"
[[ -x "$PACKAGE_SESSION_CONTINUITY/tests/test_session_state.py" ]] || fail "session continuity tests missing or not executable"
[[ -f "$MANIFEST" ]] || fail "manifest not found: $MANIFEST"
[[ -f "$AGENTS_MANIFEST" ]] || fail "agents manifest not found: $AGENTS_MANIFEST"
[[ -x "$VALIDATOR" ]] || fail "validator not executable: $VALIDATOR"
[[ -x "$HOOK_REPAIR" ]] || fail "hook repair helper not executable: $HOOK_REPAIR"
[[ -f "$PACKAGE_EDITORIAL_CONFIG/visual-style.md" ]] || fail "editorial visual-style config missing"

# ai-image and its configuration are intentionally external to this package.
# Do not validate, back up, copy, install, update, or remove that user-managed runtime.

log "Validating package..."
# Installer validation focuses on the packaged skill/agent contracts. The
# unchanged session-continuity and hook-repair unit suites are shipped for
# explicit maintenance verification, but are not rerun during every install;
# running both process-heavy suites back-to-back with repository-verification
# fixtures can create platform-specific process-pressure stalls.
python3 "$VALIDATOR" \
  --skills-root "$PACKAGE_SKILLS" \
  --manifest "$MANIFEST" \
  --agents-root "$PACKAGE_AGENTS" \
  --agents-manifest "$AGENTS_MANIFEST" \
  --run-tests

if [[ -f "$SCRIPT_DIR/CHECKSUMS.sha256" ]]; then
  command -v shasum >/dev/null 2>&1 || fail "shasum is required for checksum verification"
  log "Verifying package checksums..."
  (
    cd "$SCRIPT_DIR"
    shasum -a 256 -c CHECKSUMS.sha256
  )
fi

[[ -d "$DOTFILES_REPO/.git" ]] || fail "DotFiles Git repository not found: $DOTFILES_REPO"
REMOTE_URL="$(git -C "$DOTFILES_REPO" remote get-url origin 2>/dev/null || true)"
[[ -n "$REMOTE_URL" ]] || fail "DotFiles origin remote is not configured: $DOTFILES_REPO"

remote_has_branch() {
  local branch="$1"
  git ls-remote --exit-code --heads "$REMOTE_URL" "$branch" >/dev/null 2>&1
}

detect_target_branch() {
  local detected=""
  local origin_head=""
  local current_branch=""

  if [[ -n "$TARGET_BRANCH" ]]; then
    git check-ref-format --branch "$TARGET_BRANCH" >/dev/null 2>&1 \
      || fail "invalid target branch name: $TARGET_BRANCH"
    remote_has_branch "$TARGET_BRANCH" \
      || fail "remote branch does not exist: $TARGET_BRANCH"
    printf '%s\n' "$TARGET_BRANCH"
    return
  fi

  detected="$(
    git ls-remote --symref "$REMOTE_URL" HEAD 2>/dev/null \
      | awk '$1 == "ref:" { sub("refs/heads/", "", $2); print $2; exit }'
  )"
  if [[ -n "$detected" ]] && remote_has_branch "$detected"; then
    printf '%s\n' "$detected"
    return
  fi

  origin_head="$(
    git -C "$DOTFILES_REPO" symbolic-ref --quiet --short refs/remotes/origin/HEAD \
      2>/dev/null || true
  )"
  origin_head="${origin_head#origin/}"
  if [[ -n "$origin_head" ]] && remote_has_branch "$origin_head"; then
    printf '%s\n' "$origin_head"
    return
  fi

  for detected in main master; do
    if remote_has_branch "$detected"; then
      printf '%s\n' "$detected"
      return
    fi
  done

  current_branch="$(git -C "$DOTFILES_REPO" branch --show-current || true)"
  if [[ -n "$current_branch" ]] && remote_has_branch "$current_branch"; then
    printf '%s\n' "$current_branch"
    return
  fi

  fail "could not determine the DotFiles remote default branch; rerun with --target-branch BRANCH"
}

log "Detecting DotFiles target branch..."
TARGET_BRANCH="$(detect_target_branch)"
log "DotFiles target branch: $TARGET_BRANCH"

LOCAL_NAME="$(git -C "$DOTFILES_REPO" config --get user.name || true)"
LOCAL_EMAIL="$(git -C "$DOTFILES_REPO" config --get user.email || true)"
[[ -n "$LOCAL_NAME" ]] || fail "Git user.name is not configured for DotFiles"
[[ -n "$LOCAL_EMAIL" ]] || fail "Git user.email is not configured for DotFiles"

TMP_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/claude-skills-update.XXXXXX")"
STAGED_INSTALL="$TMP_ROOT/staged-skills"
STAGED_AGENTS="$TMP_ROOT/staged-agents"
STAGED_SESSION_CONTINUITY="$TMP_ROOT/staged-session-continuity"
mkdir -p "$STAGED_INSTALL" "$STAGED_AGENTS" "$STAGED_SESSION_CONTINUITY"
rsync -a --delete --exclude '__pycache__' --exclude '*.pyc' "$PACKAGE_SESSION_CONTINUITY/" "$STAGED_SESSION_CONTINUITY/"

while IFS= read -r skill; do
  [[ -n "$skill" ]] || continue
  mkdir -p "$STAGED_INSTALL/$skill"
  rsync -a --delete --exclude '.DS_Store' \
    "$PACKAGE_SKILLS/$skill/" \
    "$STAGED_INSTALL/$skill/"
done < "$MANIFEST"

while IFS= read -r agent; do
  [[ -n "$agent" ]] || continue
  rsync -a --exclude '.DS_Store' \
    "$PACKAGE_AGENTS/$agent.md" \
    "$STAGED_AGENTS/$agent.md"
done < "$AGENTS_MANIFEST"

python3 "$VALIDATOR" \
  --skills-root "$STAGED_INSTALL" \
  --manifest "$MANIFEST" \
  --agents-root "$STAGED_AGENTS" \
  --agents-manifest "$AGENTS_MANIFEST"

log "Preflighting session hook repair..."
python3 "$HOOK_REPAIR" --claude-root "$CLAUDE_ROOT" --dry-run

if [[ "$DRY_RUN" == true ]]; then
  log ""
  log "DRY RUN COMPLETE — no files or Git references were changed."
  log "Would back up replaced and removed skills under: $BACKUP_ROOT"
  log "Would install session continuity helper into: $SESSION_CONTINUITY_INSTALL_ROOT"
  log "Would preserve/editable editorial visual style under: $EDITORIAL_CONFIG_ROOT"
  log "Would leave the externally managed ai-image binary and configuration completely untouched."
  log "Would synchronize package-owned session continuity files into: $DOTFILES_REPO/$DOTFILES_SESSION_CONTINUITY_REL"
  log "Would synchronize editorial visual style into: $DOTFILES_REPO/$DOTFILES_EDITORIAL_CONFIG_REL"
  log "Would synchronize package install/uninstall/verify tools into: $DOTFILES_REPO/$DOTFILES_PACKAGE_TOOLS_REL"
  log "Would repair stale hook references in local and tracked global Claude settings."
  log "Would install $(grep -cvE '^[[:space:]]*($|#)' "$MANIFEST") skills into: $INSTALL_ROOT"
  log "Would install $(grep -cvE '^[[:space:]]*($|#)' "$AGENTS_MANIFEST") agents into: $AGENTS_INSTALL_ROOT"
  log "Would remove: $INSTALL_ROOT/no-mistakes $INSTALL_ROOT/$RETIRED_SKILL"
  log "Would replace legacy skill: $INSTALL_ROOT/$LEGACY_SKILL -> $INSTALL_ROOT/fix-issues"
  log "Would remove generated packaging metadata from installed skill/agent roots before validation."
  log "Would replace legacy agent: $AGENTS_INSTALL_ROOT/$LEGACY_AGENT.md -> $AGENTS_INSTALL_ROOT/issue-fix-worker.md"
  log "Would synchronize skills into: $DOTFILES_REPO/$DOTFILES_SKILLS_REL"
  log "Would synchronize agents into: $DOTFILES_REPO/$DOTFILES_AGENTS_REL"
  log "Would merge the update into remote branch: $TARGET_BRANCH"
  log "Would push: origin/$TARGET_BRANCH"
  log "Would fast-forward the primary DotFiles checkout only when clean and already on $TARGET_BRANCH."
  exit 0
fi

mkdir -p "$INSTALL_ROOT" "$AGENTS_INSTALL_ROOT" "$BACKUP_ROOT"

log "Backing up replaced and removed skills, agents, and session continuity to: $BACKUP_ROOT"
if [[ -d "$SESSION_CONTINUITY_INSTALL_ROOT" ]]; then
  mkdir -p "$BACKUP_ROOT/session-continuity"
  rsync -a "$SESSION_CONTINUITY_INSTALL_ROOT/" "$BACKUP_ROOT/session-continuity/"
fi
for settings_file in "$CLAUDE_ROOT/settings.json" "$CLAUDE_ROOT/settings.local.json"; do
  if [[ -f "$settings_file" ]]; then
    mkdir -p "$BACKUP_ROOT/settings"
    cp -p "$settings_file" "$BACKUP_ROOT/settings/$(basename "$settings_file")"
  fi
done
while IFS= read -r skill; do
  [[ -n "$skill" ]] || continue
  if [[ -d "$INSTALL_ROOT/$skill" ]]; then
    mkdir -p "$BACKUP_ROOT/skills/$skill"
    rsync -a "$INSTALL_ROOT/$skill/" "$BACKUP_ROOT/skills/$skill/"
  fi
done < "$MANIFEST"

if [[ -d "$INSTALL_ROOT/no-mistakes" ]]; then
  mkdir -p "$BACKUP_ROOT/skills/no-mistakes"
  rsync -a "$INSTALL_ROOT/no-mistakes/" "$BACKUP_ROOT/skills/no-mistakes/"
fi
if [[ -d "$INSTALL_ROOT/$LEGACY_SKILL" ]]; then
  mkdir -p "$BACKUP_ROOT/skills/$LEGACY_SKILL"
  rsync -a "$INSTALL_ROOT/$LEGACY_SKILL/" "$BACKUP_ROOT/skills/$LEGACY_SKILL/"
fi
if [[ -d "$INSTALL_ROOT/$RETIRED_SKILL" ]]; then
  mkdir -p "$BACKUP_ROOT/skills/$RETIRED_SKILL"
  rsync -a "$INSTALL_ROOT/$RETIRED_SKILL/" "$BACKUP_ROOT/skills/$RETIRED_SKILL/"
fi
if [[ -f "$AGENTS_INSTALL_ROOT/$LEGACY_AGENT.md" ]]; then
  mkdir -p "$BACKUP_ROOT/agents"
  cp -p "$AGENTS_INSTALL_ROOT/$LEGACY_AGENT.md" "$BACKUP_ROOT/agents/$LEGACY_AGENT.md"
fi

while IFS= read -r agent; do
  [[ -n "$agent" ]] || continue
  if [[ -f "$AGENTS_INSTALL_ROOT/$agent.md" ]]; then
    mkdir -p "$BACKUP_ROOT/agents"
    cp -p "$AGENTS_INSTALL_ROOT/$agent.md" "$BACKUP_ROOT/agents/$agent.md"
  fi
done < "$AGENTS_MANIFEST"

if [[ -d "$EDITORIAL_CONFIG_ROOT" ]]; then
  mkdir -p "$BACKUP_ROOT/editorial"
  rsync -a "$EDITORIAL_CONFIG_ROOT/" "$BACKUP_ROOT/editorial/"
fi

log "Installing skills into: $INSTALL_ROOT"
while IFS= read -r skill; do
  [[ -n "$skill" ]] || continue
  install_stage="$TMP_ROOT/install-$skill"
  mkdir -p "$install_stage"
  rsync -a --delete "$STAGED_INSTALL/$skill/" "$install_stage/"
  rm -rf "$INSTALL_ROOT/$skill"
  mv "$install_stage" "$INSTALL_ROOT/$skill"
done < "$MANIFEST"

log "Installing agents into: $AGENTS_INSTALL_ROOT"
while IFS= read -r agent; do
  [[ -n "$agent" ]] || continue
  install_stage="$TMP_ROOT/install-agent-$agent.md"
  cp -p "$STAGED_AGENTS/$agent.md" "$install_stage"
  mv "$install_stage" "$AGENTS_INSTALL_ROOT/$agent.md"
done < "$AGENTS_MANIFEST"

rm -rf "$INSTALL_ROOT/no-mistakes" "$INSTALL_ROOT/$LEGACY_SKILL" "$INSTALL_ROOT/$RETIRED_SKILL"
rm -f "$AGENTS_INSTALL_ROOT/$LEGACY_AGENT.md"

log "Installing editable editorial visual style into: $EDITORIAL_CONFIG_ROOT"
mkdir -p "$EDITORIAL_CONFIG_ROOT"
install -m 0644 "$PACKAGE_EDITORIAL_CONFIG/visual-style.md" "$EDITORIAL_CONFIG_ROOT/visual-style.dist.md"
if [[ ! -f "$EDITORIAL_CONFIG_ROOT/visual-style.md" ]]; then
  install -m 0644 "$PACKAGE_EDITORIAL_CONFIG/visual-style.md" "$EDITORIAL_CONFIG_ROOT/visual-style.md"
fi

log "Installing package-owned session continuity files into: $SESSION_CONTINUITY_INSTALL_ROOT"
mkdir -p "$SESSION_CONTINUITY_INSTALL_ROOT/bin" "$SESSION_CONTINUITY_INSTALL_ROOT/tests"
install -m 0755 "$STAGED_SESSION_CONTINUITY/bin/session_state.py" \
  "$SESSION_CONTINUITY_INSTALL_ROOT/bin/session_state.py"
install -m 0755 "$STAGED_SESSION_CONTINUITY/tests/test_session_state.py" \
  "$SESSION_CONTINUITY_INSTALL_ROOT/tests/test_session_state.py"

log "Repairing stale session hook references and recovering the prior stop hook when available..."
python3 "$HOOK_REPAIR" --claude-root "$CLAUDE_ROOT"

cmp -s "$PACKAGE_SESSION_CONTINUITY/bin/session_state.py" \
  "$SESSION_CONTINUITY_INSTALL_ROOT/bin/session_state.py" \
  || fail "installed session continuity helper differs from the validated package"
cmp -s "$PACKAGE_SESSION_CONTINUITY/tests/test_session_state.py" \
  "$SESSION_CONTINUITY_INSTALL_ROOT/tests/test_session_state.py" \
  || fail "installed session continuity tests differ from the validated package"
python3 "$SESSION_CONTINUITY_INSTALL_ROOT/bin/session_state.py" --help >/dev/null

log "Removing generated packaging metadata from installed skill and agent roots..."
find "$INSTALL_ROOT" "$AGENTS_INSTALL_ROOT" -name '.DS_Store' -type f -delete 2>/dev/null || true
find "$INSTALL_ROOT" "$AGENTS_INSTALL_ROOT" -type d -name '__MACOSX' -prune -exec rm -rf {} + 2>/dev/null || true
find "$INSTALL_ROOT" "$AGENTS_INSTALL_ROOT" -type d -name '__pycache__' -prune -exec rm -rf {} + 2>/dev/null || true
find "$INSTALL_ROOT" "$AGENTS_INSTALL_ROOT" -name '*.pyc' -type f -delete 2>/dev/null || true

python3 "$VALIDATOR" \
  --skills-root "$INSTALL_ROOT" \
  --manifest "$MANIFEST" \
  --agents-root "$AGENTS_INSTALL_ROOT" \
  --agents-manifest "$AGENTS_MANIFEST" \
  --allow-extra

DOTFILES_CLONE="$TMP_ROOT/DotFiles"
log "Preparing an isolated DotFiles update from: $REMOTE_URL"
git clone --quiet --branch "$TARGET_BRANCH" --single-branch \
  "$REMOTE_URL" "$DOTFILES_CLONE"

git -C "$DOTFILES_CLONE" config user.name "$LOCAL_NAME"
git -C "$DOTFILES_CLONE" config user.email "$LOCAL_EMAIL"

UPDATE_BRANCH="chore/claude-skills-update-${TIMESTAMP}"
git -C "$DOTFILES_CLONE" checkout --quiet -b "$UPDATE_BRANCH"
mkdir -p "$DOTFILES_CLONE/$DOTFILES_SKILLS_REL" "$DOTFILES_CLONE/$DOTFILES_AGENTS_REL" \
  "$DOTFILES_CLONE/$DOTFILES_SESSION_CONTINUITY_REL/bin" \
  "$DOTFILES_CLONE/$DOTFILES_SESSION_CONTINUITY_REL/tests" \
  "$DOTFILES_CLONE/$DOTFILES_EDITORIAL_CONFIG_REL" \
  "$DOTFILES_CLONE/$DOTFILES_PACKAGE_TOOLS_REL"
install -m 0755 "$PACKAGE_SESSION_CONTINUITY/bin/session_state.py" \
  "$DOTFILES_CLONE/$DOTFILES_SESSION_CONTINUITY_REL/bin/session_state.py"
install -m 0755 "$PACKAGE_SESSION_CONTINUITY/tests/test_session_state.py" \
  "$DOTFILES_CLONE/$DOTFILES_SESSION_CONTINUITY_REL/tests/test_session_state.py"

install -m 0644 "$EDITORIAL_CONFIG_ROOT/visual-style.md" "$DOTFILES_CLONE/$DOTFILES_EDITORIAL_CONFIG_REL/visual-style.md"
install -m 0644 "$PACKAGE_EDITORIAL_CONFIG/visual-style.md" "$DOTFILES_CLONE/$DOTFILES_EDITORIAL_CONFIG_REL/visual-style.dist.md"
install -m 0755 "$SCRIPT_DIR/install.sh" "$DOTFILES_CLONE/$DOTFILES_PACKAGE_TOOLS_REL/install.sh"
install -m 0755 "$SCRIPT_DIR/uninstall.sh" "$DOTFILES_CLONE/$DOTFILES_PACKAGE_TOOLS_REL/uninstall.sh"
install -m 0755 "$SCRIPT_DIR/verify.sh" "$DOTFILES_CLONE/$DOTFILES_PACKAGE_TOOLS_REL/verify.sh"
install -m 0644 "$SCRIPT_DIR/VERSION" "$DOTFILES_CLONE/$DOTFILES_PACKAGE_TOOLS_REL/VERSION"


# Track a recovered stop hook without deleting any other continuity hooks.
if [[ -f "$SESSION_CONTINUITY_INSTALL_ROOT/hooks/stop_notify.py" ]]; then
  mkdir -p "$DOTFILES_CLONE/$DOTFILES_SESSION_CONTINUITY_REL/hooks"
  cp -p "$SESSION_CONTINUITY_INSTALL_ROOT/hooks/stop_notify.py" \
    "$DOTFILES_CLONE/$DOTFILES_SESSION_CONTINUITY_REL/hooks/stop_notify.py"
fi

# Remove only the unwanted clear auto-handoff hook and any irrecoverably stale
# stop-hook reference from the tracked global Claude settings.
python3 "$HOOK_REPAIR" --claude-root "$DOTFILES_CLONE/global-claude"

while IFS= read -r skill; do
  [[ -n "$skill" ]] || continue
  mkdir -p "$DOTFILES_CLONE/$DOTFILES_SKILLS_REL/$skill"
  rsync -a --delete --exclude '.DS_Store' \
    "$PACKAGE_SKILLS/$skill/" \
    "$DOTFILES_CLONE/$DOTFILES_SKILLS_REL/$skill/"
done < "$MANIFEST"

while IFS= read -r agent; do
  [[ -n "$agent" ]] || continue
  cp -p "$PACKAGE_AGENTS/$agent.md" "$DOTFILES_CLONE/$DOTFILES_AGENTS_REL/$agent.md"
done < "$AGENTS_MANIFEST"

rm -rf "$DOTFILES_CLONE/$DOTFILES_SKILLS_REL/no-mistakes" \
  "$DOTFILES_CLONE/$DOTFILES_SKILLS_REL/$LEGACY_SKILL" \
  "$DOTFILES_CLONE/$DOTFILES_SKILLS_REL/$RETIRED_SKILL"
rm -f "$DOTFILES_CLONE/$DOTFILES_AGENTS_REL/$LEGACY_AGENT.md"
find "$DOTFILES_CLONE/$DOTFILES_SKILLS_REL" -name '.DS_Store' -delete
find "$DOTFILES_CLONE" -type d -name '__MACOSX' -prune -exec rm -rf {} + \
  2>/dev/null || true

python3 "$VALIDATOR" \
  --skills-root "$DOTFILES_CLONE/$DOTFILES_SKILLS_REL" \
  --manifest "$MANIFEST" \
  --agents-root "$DOTFILES_CLONE/$DOTFILES_AGENTS_REL" \
  --agents-manifest "$AGENTS_MANIFEST" \
  --allow-extra

cmp -s "$EDITORIAL_CONFIG_ROOT/visual-style.md" "$DOTFILES_CLONE/$DOTFILES_EDITORIAL_CONFIG_REL/visual-style.md" \
  || fail "DotFiles editorial visual style differs from installed configuration"

DOTFILES_UPDATE_PATHS=(
  "$DOTFILES_SKILLS_REL"
  "$DOTFILES_AGENTS_REL"
  "$DOTFILES_SESSION_CONTINUITY_REL"
  "$DOTFILES_EDITORIAL_CONFIG_REL"
  "$DOTFILES_PACKAGE_TOOLS_REL"
)
for settings_rel in "$DOTFILES_SETTINGS_REL" "$DOTFILES_SETTINGS_LOCAL_REL"; do
  if [[ -e "$DOTFILES_CLONE/$settings_rel" ]] || \
     git -C "$DOTFILES_CLONE" ls-files --error-unmatch -- "$settings_rel" >/dev/null 2>&1; then
    DOTFILES_UPDATE_PATHS+=("$settings_rel")
  fi
done

if [[ -z "$(git -C "$DOTFILES_CLONE" status --porcelain -- "${DOTFILES_UPDATE_PATHS[@]}")" ]]; then
  log "DotFiles already contains the requested skill state; no commit was needed."
else
  git -C "$DOTFILES_CLONE" add -A -- "${DOTFILES_UPDATE_PATHS[@]}"
  git -C "$DOTFILES_CLONE" commit --quiet -m "chore: update global Claude skills and agents"
  UPDATE_COMMIT="$(git -C "$DOTFILES_CLONE" rev-parse HEAD)"

  git -C "$DOTFILES_CLONE" checkout --quiet "$TARGET_BRANCH"
  git -C "$DOTFILES_CLONE" fetch --quiet origin "$TARGET_BRANCH"
  git -C "$DOTFILES_CLONE" merge --ff-only "origin/$TARGET_BRANCH" >/dev/null
  git -C "$DOTFILES_CLONE" merge --quiet --no-ff "$UPDATE_BRANCH" \
    -m "chore: merge global Claude skills and agents update"
  MERGE_COMMIT="$(git -C "$DOTFILES_CLONE" rev-parse HEAD)"
  git -C "$DOTFILES_CLONE" push origin "HEAD:$TARGET_BRANCH"

  log "DotFiles update commit: $UPDATE_COMMIT"
  log "DotFiles $TARGET_BRANCH merge commit: $MERGE_COMMIT"
fi

# Keep the user's primary checkout current only when doing so is provably safe.
PRIMARY_BRANCH="$(git -C "$DOTFILES_REPO" branch --show-current || true)"
PRIMARY_STATUS="$(git -C "$DOTFILES_REPO" status --porcelain || true)"
if [[ "$PRIMARY_BRANCH" == "$TARGET_BRANCH" && -z "$PRIMARY_STATUS" ]]; then
  git -C "$DOTFILES_REPO" fetch --quiet origin "$TARGET_BRANCH"
  if git -C "$DOTFILES_REPO" merge --ff-only "origin/$TARGET_BRANCH" >/dev/null 2>&1; then
    log "Updated the primary DotFiles checkout to origin/$TARGET_BRANCH."
  else
    log "WARNING: remote $TARGET_BRANCH was updated, but the primary DotFiles checkout could not fast-forward safely." >&2
  fi
else
  log "Primary DotFiles checkout was left untouched because it is dirty or not on $TARGET_BRANCH."
  log "The committed skills are available on origin/$TARGET_BRANCH."
fi

log ""
log "Installation complete."
log "Installed skills: $(tr '\n' ' ' < "$MANIFEST" | sed 's/[[:space:]]*$//')"
log "Installed session continuity helper: $SESSION_CONTINUITY_INSTALL_ROOT/bin/session_state.py"
log "Editorial visual style: $EDITORIAL_CONFIG_ROOT/visual-style.md"
log "ai-image runtime/configuration: externally managed and untouched by this package"
log "Preserved unrelated session-continuity hooks and removed the stale clear auto-handoff hook reference."
log "Installed agents: $(tr '\n' ' ' < "$AGENTS_MANIFEST" | sed 's/[[:space:]]*$//')"
log "Removed skills: no-mistakes $LEGACY_SKILL $RETIRED_SKILL"
log "Removed legacy agent: $LEGACY_AGENT"
log "DotFiles branch: $TARGET_BRANCH"
log "Backup: $BACKUP_ROOT"
