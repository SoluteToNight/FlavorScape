# AGENTS.md

Compact OpenCode guidance for this repo. `CLAUDE.md` has the fuller architecture notes; trust executable config/scripts over prose when they disagree.

## Commands that are easy to get wrong

- Windows one-shot: `.\start.ps1` from repo root; it creates `.venv`, installs deps, frees port 8001, starts FastAPI, waits on `/health`, then starts Vite.
- Bash one-shot: `bash start.sh`; it writes backend logs to `.backend.log` and uses `python3` only to parse the health response.
- Manual backend: `.venv/Scripts/python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8001 --reload`.
- Manual frontend: `npm run dev`; this starts Vite on port 3002 (which proxies `/api` and `/tiles` to FastAPI).
- Python deps: `uv pip install --python .venv/Scripts/python.exe -r backend/requirements.txt`; do not let `uv` pick the system Python.
- DB reset/seed: `.venv/Scripts/python.exe -m backend.db.run_migration` after `.env` has `DATABASE_URL` for a PostGIS database.
- Production static build: `npm run build && npm run start`; `server.js` serves `dist/` but does not proxy Python `/tiles` or FastAPI data.
- No lint/test scripts are configured in `package.json`; use `npm run build`, `/health`, and `/tiles/status` as the focused smoke checks.

## Ports and stale sources

- Current ports: FastAPI 8001, Vite dev 3002, Vite preview 4173, Express 3001.
- Ignore `backend/main.py`'s docstring command using port 8000; `backend/config.py`, scripts, and Vite proxy all use 8001.
- `.claude/settings.local.json` also contains stale 8000 permission examples; do not copy them into new docs or commands.

## Development artifacts

- Save development screenshots in `dev/screenshots/`; do not leave generated PNGs in the repo root.
- Playwright validation screenshots and map UI review captures should use `dev/screenshots/` as the default output folder.

## Git and repository operations

- Do not automatically run `git commit`, `git push`, `git pull`, `git clone`, or upload project changes unless the user explicitly asks for that Git/upload action in the current request.
- It is OK to inspect Git state with read-only commands such as `git status`, `git diff`, `git log`, and `git remote -v` when needed.
- When the user asks to upload or sync with GitHub, confirm the target branch/repository from local context and report what was committed or pushed.

## Product scope

- Desktop-only product scope: do not design, implement, review, or screenshot mobile layouts unless the user explicitly asks for mobile work in that request.
- UI/UX validation should default to desktop viewports only; avoid spending effort on mobile responsiveness or mobile adaptation.

## Architecture traps

- Dev is two-process when fully running: FastAPI 8001 from `start.ps1`/`start.sh`, plus Vite 3002 from `npm run dev`.
- The browser app in dev calls Vite, and Vite proxies `/api/*` and `/tiles/*` to FastAPI 8001.
- In production, Express serves `dist/` and proxies `/api/*` and `/tiles/*` to FastAPI; a separate FastAPI backend is required for full WebGIS functionality.
- FastAPI lifespan blocks all requests until `run_startup()` finishes raster extraction/vector loading and `init_pool()` opens PostgreSQL connections.
- First backend start may spend minutes extracting `data/HYP_HR_SR_W_DR.zip` and loading shapefiles; `start.ps1` waits up to 300s on `/health`.

## Data and database flow

- FastAPI `/api/*` routes call `backend/db/query.py`, which queries PostgreSQL/PostGIS and merges display metadata from `backend/data/app_data.py`.
- Keep `dish` values stable: `query.py` joins DB flavor rows to UI metadata by dish name.
- Route UI metadata is matched by `dispersal_event` order against `app_data.ROUTES`; reordering routes can silently mismatch names/colors/types.
- `.env` is required for `DATABASE_URL` but is ignored by `.gitignore`; never print or commit real credentials.

## Map/GIS gotchas

- All vector data loaded by `backend/startup.py` must already be EPSG:4326; TEOW should prefer `data/extracted/wwf_terr_ecos_wgs84.shp` to avoid runtime reprojection cost.
- Raster tiles use `from rio_tiler.io import Reader`; do not revert to old `COGReader` examples.
- Tile rendering is thread-pooled (`max_workers=6`) and cached with the custom 512-entry LRU in `backend/tile_cache.py`.
- MapLibre `map.addLayer(spec, beforeId)` inserts below/before `beforeId`; passing `beforeId: 'hyp'` would hide vectors under the raster.
- `MapView.vue` appends coastline, rivers, and ecoregions above the HYP raster, then adds Deck.gl `MapboxOverlay({ interleaved: true })` with PathLayer, TripsLayer, and ScatterplotLayer.
- Pinia selection state is mutually exclusive: selecting node, route, or ecozone clears the other two; only `selectedNode` triggers `map.flyTo()`.
