# 寻味地理 — 一键启动脚本 (PowerShell)
# 用法：在 Food 目录右键 → 在终端中打开 → .\start.ps1

# uv/npm 等外部命令会把状态信息写到 stderr，不能用 Stop 策略
$ErrorActionPreference = "Continue"
$Root = $PSScriptRoot

# ── 颜色输出 ──────────────────────────────────────────────────────────────────
function Write-Step($msg) { Write-Host "  $msg" -ForegroundColor Cyan }
function Write-Ok($msg)   { Write-Host "  ✓ $msg" -ForegroundColor Green }
function Write-Warn($msg) { Write-Host "  ⚠ $msg" -ForegroundColor Yellow }
function Write-Err($msg)  { Write-Host "  ✗ $msg" -ForegroundColor Red }

Write-Host ""
Write-Host "  寻味地理 · 启动中" -ForegroundColor White
Write-Host "  ─────────────────────────────────────────" -ForegroundColor DarkGray
Write-Host ""

# ── 1. 检查 uv ────────────────────────────────────────────────────────────────
Write-Step "检查 uv..."
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Err "未找到 uv，请先安装：https://docs.astral.sh/uv/getting-started/installation/"
    exit 1
}
Write-Ok "uv $(uv --version)"

# ── 2. 创建/更新 Python 虚拟环境 ─────────────────────────────────────────────
$venv = Join-Path $Root ".venv"
if (-not (Test-Path $venv)) {
    Write-Step "创建 Python 虚拟环境（.venv）..."
    uv venv $venv --python 3.12 2>$null | Out-Null
    Write-Ok "虚拟环境已创建"
} else {
    Write-Ok "虚拟环境已存在"
}

# ── 3. 安装/同步 Python 依赖 ──────────────────────────────────────────────────
$pyExe = Join-Path $venv "Scripts\python.exe"
Write-Step "同步 Python 依赖..."
# --quiet 抑制 "Audited N packages" 等 uv 状态输出；2>$null 丢弃 stderr
uv pip install --python $pyExe --quiet -r "$Root\backend\requirements.txt" 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Ok "Python 依赖已就绪"
} else {
    Write-Warn "依赖安装返回非零退出码 ($LASTEXITCODE)，尝试继续..."
}

# ── 4. 检查 Node.js 依赖 ──────────────────────────────────────────────────────
Write-Step "检查前端依赖..."
if (-not (Test-Path (Join-Path $Root "node_modules"))) {
    Write-Step "安装 npm 依赖..."
    Push-Location $Root
    npm install --silent 2>&1 | Out-Null
    Pop-Location
}
Write-Ok "前端依赖已就绪"

# ── 5. 释放 8001 端口（如有旧进程占用则终止）────────────────────────────────
# uvicorn --reload 在 Windows 上通过 multiprocessing.spawn 创建父子双进程，
# 父进程被杀后子进程可能成为孤儿继续占用端口，需用 /T 递归终止
Write-Step "检查 8001 端口..."
$tries = 0
do {
    $portInUse = netstat -ano 2>$null | Select-String '\s+0\.0\.0\.0:8001\s+|\s+127\.0\.0\.1:8001\s+' | Select-String 'LISTENING'
    if (-not $portInUse) { break }
    $oldPid = ($portInUse[0].Line.Trim() -split '\s+')[-1]
    if ($oldPid -match '^\d+$') {
        # taskkill /T 会同时终止该进程及其所有子进程（包括 uvicorn worker）
        taskkill /F /T /PID $oldPid 2>$null | Out-Null
        Start-Sleep -Seconds 2
        Write-Warn "已终止占用 8001 端口的旧进程 (PID $oldPid，含子进程)"
    }
    $tries++
} while ($tries -lt 3)

# ── 6. 启动后端（新窗口）─────────────────────────────────────────────────────
Write-Step "启动 FastAPI 后端 → http://localhost:8001"
$backendArgs = @(
    "-NoExit", "-Command",
    "cd '$Root'; " +
    "Write-Host '  [后端] 寻味地理 API' -ForegroundColor Cyan; " +
    "Write-Host '  [后端] 首次启动需解压底图，请稍候...' -ForegroundColor Yellow; " +
    "& '$pyExe' -m uvicorn backend.main:app --host 127.0.0.1 --port 8001 --reload"
)
Start-Process powershell -ArgumentList $backendArgs

# ── 7. 等待后端就绪 ───────────────────────────────────────────────────────────
Write-Step "等待后端就绪..."
$maxWait = 300   # 最多等 5 分钟（首次需解压 ~700MB TIF）
$waited  = 0
$ready   = $false
while ($waited -lt $maxWait) {
    Start-Sleep -Seconds 3
    $waited += 3
    try {
        $resp = Invoke-WebRequest -Uri "http://127.0.0.1:8001/health" -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop
        $json = $resp.Content | ConvertFrom-Json
        if ($json.status -eq "ok") {
            $ready = $true
            break
        }
    } catch {}
    if ($waited % 15 -eq 0) {
        Write-Step "  … 已等待 ${waited}s，底图数据加载中"
    }
}

if ($ready) {
    $layers = $json.vector_layers -join ", "
    Write-Ok "后端已就绪  (图层: $layers)"
} else {
    Write-Warn "后端在 ${maxWait}s 内未响应，前端将继续启动（后端可能还在加载）"
}

# ── 7. 启动前端（新窗口）─────────────────────────────────────────────────────
Write-Step "启动 Vite 前端 → http://localhost:5173"
$frontendArgs = @(
    "-NoExit", "-Command",
    "cd '$Root'; " +
    "Write-Host '  [前端] 寻味地理 Vite Dev' -ForegroundColor Cyan; " +
    "npm run dev"
)
Start-Process powershell -ArgumentList $frontendArgs

# ── 8. 完成 ──────────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "  ─────────────────────────────────────────" -ForegroundColor DarkGray
Write-Ok "服务已全部启动"
Write-Host ""
Write-Host "    前端  →  http://localhost:5173" -ForegroundColor White
Write-Host "    后端  →  http://localhost:8001" -ForegroundColor White
Write-Host "    API   →  http://localhost:8001/docs" -ForegroundColor White
Write-Host ""
Write-Host "  关闭两个子窗口即可停止所有服务" -ForegroundColor DarkGray
Write-Host ""
