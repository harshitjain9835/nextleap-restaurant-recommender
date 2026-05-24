# Install Python dependencies for the restaurant recommendation project.
# Requires Python 3.12+ (install: winget install Python.Python.3.12)

$ErrorActionPreference = "Stop"

# Refresh PATH so newly installed Python is visible in this session
$env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" +
            [System.Environment]::GetEnvironmentVariable("Path", "User")

if (-not (Get-Command py -ErrorAction SilentlyContinue)) {
    Write-Host "Python launcher 'py' not found. Install with:" -ForegroundColor Red
    Write-Host "  winget install Python.Python.3.12 --accept-package-agreements --accept-source-agreements"
    exit 1
}

$version = & py --version 2>&1
Write-Host "Using $version"

$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $root

& py -m pip install --upgrade pip
if (Test-Path "requirements.txt") {
    & py -m pip install -r requirements.txt
} else {
    Write-Host "requirements.txt not found yet; skipping package install."
}

Write-Host ""
Write-Host "Verify:" -ForegroundColor Green
& py -c "import sys; print('Python OK:', sys.executable)"

Write-Host ""
Write-Host "Tip: Use 'py' instead of 'python' if you see the Microsoft Store stub error."
Write-Host "Optional: Settings > Apps > Advanced app settings > App execution aliases"
Write-Host "         Turn OFF python.exe and python3.exe aliases."
