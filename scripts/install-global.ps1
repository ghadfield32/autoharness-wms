$ErrorActionPreference = "Stop"

$MarketplaceSource = "ghadfield32/autoharness-wms"
$MarketplaceName = "autoharness-wms"
$PluginId = "autoharness@$MarketplaceName"
$MinimumClaude = [version]"2.1.259"

function Invoke-Claude {
    param([Parameter(ValueFromRemainingArguments=$true)][string[]]$Args)
    & claude @Args
    if ($LASTEXITCODE -ne 0) {
        throw "claude $($Args -join ' ') failed with exit code $LASTEXITCODE"
    }
}

if (-not (Get-Command claude -ErrorAction SilentlyContinue)) {
    throw "Claude Code is not on PATH."
}
if (-not (Get-Command python3 -ErrorAction SilentlyContinue) -and
    -not (Get-Command python -ErrorAction SilentlyContinue)) {
    throw "Python 3.11+ is required on PATH."
}

$versionText = (& claude --version | Out-String).Trim()
$match = [regex]::Match($versionText, '\d+\.\d+\.\d+')
if (-not $match.Success) { throw "Could not parse Claude Code version from: $versionText" }
$installedVersion = [version]$match.Value
if ($installedVersion -lt $MinimumClaude) {
    throw "Claude Code $MinimumClaude+ is required; found $installedVersion. Run: claude update"
}

$marketplaces = (& claude plugin marketplace list 2>&1 | Out-String)
if ($marketplaces -match [regex]::Escape($MarketplaceName)) {
    Invoke-Claude plugin marketplace update $MarketplaceName
} else {
    Invoke-Claude plugin marketplace add $MarketplaceSource
}

$plugins = (& claude plugin list 2>&1 | Out-String)
if ($plugins -match [regex]::Escape($PluginId)) {
    Invoke-Claude plugin update $PluginId
} else {
    Invoke-Claude plugin install $PluginId --scope user
}

Write-Host ""
Write-Host "AutoHarness WMS installed at user scope: enabled across local Claude Code projects." -ForegroundColor Green
Write-Host "Start a new session or run /reload-plugins. Use /autoharness:learn only after a lesson is verified."
Write-Host "Third-party marketplace auto-update stays off unless you explicitly enable it."
