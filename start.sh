#!/usr/bin/env bash
# 寻味地理 — 一键启动脚本 (Bash / MSYS2 / Git Bash)
# 用法：bash start.sh
#
# 行为说明：后端作为后台进程运行（日志写入 .backend.log），
# 前端在前台运行。Ctrl+C 会自动清理后端进程。
# Windows 用户若需要独立窗口运行，请使用 start.ps1。

set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="$ROOT/.venv"
PY="$VENV/Scripts/python.exe"

RED='\033[0;31m' GRN='\033[0;32m' YLW='\033[0;33m' CYN='\033[0;36m' RST='\033[0m'
step() { echo -e "${CYN}  ▶ $*${RST}"; }
ok()   { echo -e "${GRN}  ✓ $*${RST}"; }
warn() { echo -e "${YLW}  ⚠ $*${RST}"; }
err()  { echo -e "${RED}  ✗ $*${RST}"; exit 1; }

echo ""
echo -e "  寻味地理 · 启动中"
echo "  ─────────────────────────────────────────"
echo ""

# 1. 检查 uv
step "检查 uv..."
command -v uv >/dev/null 2>&1 || err "未找到 uv，请安装：https://docs.astral.sh/uv/getting-started/installation/"
ok "uv $(uv --version)"

# 2. 创建虚拟环境
if [ ! -f "$PY" ]; then
    step "创建 Python 虚拟环境（.venv，Python 3.12）..."
    uv venv "$VENV" --python 3.12 >/dev/null 2>&1 || uv venv "$VENV" >/dev/null 2>&1
    ok "虚拟环境已创建"
else
    ok "虚拟环境已存在"
fi

# 3. 安装 Python 依赖
step "同步 Python 依赖..."
uv pip install --python "$PY" -r "$ROOT/backend/requirements.txt" --quiet \
    && ok "Python 依赖已就绪" \
    || warn "依赖安装有警告，尝试继续"

# 4. 检查 Node 依赖
step "检查前端依赖..."
[ -d "$ROOT/node_modules" ] || (cd "$ROOT" && npm install --silent)
ok "前端依赖已就绪"

# 5. 启动后端（后台）
step "启动 FastAPI 后端 → http://localhost:8001"
cd "$ROOT"
"$PY" -m uvicorn backend.main:app --host 127.0.0.1 --port 8001 \
    > "$ROOT/.backend.log" 2>&1 &
BACKEND_PID=$!
echo "  后端 PID: $BACKEND_PID  (日志: .backend.log)"

# 6. 等待后端就绪
step "等待后端就绪（首次启动需解压底图，最多 5 分钟）..."
waited=0
max=300
while [ $waited -lt $max ]; do
    sleep 3; waited=$((waited+3))
    if curl -sf http://127.0.0.1:8001/health >/dev/null 2>&1; then
        layers=$(curl -s http://127.0.0.1:8001/health | python3 -c "import sys,json; d=json.load(sys.stdin); print(', '.join(d['vector_layers']))" 2>/dev/null || echo "?")
        ok "后端已就绪  (图层: $layers)"
        break
    fi
    [ $((waited % 15)) -eq 0 ] && step "  … 已等待 ${waited}s"
done
[ $waited -ge $max ] && warn "后端在 ${max}s 内未响应，前端将继续（后端可能还在加载）"

# 7. 启动前端（前台，Ctrl+C 停止）
step "启动 Vite 前端 → http://127.0.0.1:3002"
echo ""
echo "  ─────────────────────────────────────────"
ok "服务已全部启动"
echo ""
echo "    前端  →  http://127.0.0.1:3002"
echo "    后端  →  http://localhost:8001"
echo "    API   →  http://localhost:8001/docs"
echo ""
echo "  按 Ctrl+C 停止前端（后端将继续运行）"
echo "  停止后端：kill $BACKEND_PID"
echo ""

# 捕获 Ctrl+C，同时停止后端
trap "echo ''; step '停止服务...'; kill $BACKEND_PID 2>/dev/null; ok '已停止'; exit 0" INT

cd "$ROOT" && npm run dev
