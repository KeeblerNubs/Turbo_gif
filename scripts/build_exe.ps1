$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    throw "Python was not found on PATH. Install Python 3.10+ for Windows first."
}

python -m venv .venv-build
& .\.venv-build\Scripts\python.exe -m pip install --upgrade pip
& .\.venv-build\Scripts\python.exe -m pip install -r requirements-build.txt

if (Test-Path .\build) { Remove-Item .\build -Recurse -Force }
if (Test-Path .\dist) { Remove-Item .\dist -Recurse -Force }

& .\.venv-build\Scripts\python.exe -m PyInstaller --clean --noconfirm .\TurboGifSpammer.spec

$ExePath = Join-Path $RepoRoot "dist\TurboGifSpammer.exe"
if (-not (Test-Path $ExePath)) {
    throw "Build completed without producing $ExePath"
}

Write-Host "Built $ExePath"
