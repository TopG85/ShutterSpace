#!/bin/bash
set -euo pipefail

PROJECT_DIR="/Users/danielcarson/Documents/Visual Studio Code Project/ShutterSpace/ShutterSpace"
TMPDIR=$(mktemp -d)
cd "$TMPDIR"

echo "Downloading Font Awesome v6.4.2..."
curl -L -o fa.zip "https://use.fontawesome.com/releases/v6.4.2/fontawesome-free-6.4.2-web.zip"

echo "Unzipping..."
unzip -q fa.zip

echo "Copying webfonts to project static/webfonts..."
mkdir -p "$PROJECT_DIR/static/webfonts"
cp -r fontawesome-free-6.4.2-web/webfonts/* "$PROJECT_DIR/static/webfonts/"

# Backup existing all.min.css if present
if [ -f "$PROJECT_DIR/static/css/all.min.css" ]; then
  echo "Backing up existing all.min.css -> all.min.css.bak"
  cp "$PROJECT_DIR/static/css/all.min.css" "$PROJECT_DIR/static/css/all.min.css.bak"
fi

# Copy the full CSS file into place
echo "Copying full all.min.css into static/css..."
mkdir -p "$PROJECT_DIR/static/css"
cp fontawesome-free-6.4.2-web/css/all.min.css "$PROJECT_DIR/static/css/all.min.css"

# Reapply rotate() fix for W3C validation (none -> 0deg)
echo "Applying rotate() fallback fix..."
# Try macOS sed in-place first, fall back to GNU sed if needed
if sed -i '' "s/rotate(var(--fa-rotate-angle, none))/rotate(var(--fa-rotate-angle, 0deg))/g" "$PROJECT_DIR/static/css/all.min.css" 2>/dev/null; then
  true
else
  sed -i "s/rotate(var(--fa-rotate-angle, none))/rotate(var(--fa-rotate-angle, 0deg))/g" "$PROJECT_DIR/static/css/all.min.css"
fi

# Cleanup
cd /
rm -rf "$TMPDIR"

# Stage and commit the new files (commit only if there are changes)
git add static/webfonts static/css/all.min.css || true
if git diff --staged --quiet; then
  echo "No changes to commit."
else
  git commit -m "chore: add Font Awesome webfonts and full CSS (6.4.2); reapply rotate() fix for W3C"
  git push || echo "git push failed; please run git push manually"
fi

echo "Done. Please hard-refresh your site (Cmd+Shift+R) and check icons."
