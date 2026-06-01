"""食材传播数据 API。

读取 data/ingredient/*.json，支持多食材可扩展架构。
每个 JSON 文件遵循统一 schema：
  ingredient_id, name, name_en, species, origin, origin_coordinates,
  summary, color, timeline[{year, dynasty, location, coordinates, ...}]
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException

from ..config import DATA_DIR

log = logging.getLogger("ingredient_spread")
router = APIRouter(prefix="/api/ingredients", tags=["ingredients"])

INGREDIENT_DIR = DATA_DIR / "ingredient"

_cache: dict[str, dict] = {}
_loaded = False


def _load_all() -> dict[str, dict]:
    global _cache, _loaded
    if _loaded:
        return _cache

    if not INGREDIENT_DIR.exists():
        log.warning("Ingredient data directory not found: %s", INGREDIENT_DIR)
        _loaded = True
        return _cache

    for fp in sorted(INGREDIENT_DIR.glob("*.json")):
        try:
            data = json.loads(fp.read_text(encoding="utf-8"))
            iid = data.get("ingredient_id") or fp.stem
            _cache[iid] = data
            log.info("Loaded ingredient: %s (%s)", iid, data.get("name", "?"))
        except Exception as exc:
            log.warning("Failed to load %s: %s", fp.name, exc)

    _loaded = True
    return _cache


def _reload():
    global _cache, _loaded
    _cache = {}
    _loaded = False
    _load_all()


@router.get("/spread")
def list_ingredients():
    """列出所有可用食材传播数据（概要信息）。"""
    all_data = _load_all()
    results = []
    for iid, data in all_data.items():
        timeline = data.get("timeline", [])
        results.append({
            "ingredient_id": iid,
            "name": data.get("name", iid),
            "name_en": data.get("name_en", ""),
            "species": data.get("species", ""),
            "origin": data.get("origin", ""),
            "origin_coordinates": data.get("origin_coordinates"),
            "summary": data.get("summary", ""),
            "color": data.get("color", "#E5394E"),
            "image_url": data.get("image_url") or data.get("image") or f"/ingredients/{iid}.svg",
            "event_count": len(timeline),
            "year_range": [
                min(e["year"] for e in timeline) if timeline else None,
                max(e["year"] for e in timeline) if timeline else None,
            ],
        })
    return results


@router.get("/spread/{ingredient_id}")
def get_ingredient_spread(ingredient_id: str):
    """获取单个食材的完整传播时间线。"""
    all_data = _load_all()
    if ingredient_id not in all_data:
        raise HTTPException(404, f"Ingredient '{ingredient_id}' not found. Available: {list(all_data.keys())}")
    return all_data[ingredient_id]


@router.get("/spread/{ingredient_id}/path")
def get_ingredient_path(ingredient_id: str):
    """获取食材传播路径（按时间排序的坐标序列 + 路径段信息）。"""
    all_data = _load_all()
    if ingredient_id not in all_data:
        raise HTTPException(404, f"Ingredient '{ingredient_id}' not found.")

    data = all_data[ingredient_id]
    timeline = sorted(data.get("timeline", []), key=lambda e: e["year"])

    origin_coords = data.get("origin_coordinates")
    path_coords = []
    segments = []

    if origin_coords:
        path_coords.append({
            "year": None,
            "location": data.get("origin", ""),
            "coordinates": origin_coords,
            "type": "origin",
        })

    for event in timeline:
        coords = event.get("coordinates")
        if not coords:
            continue
        path_coords.append({
            "year": event["year"],
            "location": event["location"],
            "coordinates": coords,
            "type": event.get("event_type", ""),
            "dynasty": event.get("dynasty", ""),
            "historical_name": event.get("historical_name", []),
            "route": event.get("route", ""),
            "notes": event.get("notes", ""),
            "source_literature": event.get("source_literature", ""),
        })

    for i in range(len(path_coords) - 1):
        curr = path_coords[i]
        nxt = path_coords[i + 1]
        segments.append({
            "from": curr["coordinates"],
            "to": nxt["coordinates"],
            "from_year": curr.get("year"),
            "to_year": nxt["year"],
            "from_location": curr["location"],
            "to_location": nxt["location"],
            "route_desc": nxt.get("route", ""),
        })

    return {
        "ingredient_id": ingredient_id,
        "name": data.get("name", ""),
        "color": data.get("color", "#E5394E"),
        "path_coords": path_coords,
        "segments": segments,
    }
