# EQMOD Windows Setup Script (PowerShell)
# Usage: .\setup_windows.ps1 -BundlePath <path-to-eqmod_transfer.tar.gz>

param(
    [string]$BundlePath = "$env:USERPROFILE\Downloads\eqmod_transfer.tar.gz",
    [string]$RepoDir   = "$env:USERPROFILE\Documents\EQMOD",
    [switch]$SkipGitClone,
    [switch]$SkipBundle,
    [switch]$SkipVenv
)

$ErrorActionPreference = "Stop"
Write-Host "EQMOD Windows setup starting..." -ForegroundColor Cyan

# 1. Git clone
if (-not $SkipGitClone) {
    if (Test-Path $RepoDir) {
        Write-Host "Repo dir exists, pulling latest..." -ForegroundColor Yellow
        Set-Location $RepoDir
        git pull origin main
    } else {
        Write-Host "Cloning repo..." -ForegroundColor Yellow
        git clone https://github.com/mkupermann/vibrasim.git $RepoDir
        Set-Location $RepoDir
    }
} else {
    Set-Location $RepoDir
}

# 2. Unpack data bundle into ~/.eqmod/
if (-not $SkipBundle) {
    if (-not (Test-Path $BundlePath)) {
        Write-Host "Bundle not found at $BundlePath — skipping unpack." -ForegroundColor Red
        Write-Host "Re-run with -BundlePath <path-to-eqmod_transfer.tar.gz> after transferring." -ForegroundColor Red
    } else {
        $eqmodHome = "$env:USERPROFILE\.eqmod"
        Write-Host "Unpacking $BundlePath to $env:USERPROFILE..." -ForegroundColor Yellow
        tar -xzf $BundlePath -C $env:USERPROFILE
        Write-Host "Bundle unpacked." -ForegroundColor Green

        # 3. Path-patch manifest from Mac paths to Windows paths
        $manifestPath = "$eqmodHome\training\EN\manifest.json"
        if (Test-Path $manifestPath) {
            Write-Host "Patching manifest paths..." -ForegroundColor Yellow
            python -c @"
import json, pathlib
p = pathlib.Path(r'$manifestPath')
m = json.loads(p.read_text())
home_str = str(pathlib.Path.home()).replace('\\', '/')
for s in m['stages'].values():
    for f in s.get('files', []):
        old = f['path']
        # Replace Mac home with Windows home (forward slash form)
        f['path'] = old.replace('/Users/mkupermann', home_str)
p.write_text(json.dumps(m, indent=2))
print('Manifest patched.')
"@
        }
    }
}

# 4. Python venv + dependencies
if (-not $SkipVenv) {
    if (-not (Test-Path "$RepoDir\.venv")) {
        Write-Host "Creating Python venv..." -ForegroundColor Yellow
        python -m venv .venv
    }
    & "$RepoDir\.venv\Scripts\Activate.ps1"
    Write-Host "Installing dependencies (this can take 5-10 min)..." -ForegroundColor Yellow
    pip install --upgrade pip
    pip install brian2 numpy pytest
    # Optional but recommended for GPU:
    Write-Host ""
    Write-Host "If you have NVIDIA GPU, run additionally:" -ForegroundColor Cyan
    Write-Host "  pip install brian2cuda" -ForegroundColor Cyan
    Write-Host "  (requires CUDA toolkit installed system-wide)" -ForegroundColor Cyan
}

# 5. Sanity check
Write-Host ""
Write-Host "Running sanity test (BET-078 checkpoint/resume)..." -ForegroundColor Yellow
pytest tests/bet/test_bet_078_checkpoint_resume.py -xvs

Write-Host ""
Write-Host "Setup complete." -ForegroundColor Green
Write-Host "Next: read HANDOFF.md, then ask Claude-on-Windows to design BET-081." -ForegroundColor Cyan
Write-Host ""
Write-Host "If you need Telegram heartbeats: copy notify_config.json from Mac to" -ForegroundColor Yellow
Write-Host "  $env:USERPROFILE\.eqmod\autopilot\notify_config.json" -ForegroundColor Yellow
Write-Host "(file mode 0600, sensitive — do not commit)" -ForegroundColor Yellow
