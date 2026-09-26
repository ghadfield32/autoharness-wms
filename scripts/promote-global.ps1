$ErrorActionPreference = "Stop"
$Python = if (Get-Command python3 -ErrorAction SilentlyContinue) { "python3" } else { "python" }
& $Python (Join-Path $PSScriptRoot "configure-user-settings.py") --mode production
if ($LASTEXITCODE -ne 0) { throw "Failed to promote AutoHarness WMS to production." }
Write-Host "AutoHarness WMS production profile enabled. Restart Claude Code or run /reload-plugins."
