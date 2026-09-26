$ErrorActionPreference = "Stop"
$Python = if (Get-Command python3 -ErrorAction SilentlyContinue) { "python3" } else { "python" }
& $Python (Join-Path $PSScriptRoot "configure-user-settings.py") --mode freeze
if ($LASTEXITCODE -ne 0) { throw "Failed to freeze global AutoHarness writes." }
Write-Host "New global AutoHarness writes are frozen; project learning and existing recall remain available."
