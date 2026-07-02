#!/usr/bin/env bash
# Encrypt every .html file in the built Jekyll site with StatiCrypt.
#
# Usage:
#   STATICRYPT_PASSWORD='your-password' bash scripts/encrypt.sh [site-dir]
#
# Defaults: site-dir = _site
#
# What this script does:
#   1. Removes feed.xml / sitemap.xml / robots.txt (they would leak
#      content around the password gate).
#   2. Runs StatiCrypt on each .html file individually, into a per-file
#      temp directory, then moves the encrypted version back over the
#      original. Per-file processing avoids basename collisions (Jekyll
#      generates many files all called `index.html`).
#   3. Verifies every HTML now contains the StatiCrypt marker — if any
#      file is unencrypted the script aborts so we never deploy a
#      half-protected site.
#
# Why every page? Privacy. With `--remember 30`, visitors only enter
# the password ONCE per browser; after that the decryption key is
# stored in localStorage for 30 days and every page auto-decrypts on
# load. So this gives single-sign-in UX with proper protection on
# every URL — direct links to inner pages also require auth.

set -euo pipefail

SITE_DIR="${1:-_site}"
PASSWORD="${STATICRYPT_PASSWORD:-}"

# ─── Login screen styling ─────────────────────────────────────────
TEMPLATE_TITLE="Welcome — please sign in"
TEMPLATE_INSTRUCTIONS='The concatenated name abbreviation of some celebrates.<br><small style="font-size:0.8em;opacity:0.8;">Hints: dy&lt;date_together&gt;。</small>'
TEMPLATE_BUTTON="Enter"
# Romantic purple palette
TEMPLATE_COLOR_PRIMARY="#9b59b6"
TEMPLATE_COLOR_SECONDARY="#f7f1fb"

if [[ -z "$PASSWORD" ]]; then
  echo "ERROR: STATICRYPT_PASSWORD env var is empty." >&2
  echo "Run again like:  STATICRYPT_PASSWORD='your-password' bash scripts/encrypt.sh" >&2
  exit 1
fi

if [[ ! -d "$SITE_DIR" ]]; then
  echo "ERROR: $SITE_DIR does not exist. Did you run 'bundle exec jekyll build' first?" >&2
  exit 1
fi

echo "→ Stripping feed/sitemap so they don't bypass the password..."
rm -f "$SITE_DIR/feed.xml" "$SITE_DIR/sitemap.xml" "$SITE_DIR/robots.txt"

# Collect every HTML file under the site dir.
HTML_FILES=()
while IFS= read -r -d '' f; do HTML_FILES+=("$f"); done \
  < <(find "$SITE_DIR" -type f -name '*.html' -print0)

if [[ ${#HTML_FILES[@]} -eq 0 ]]; then
  echo "ERROR: no .html files found under $SITE_DIR" >&2
  exit 1
fi

TOTAL=${#HTML_FILES[@]}
echo "→ Encrypting $TOTAL HTML files (this takes ~1s per file)..."

# Per-file scratch root so we can clean up reliably.
SCRATCH="$(mktemp -d)"
trap 'rm -rf "$SCRATCH"' EXIT

i=0
for html in "${HTML_FILES[@]}"; do
  i=$((i + 1))
  out_dir="$SCRATCH/$i"
  mkdir -p "$out_dir"

  # Run StatiCrypt on this single file. With --directory pointing to a
  # fresh empty dir, the encrypted output lands at <out_dir>/<basename>.
  npx --no-install staticrypt "$html" \
    --password "$PASSWORD" \
    --directory "$out_dir" \
    --short \
    --remember 30 \
    --template-title "$TEMPLATE_TITLE" \
    --template-instructions "$TEMPLATE_INSTRUCTIONS" \
    --template-button "$TEMPLATE_BUTTON" \
    --template-color-primary "$TEMPLATE_COLOR_PRIMARY" \
    --template-color-secondary "$TEMPLATE_COLOR_SECONDARY" \
    >/dev/null

  base="$(basename "$html")"
  encrypted="$out_dir/$base"

  if [[ ! -f "$encrypted" ]]; then
    # Fallback: maybe StatiCrypt placed it under a nested path.
    encrypted="$(find "$out_dir" -type f -name "$base" | head -n1)"
  fi

  if [[ -z "${encrypted:-}" || ! -f "$encrypted" ]]; then
    echo "ERROR: StatiCrypt did not produce an encrypted version of $html" >&2
    echo "Contents of $out_dir:" >&2
    ls -laR "$out_dir" >&2
    exit 1
  fi

  mv -f "$encrypted" "$html"

  # Light progress indicator every 10 files.
  if (( i % 10 == 0 )) || (( i == TOTAL )); then
    echo "  …$i / $TOTAL"
  fi
done

# Final verification: every HTML must contain the StatiCrypt marker.
echo "→ Verifying every HTML is actually encrypted..."
UNENCRYPTED=0
for html in "${HTML_FILES[@]}"; do
  if ! grep -q 'staticrypt' "$html"; then
    echo "ERROR: $html does not look encrypted (no staticrypt marker)." >&2
    UNENCRYPTED=$((UNENCRYPTED + 1))
  fi
done

if [[ $UNENCRYPTED -gt 0 ]]; then
  echo "ERROR: $UNENCRYPTED file(s) were not encrypted. Refusing to deploy." >&2
  exit 1
fi

echo "✓ Done. $TOTAL HTML files in $SITE_DIR encrypted and verified."
echo "  Visitors will enter the password ONCE; --remember 30 keeps them"
echo "  signed in for 30 days so other pages auto-decrypt."
