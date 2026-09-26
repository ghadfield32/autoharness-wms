#!/usr/bin/env bash
set -euo pipefail
python3 "$(cd "$(dirname "$0")" && pwd)/configure-user-settings.py" --mode freeze
echo "New global AutoHarness writes are frozen; project learning and existing recall remain available."
