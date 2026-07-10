#!/usr/bin/env bash

set -Eeuo pipefail

SOURCE="$HOME/.claude"
REPO="$HOME/git/DotFiles/"
DEST="$REPO/global-claude"

if [[ ! -d "$SOURCE" ]]; then
  echo "Claude configuration directory not found: $SOURCE"
  exit 1
fi

if [[ ! -d "$REPO/.git" ]]; then
  echo "Backup repository not found: $REPO"
  exit 1
fi

mkdir -p "$DEST"

# Global instruction file
if [[ -f "$SOURCE/CLAUDE.md" ]]; then
  cp "$SOURCE/CLAUDE.md" "$DEST/CLAUDE.md"
fi

# Main settings file. Review it for secrets before committing.
if [[ -f "$SOURCE/settings.json" ]]; then
  cp "$SOURCE/settings.json" "$DEST/settings.json"
fi

# Reusable Claude customizations
for directory in skills agents commands rules; do
  if [[ -d "$SOURCE/$directory" ]]; then
    rsync -a --delete \
      --exclude='.DS_Store' \
      "$SOURCE/$directory/" "$DEST/$directory/"
  else
    rm -rf "$DEST/$directory"
  fi
done

cd "$REPO"

if git diff --quiet && git diff --cached --quiet; then
  echo "No Claude configuration changes detected."
  exit 0
fi

git add global-claude scripts .gitignore README.md
git commit -m "Back up Claude Code configuration $(date '+%Y-%m-%d %H:%M:%S')"
git push

echo "Claude Code configuration backed up successfully."
