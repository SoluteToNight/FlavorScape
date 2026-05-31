# 寻味地理 — 局域网启动脚本 (PowerShell)
# 用法：在 Food 目录右键 → 在终端中打开 → .\start-lan.ps1

# uv/npm 等外部命令会把状态信息写到 stderr，不能用 Stop 策略
$ErrorActionPreference = "Continue"
$Root = $PSScriptRoot

# ── 颜色输出 ──────────────────────────────────────────────────────────────────
function Write-Step($msg) { Write-Host "  $msg" -ForegroundColor Cyan }
function Write-Ok($msg)   { Write-Host "  ✓ $msg" -ForegroundColor Green }
function Write-Warn($msg) { Write-Host "  ⚠ $msg" -ForegroundColor Yellow }
function Write-Err($msg)  { Write-Host "  ✗ $msg" -ForegroundColor Red }

function Get-LanIPv4Addresses {
    $addresses = @()

    try {
        $addresses = Get-NetIPAddress -AddressFamily IPv4 -ErrorAction Stop |
            Where-Object {
                $_.IPAddress -notmatch '^(127\.|169\.254\.)' -and
                $_.IPAddress -ne '0.0.0.0' -and
                $_.InterfaceOperationalStatus -eq 'Up'
            } |
            Select-Object -ExpandProperty IPAddress -Unique
    } catch {
        $addresses = @()
    }

    if (-not $addresses -or $addresses.Count -eq 0) {
        $addresses = ipconfig 2>$null |
            Select-String 'IPv4.*?:\s*([0-9.]+)' |
            ForEach-Object { $_.Matches[0].Groups[1].Value } |
            Where-Object { $_ -notmatch '^(127\.|169\.254\.)' } |
            Select-Object -Unique
    }

    return @($addresses)
}

function Stop-PortListener($port) {
    $listeners = netstat -ano 2>$null |
        Select-String "LISTENING" |
        Where-Object { $_.Line -match "[:.]$port\s+" }

    $pids = @($listeners | ForEach-Object {
        ($_.Line.Trim() -split '\s+')[-1]
    } | Where-Object {
        $_ -match '^\d+$' -and $_ -ne '0'
    } | Select-Object -Unique)

    foreach ($pidText in $pids) {
        Stop-Process -Id ([int]$pidText) -Force -ErrorAction SilentlyContinue
        Write-Warn "已终止占用 $port 端口的旧进程 (PID $pidText)"
    }

    if ($pids.Count -gt 0) {
        Start-Sleep -Seconds 1
    }
}

Write-Host ""
Write-Host "  寻味地理 · 局域网启动中" -ForegroundColor White
Write-Host "  ─────────────────────────────────────────" -ForegroundColor DarkGray
Write-Host ""

$lanIps = Get-LanIPv4Addresses
if (-not $lanIps -or $lanIps.Count -eq 0) {
    Write-Warn "未检测到局域网 IPv4 地址，仍将以 0.0.0.0 启动服务"
}

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

# ── 5. 释放端口（如有旧进程占用则终止）──────────────────────────────────────
Stop-PortListener 8001
Stop-PortListener 5173

# ── 6. 启动后端（新窗口）─────────────────────────────────────────────────────
Write-Step "启动 FastAPI 后端（局域网）→ http://0.0.0.0:8001"
$backendArgs = @(
    "-NoExit", "-Command",
    "cd '$Root'; " +
    "Write-Host '  [后端] 寻味地理 API (LAN)' -ForegroundColor Cyan; " +
    "Write-Host '  [后端] 首次启动需解压底图，请稍候...' -ForegroundColor Yellow; " +
    "& '$pyExe' -m uvicorn backend.main:app --host 0.0.0.0 --port 8001 --reload"
)
Start-Process powershell -ArgumentList $backendArgs

# ── 7. 等待后端就绪 ───────────────────────────────────────────────────────────
Write-Step "等待后端就绪..."
$maxWait = 300
$waited  = 0
$ready   = $false
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

# ── 8. 启动前端（新窗口）─────────────────────────────────────────────────────
Write-Step "启动 Vite 前端（局域网）→ http://0.0.0.0:5173"
$frontendArgs = @(
    "-NoExit", "-Command",
    "cd '$Root'; " +
    "Write-Host '  [前端] 寻味地理 Vite Dev (LAN)' -ForegroundColor Cyan; " +
    "npm run dev:lan"
)
Start-Process powershell -ArgumentList $frontendArgs

# ── 9. 完成并打印连接地址 ────────────────────────────────────────────────────
Write-Host ""
Write-Host "  ─────────────────────────────────────────" -ForegroundColor DarkGray
Write-Ok "服务已全部启动"
Write-Host ""
Write-Host "    本机前端  →  http://localhost:5173" -ForegroundColor White
Write-Host "    本机后端  →  http://localhost:8001" -ForegroundColor White
Write-Host "    本机 API   →  http://localhost:8001/docs" -ForegroundColor White

if ($lanIps -and $lanIps.Count -gt 0) {
    Write-Host ""
    foreach ($ip in $lanIps) {
        Write-Host "    局域网前端 →  http://${ip}:5173" -ForegroundColor Green
        Write-Host "    局域网后端 →  http://${ip}:8001" -ForegroundColor DarkGray
        Write-Host "    局域网 API  →  http://${ip}:8001/docs" -ForegroundColor DarkGray
    }
} else {
    Write-Host ""
    Write-Host "    局域网前端 →  http://<本机局域网IP>:5173" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "  同一局域网设备请访问上面的“局域网前端”地址" -ForegroundColor DarkGray
Write-Host "  若无法连接，请检查 Windows 防火墙是否放行 Node.js/Python 或 5173/8001 端口" -ForegroundColor DarkGray
Write-Host "  关闭两个子窗口即可停止所有服务" -ForegroundColor DarkGray
Write-Host ""
