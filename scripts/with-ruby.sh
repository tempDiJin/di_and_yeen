#!/usr/bin/env bash
# Wrapper that puts Homebrew's Ruby on PATH before exec'ing a command.
# Usage:  bash scripts/with-ruby.sh <command> [args...]
#
# Why: macOS still ships Ruby 2.6, and if it ends up earlier on PATH
# than Homebrew's Ruby, bundle/jekyll will fail in confusing ways.
# This script forces Homebrew Ruby to win for any command it wraps.

set -euo pipefail

# Find Homebrew (Apple Silicon vs Intel locations).
BREW_BIN=""
if command -v brew >/dev/null 2>&1; then
  BREW_BIN="$(command -v brew)"
elif [[ -x /opt/homebrew/bin/brew ]]; then
  BREW_BIN="/opt/homebrew/bin/brew"
elif [[ -x /usr/local/bin/brew ]]; then
  BREW_BIN="/usr/local/bin/brew"
fi

if [[ -n "$BREW_BIN" ]]; then
  RUBY_PREFIX="$("$BREW_BIN" --prefix ruby 2>/dev/null || true)"
  if [[ -n "$RUBY_PREFIX" && -x "$RUBY_PREFIX/bin/ruby" ]]; then
    export PATH="$RUBY_PREFIX/bin:$PATH"
    # Also expose user-installed gem binaries (`gem install --user-install`)
    if RUBY_USER_DIR="$("$RUBY_PREFIX/bin/ruby" -e 'require "rubygems"; print Gem.user_dir' 2>/dev/null)"; then
      export PATH="$RUBY_USER_DIR/bin:$PATH"
    fi
  fi
fi

# CI (GitHub Actions) sets up Ruby itself — brew may not exist there,
# in which case we just fall through with whatever PATH we got. That's fine.

exec "$@"
