import sys
from pathlib import Path

ps1_path = Path(__file__).parent / "start.ps1"
content = ps1_path.read_text(encoding="utf-8")

old = """# ── 6. 启动后端（新窗口）─────────────────────────────────────────────────────
Write-Step "启动 FastAPI 后端 → http://localhost:8001"
$backendArgs = @(
    "-NoExit", "-Command",
    "cd '$Root'; " +
    "Write-Host '  [后端] 寻味地理 API' -ForegroundColor Cyan; " +
    "Write-Host '  [后端] 首次启动需解压底图，请稍候...' -ForegroundColor Yellow; " +
    "& '$pyExe' -m uvicorn backend.main:app --host 127.0.0.1 --port 8001 --reload"
)
Start-Process powershell -ArgumentList $backendArgs"""

new = """# ── 6. 启动后端（新窗口）─────────────────────────────────────────────────────
Write-Step "启动 FastAPI 后端 → http://localhost:8001"
$backendArgs = @(
    "-NoExit", "-Command",
    "cd '$Root'; " +
    "Write-Host '  [后端] 寻味地理 API' -ForegroundColor Cyan; " +
    "Write-Host '  [后端] 首次启动需解压底图，请稍候...' -ForegroundColor Yellow; " +
    "& '$pyExe' run_server.py"
)
Start-Process powershell -ArgumentList $backendArgs"""

content = content.replace(old, new)
ps1_path.write_text(content, encoding="utf-8")
print("Done")
