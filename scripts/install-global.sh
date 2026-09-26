#!/usr/bin/env bash
set -euo pipefail

MARKETPLACE_SOURCE="ghadfield32/autoharness-wms"
MARKETPLACE_NAME="autoharness-wms"
PLUGIN_ID="autoharness@${MARKETPLACE_NAME}"
MIN_CLAUDE="2.1.259"

command -v claude >/dev/null || { echo "Claude Code is not on PATH." >&2; exit 1; }
command -v python3 >/dev/null || { echo "Python 3.11+ is required on PATH." >&2; exit 1; }

CLAUDE_VERSION="$(claude --version | grep -Eo '[0-9]+\.[0-9]+\.[0-9]+' | head -1)"
python3 - "$CLAUDE_VERSION" "$MIN_CLAUDE" <<'PY'
import sys
def v(s): return tuple(map(int, s.split(".")))
if v(sys.argv[1]) < v(sys.argv[2]):
    raise SystemExit(f"Claude Code {sys.argv[2]}+ required; found {sys.argv[1]}. Run: claude update")
PY

if claude plugin marketplace list 2>&1 | grep -q "$MARKETPLACE_NAME"; then
  claude plugin marketplace update "$MARKETPLACE_NAME"
else
  claude plugin marketplace add "$MARKETPLACE_SOURCE"
fi

if claude plugin list 2>&1 | grep -q "$PLUGIN_ID"; then
  claude plugin update "$PLUGIN_ID"
else
  claude plugin install "$PLUGIN_ID" --scope user
fi

python3 "$(cd "$(dirname "$0")" && pwd)/configure-user-settings.py" --mode probation

echo
echo "AutoHarness WMS installed at user scope across local Claude Code projects."
echo "Safe probation profile applied: automatic reflection paused and global skill writes frozen."
echo "Start a new session or run /reload-plugins. Use /autoharness:learn only after a verified lesson."
echo "Third-party marketplace auto-update stays off unless you explicitly enable it."
