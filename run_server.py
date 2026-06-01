"""Startup wrapper: sets PROJ_LIB before importing rio_tiler/rasterio."""
import os
import sys
from pathlib import Path

# Fix PROJ library conflict: PostgreSQL 16 ships an old proj.db that breaks rasterio.
_venv_site = Path(__file__).resolve().parent / ".venv" / "Lib" / "site-packages"
_proj_data = _venv_site / "rasterio" / "proj_data"
if _proj_data.exists():
    os.environ["PROJ_LIB"] = str(_proj_data)

if __name__ == "__main__":
    from uvicorn import run
    run("backend.main:app", host="127.0.0.1", port=8001, reload=True)
