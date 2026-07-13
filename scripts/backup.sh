#!/usr/bin/env bash

set -Eeuo pipefail

SOURCE="${HOME}/.claude"
REPO="${HOME}/git/DotFiles"
DEST="${REPO}/global-claude"

BACKUP_DIRECTORIES=(
  skills
  agents
  commands
  rules
)

BACKUP_FILES=(
  CLAUDE.md
  settings.json
)

die() {
  echo "ERROR: $*" >&2
  exit 1
}

command -v git >/dev/null 2>&1 || die "git is not installed."
command -v rsync >/dev/null 2>&1 || die "rsync is not installed."

[[ -d "$SOURCE" ]] || die "Claude configuration directory not found: $SOURCE"
[[ -d "$REPO/.git" ]] || die "Backup repository not found: $REPO"

mkdir -p "$DEST"

echo "Backing up Claude Code configuration..."

# Back up top-level Claude configuration files.
#
# If a previously backed-up file no longer exists in ~/.claude,
# remove it from the backup so the repository reflects the source.
for file in "${BACKUP_FILES[@]}"; do
  if [[ -f "$SOURCE/$file" ]]; then
    cp -p "$SOURCE/$file" "$DEST/$file"
  else
    rm -f "$DEST/$file"
  fi
done

# Back up reusable Claude customizations.
#
# rsync -a preserves:
# - nested directory structure
# - permissions
# - timestamps
# - symbolic links
#
# --delete ensures files removed from ~/.claude are also removed
# from the backup.
for directory in "${BACKUP_DIRECTORIES[@]}"; do
  source_directory="$SOURCE/$directory"
  destination_directory="$DEST/$directory"

  if [[ -d "$source_directory" ]]; then
    mkdir -p "$destination_directory"

    rsync -a --delete \
      --exclude='.DS_Store' \
      --exclude='*.tmp' \
      --exclude='*.swp' \
      "$source_directory/" \
      "$destination_directory/"
  else
    rm -rf "$destination_directory"
  fi
done

# Git does not track empty directories.
# Add .gitkeep files so an intentionally empty nested rules structure
# is retained in the remote repository.
if [[ -d "$DEST/rules" ]]; then
  while IFS= read -r -d '' directory; do
    touch "$directory/.gitkeep"
  done < <(
    find "$DEST/rules" \
      -type d \
      -empty \
      -print0
  )
fi

cd "$REPO"

# git diff does not include untracked files.
# git status --porcelain detects added, modified, renamed, and deleted files.
if [[ -z "$(git status --porcelain -- \
  global-claude \
  scripts \
  .gitignore \
  README.md)" ]]; then
  echo "No Claude Code configuration changes detected."
  exit 0
fi

git add -- \
  global-claude \
  scripts \
  .gitignore \
  README.md

# Defensive check after staging.
if git diff --cached --quiet; then
  echo "No staged Claude Code configuration changes detected."
  exit 0
fi

git commit \
  -m "Back up Claude Code configuration $(date '+%Y-%m-%d %H:%M:%S')"

git push

echo "Claude Code configuration and rule structure backed up successfully."
