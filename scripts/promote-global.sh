#!/usr/bin/env bash
set -euo pipefail
python3 "$(cd "$(dirname "$0")" && pwd)/configure-user-settings.py" --mode production
echo "AutoHarness WMS production profile enabled. Restart Claude Code or run /reload-plugins."
