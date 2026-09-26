$ErrorActionPreference = "Stop"
& claude plugin uninstall autoharness@autoharness-wms --scope user
if ($LASTEXITCODE -ne 0) { throw "Plugin uninstall failed." }
Write-Host "AutoHarness WMS uninstalled. Learned skills and state were intentionally retained."
Write-Host "Optional marketplace removal: claude plugin marketplace remove autoharness-wms"
