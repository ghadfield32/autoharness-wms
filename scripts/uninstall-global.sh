#!/usr/bin/env bash
set -euo pipefail
claude plugin uninstall autoharness@autoharness-wms --scope user
echo "AutoHarness WMS uninstalled. Learned skills and state were intentionally retained."
echo "Optional marketplace removal: claude plugin marketplace remove autoharness-wms"
