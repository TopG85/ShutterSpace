#!/usr/bin/env bash
# Helper: swap in Heroku-safe requirements, commit, and remind you to push
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
REQ="$ROOT_DIR/requirements.txt"
HEROKU_REQ="$ROOT_DIR/requirements.heroku.txt"

if [ ! -f "$HEROKU_REQ" ]; then
  echo "Missing $HEROKU_REQ"
  exit 1
fi

cp "$REQ" "$REQ.bak"
cp "$HEROKU_REQ" "$REQ"
git add "$REQ"
git commit -m "chore: use Heroku-safe requirements temporarily" || true
echo "requirements.txt replaced with requirements.heroku.txt (original saved as requirements.txt.bak)."
echo "Now run: git push heroku main && heroku run python manage.py migrate && heroku run python manage.py collectstatic --noinput"
