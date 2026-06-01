# 寻味地理 / FlavorScape

地方食材品牌故事地图、轻量溯源可视化产品生成器、食材历史传播图谱。

当前项目处于产品化原型重构阶段。切换新对话或恢复上下文时，请先阅读：

- `docs/项目恢复与新对话交接-20260601.md`
- `docs/开发进度同步-产品化原型重构.md`
- `CLAUDE.md`
- `AGENTS.md`

## 启动

Windows PowerShell：

```powershell
.\start.ps1
```

手动启动：

```powershell
.venv/Scripts/python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8001 --reload
npm run dev
```

访问：

- 前端：`http://localhost:5173`
- 后端：`http://localhost:8001`
- API 文档：`http://localhost:8001/docs`

## 重点页面

- `/brand`：产品生成器，支持地理志、品牌公示、产业链、风物档案，并可导出 PNG。
- `/spread`：食材传播图谱，读取 `data/ingredient/*.json`。
- `/map`：原 WebGIS 风味底图。

## 验证

```powershell
npm run build
```

2026-06-01 已验证前端构建通过。完整地图能力还需要 FastAPI 后端和本地 GIS 数据。
