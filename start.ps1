# FlavorScape one-shot startup script for Windows PowerShell.
# Run from the repository root:
#   .\start.ps1

$ErrorActionPreference = "Continue"
$Root = $PSScriptRoot

function Write-Step($msg) { Write-Host "  $msg" -ForegroundColor Cyan }
function Write-Ok($msg)   { Write-Host "  OK  $msg" -ForegroundColor Green }
function Write-Warn($msg) { Write-Host "  WARN $msg" -ForegroundColor Yellow }
function Write-Err($msg)  { Write-Host "  ERR $msg" -ForegroundColor Red }

function Quote-ForPowerShell($value) {
    return "'" + ($value -replace "'", "''") + "'"
}

Write-Host ""
Write-Host "  FlavorScape startup" -ForegroundColor White
Write-Host "  ----------------------------------------" -ForegroundColor DarkGray
Write-Host ""

# 1. Check uv.
Write-Step "Checking uv..."
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Err "uv was not found. Install it first: https://docs.astral.sh/uv/getting-started/installation/"
    exit 1
}
Write-Ok "$(uv --version)"

# 2. Create or reuse the Python virtual environment.
$venv = Join-Path $Root ".venv"
$pyExe = Join-Path $venv "Scripts\python.exe"
if (-not (Test-Path $pyExe)) {
    Write-Step "Creating Python virtual environment in .venv..."
    uv venv $venv --python 3.12
    if ($LASTEXITCODE -ne 0) {
        Write-Err "Failed to create .venv with Python 3.12."
        exit $LASTEXITCODE
    }
    Write-Ok "Virtual environment created"
} else {
    Write-Ok "Virtual environment already exists"
}

# 3. Install or sync Python dependencies.
Write-Step "Syncing Python dependencies..."
uv pip install --python $pyExe --quiet -r "$Root\backend\requirements.txt"
if ($LASTEXITCODE -eq 0) {
    Write-Ok "Python dependencies are ready"
} else {
    Write-Warn "Dependency install returned exit code $LASTEXITCODE; continuing startup."
}

# 4. Check Node.js dependencies.
Write-Step "Checking frontend dependencies..."
$npmCmdInfo = Get-Command npm.cmd -ErrorAction SilentlyContinue
if (-not $npmCmdInfo) {
    Write-Err "npm was not found. Install Node.js first."
    exit 1
}
$npmCmd = $npmCmdInfo.Source
if (-not (Test-Path (Join-Path $Root "node_modules"))) {
    Write-Step "Installing npm dependencies..."
    Push-Location $Root
    & $npmCmd install --silent
    $npmInstallExitCode = $LASTEXITCODE
    Pop-Location
    if ($npmInstallExitCode -ne 0) {
        Write-Err "npm install failed with exit code $npmInstallExitCode."
        exit $npmInstallExitCode
    }
}
Write-Ok "Frontend dependencies are ready"

# 5. Free port 8001 if an old backend is still listening.
Write-Step "Checking port 8001..."
$portLines = netstat -ano 2>$null | Select-String -Pattern 'LISTENING' | Select-String -Pattern '(:8001\s+)'
$oldPids = @()
if ($portLines) {
    $oldPids = $portLines | ForEach-Object {
        ($_.Line.Trim() -split '\s+')[-1]
    } | Where-Object {
        $_ -match '^\d+$'
    } | Sort-Object -Unique
}

foreach ($oldPid in $oldPids) {
    try {
        Stop-Process -Id ([int]$oldPid) -Force -ErrorAction Stop
        Write-Warn "Stopped old process on port 8001 (PID $oldPid)"
    } catch {
        Write-Warn "Could not stop process on port 8001 (PID $oldPid): $($_.Exception.Message)"
    }
}
if ($oldPids.Count -gt 0) {
    Start-Sleep -Seconds 1
}

# 6. Start the backend in a new PowerShell window.
Write-Step "Starting FastAPI backend at http://localhost:8001"
$quotedRoot = Quote-ForPowerShell $Root
$quotedPyExe = Quote-ForPowerShell $pyExe
$quotedNpmCmd = Quote-ForPowerShell $npmCmd
$serverScript = Join-Path $Root "run_server.py"
if (Test-Path $serverScript) {
    $quotedServerScript = Quote-ForPowerShell $serverScript
    $backendRunCommand = "& $quotedPyExe $quotedServerScript"
} else {
    $backendRunCommand = "& $quotedPyExe -m uvicorn backend.main:app --host 127.0.0.1 --port 8001 --reload"
}
$backendCommand = "Set-Location -LiteralPath $quotedRoot; " +
    "Write-Host '  [backend] FlavorScape API' -ForegroundColor Cyan; " +
    "Write-Host '  [backend] First start can take several minutes while map data loads.' -ForegroundColor Yellow; " +
    $backendRunCommand
$backendArgs = @(
    "-NoExit",
    "-NoProfile",
    "-ExecutionPolicy", "Bypass",
    "-Command", $backendCommand
)
Start-Process powershell.exe -ArgumentList $backendArgs

# 7. Wait for backend readiness.
Write-Step "Waiting for backend /health..."
$maxWait = 300
$waited = 0
$ready = $false
$json = $null

while ($waited -lt $maxWait) {
    Start-Sleep -Seconds 3
    $waited += 3

    try {
        $resp = Invoke-WebRequest -Uri "http://localhost:8001/health" -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop
        $json = $resp.Content | ConvertFrom-Json
        if ($json.status -eq "ok") {
            $ready = $true
            break
        }
    } catch {
        # Backend startup can block while raster/vector data loads.
    }

    if ($waited % 15 -eq 0) {
        Write-Step "Still waiting after ${waited}s..."
    }
}

if ($ready) {
    $layers = ""
    if ($json.vector_layers) {
        $layers = $json.vector_layers -join ", "
    }
    Write-Ok "Backend is ready (layers: $layers)"
} else {
    Write-Warn "Backend did not answer within ${maxWait}s; starting frontend anyway."
}

# 8. Start the frontend in a new PowerShell window.
Write-Step "Starting Vite frontend at http://localhost:5173"
$frontendCommand = "Set-Location -LiteralPath $quotedRoot; " +
    "Write-Host '  [frontend] FlavorScape Vite Dev' -ForegroundColor Cyan; " +
    "& $quotedNpmCmd run dev"
$frontendArgs = @(
    "-NoExit",
    "-NoProfile",
    "-ExecutionPolicy", "Bypass",
    "-Command", $frontendCommand
)
Start-Process powershell.exe -ArgumentList $frontendArgs

# 9. Done.
Write-Host ""
Write-Host "  ----------------------------------------" -ForegroundColor DarkGray
Write-Ok "Startup sequence completed"
Write-Host ""
Write-Host "    Frontend: http://localhost:5173" -ForegroundColor White
Write-Host "    Backend:  http://localhost:8001" -ForegroundColor White
Write-Host "    API docs: http://localhost:8001/docs" -ForegroundColor White
Write-Host ""
Write-Host "  Close the backend and frontend PowerShell windows to stop the services." -ForegroundColor DarkGray
Write-Host ""
