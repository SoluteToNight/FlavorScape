"""从 JSON 文件导入业务数据到 PostgreSQL/PostGIS。

默认行为：
1. 保留 `eco_geo_unit` 生态区表
2. 清空业务表
3. 从 JSON 全量导入 flavors/routes/chapters/dataSources

用法：
    .venv/Scripts/python.exe -m backend.db.import_json path\\to\\bundle.json
    .venv/Scripts/python.exe -m backend.db.import_json path\\to\\bundle.json --init-schema
    .venv/Scripts/python.exe -m backend.db.import_json path\\to\\bundle.json --keep-existing
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import psycopg2

from backend.db.run_migration import execute_schema, load_database_url, verify
from backend.db.seed import DataBundle, reset_business_tables, seed_all

TABLE_FILE_CANDIDATES = {
    "flavors": ["flavor_genotype.json", "flavors.json"],
    "routes": ["dispersal_event.json", "routes.json"],
    "chapters": ["chapter.json", "chapters.json"],
    "data_sources": ["data_source.json", "data_sources.json", "dataSources.json"],
}


def _require_dict(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{label} 必须是对象。")
    return value


def _require_list(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise ValueError(f"{label} 必须是数组。")
    return value


def _require_str(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} 必须是非空字符串。")
    return value.strip()


def _coerce_float_list(value: Any, label: str, expected_len: int | None = None) -> list[float]:
    items = _require_list(value, label)
    if expected_len is not None and len(items) != expected_len:
        raise ValueError(f"{label} 长度必须为 {expected_len}。")
    try:
        return [float(item) for item in items]
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} 必须全部是数字。") from exc


def _coerce_str_list(value: Any, label: str) -> list[str]:
    items = _require_list(value, label)
    result = []
    for idx, item in enumerate(items):
        result.append(_require_str(item, f"{label}[{idx}]"))
    return result


def _pick(container: dict[str, Any], *keys: str, required: bool = False, default: Any = None) -> Any:
    for key in keys:
        if key in container:
            return container[key]
    if required:
        raise ValueError(f"缺少字段：{' / '.join(keys)}")
    return default


def _normalize_flavor(item: Any, idx: int) -> dict[str, Any]:
    obj = _require_dict(item, f"flavors[{idx}]")
    primary = _coerce_str_list(_pick(obj, "primary", required=True), f"flavors[{idx}].primary")
    vals = _coerce_float_list(_pick(obj, "vals", required=True), f"flavors[{idx}].vals", expected_len=len(primary))
    coordinates = _coerce_float_list(_pick(obj, "coordinates", required=True), f"flavors[{idx}].coordinates", expected_len=2)
    scores = _coerce_float_list(_pick(obj, "scores", required=True), f"flavors[{idx}].scores", expected_len=6)
    return {
        "id": _require_str(_pick(obj, "id", required=True), f"flavors[{idx}].id"),
        "city": _require_str(_pick(obj, "city", required=True), f"flavors[{idx}].city"),
        "dish": _require_str(_pick(obj, "dish", required=True), f"flavors[{idx}].dish"),
        "dish_family": _pick(obj, "dish_family", "dishFamily"),
        "region": _require_str(_pick(obj, "region", required=True), f"flavors[{idx}].region"),
        "eco": _require_str(_pick(obj, "eco", required=True), f"flavors[{idx}].eco"),
        "eco_name": _pick(obj, "eco_name", "ecoName"),
        "scores": scores,
        "primary": primary,
        "vals": vals,
        "color": _require_str(_pick(obj, "color", "colorHex", required=True), f"flavors[{idx}].color"),
        "cat": _require_str(_pick(obj, "cat", "category", required=True), f"flavors[{idx}].cat"),
        "ingredients": _coerce_str_list(_pick(obj, "ingredients", required=True), f"flavors[{idx}].ingredients"),
        "coordinates": coordinates,
    }


def _normalize_route(item: Any, idx: int) -> dict[str, Any]:
    obj = _require_dict(item, f"routes[{idx}]")
    path = _require_list(_pick(obj, "path", required=True), f"routes[{idx}].path")
    if len(path) < 2:
        raise ValueError(f"routes[{idx}].path 至少需要 2 个坐标点。")
    normalized_path = []
    for p_idx, point in enumerate(path):
        normalized_path.append(
            _coerce_float_list(point, f"routes[{idx}].path[{p_idx}]", expected_len=2)
        )
    route_type = _require_str(_pick(obj, "type", "route_type", required=True), f"routes[{idx}].type")
    if route_type not in {"land", "sea"}:
        raise ValueError(f"routes[{idx}].type 只能是 land 或 sea。")
    return {
        "name": _require_str(_pick(obj, "name", required=True), f"routes[{idx}].name"),
        "color": _require_str(_pick(obj, "color", "colorHex", required=True), f"routes[{idx}].color"),
        "type": route_type,
        "path": normalized_path,
        "ingredient_name": _pick(obj, "ingredient_name", "ingredientName", "ingredient"),
    }


def _normalize_chapter(item: Any, idx: int) -> dict[str, Any]:
    obj = _require_dict(item, f"chapters[{idx}]")
    chapter_id = _pick(obj, "id", "chapter_id", "chapterId", required=True)
    try:
        chapter_id = int(chapter_id)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"chapters[{idx}].id 必须是整数。") from exc
    return {
        "id": chapter_id,
        "title": _require_str(_pick(obj, "title", required=True), f"chapters[{idx}].title"),
        "date": _require_str(_pick(obj, "date", "date_label", "dateLabel", required=True), f"chapters[{idx}].date"),
        "body": _require_str(_pick(obj, "body", required=True), f"chapters[{idx}].body"),
        "cite": _require_str(_pick(obj, "cite", required=True), f"chapters[{idx}].cite"),
        "source": _require_str(_pick(obj, "source", required=True), f"chapters[{idx}].source"),
        "routeName": _require_str(_pick(obj, "routeName", "route_name", required=True), f"chapters[{idx}].routeName"),
    }


def _normalize_data_source(item: Any, idx: int) -> dict[str, Any]:
    obj = _require_dict(item, f"dataSources[{idx}]")
    return {
        "name": _require_str(_pick(obj, "name", required=True), f"dataSources[{idx}].name"),
        "desc": _require_str(_pick(obj, "desc", "description", required=True), f"dataSources[{idx}].desc"),
        "color": _require_str(_pick(obj, "color", "colorHex", required=True), f"dataSources[{idx}].color"),
        "url": _require_str(_pick(obj, "url", required=True), f"dataSources[{idx}].url"),
    }


def normalize_bundle(raw: Any) -> DataBundle:
    root = _require_dict(raw, "JSON 根对象")
    flavors = _require_list(_pick(root, "flavors", "FLAVORS", required=True), "flavors")
    routes = _require_list(_pick(root, "routes", "ROUTES", required=True), "routes")
    chapters = _require_list(_pick(root, "chapters", "CHAPTERS", required=True), "chapters")
    data_sources = _require_list(
        _pick(root, "dataSources", "data_sources", "DATA_SOURCES", required=True),
        "dataSources",
    )
    return {
        "flavors": [_normalize_flavor(item, idx) for idx, item in enumerate(flavors)],
        "routes": [_normalize_route(item, idx) for idx, item in enumerate(routes)],
        "chapters": [_normalize_chapter(item, idx) for idx, item in enumerate(chapters)],
        "data_sources": [_normalize_data_source(item, idx) for idx, item in enumerate(data_sources)],
    }


def load_bundle(json_path: Path) -> DataBundle:
    try:
        raw = json.loads(json_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"JSON 文件不存在：{json_path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"JSON 解析失败：{exc}") from exc
    return normalize_bundle(raw)


def _load_json_file(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"JSON 文件不存在：{path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"JSON 解析失败：{path} -> {exc}") from exc


def load_bundle_from_directory(dir_path: Path) -> DataBundle:
    if not dir_path.is_dir():
        raise NotADirectoryError(f"不是目录：{dir_path}")

    raw: dict[str, Any] = {}
    for logical_name, candidates in TABLE_FILE_CANDIDATES.items():
        match = next((dir_path / name for name in candidates if (dir_path / name).exists()), None)
        if match is None:
            joined = " / ".join(candidates)
            raise FileNotFoundError(f"目录 {dir_path} 中缺少 {logical_name} 文件，支持文件名：{joined}")
        raw[logical_name] = _load_json_file(match)

    return normalize_bundle(raw)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="导入业务 JSON 到 Flavor 数据库。")
    parser.add_argument("json_path", help="JSON 文件路径，或包含四个实体 JSON 的目录路径")
    parser.add_argument(
        "--init-schema",
        action="store_true",
        help="先执行 schema.sql 再导入。适合首次建库或重建数据库。",
    )
    parser.add_argument(
        "--keep-existing",
        action="store_true",
        help="保留现有业务数据，仅插入缺失记录。默认会先清空业务表后全量导入。",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    json_path = Path(args.json_path).expanduser().resolve()
    bundle = load_bundle_from_directory(json_path) if json_path.is_dir() else load_bundle(json_path)
    url = load_database_url()

    print(f"[INFO] JSON 文件：{json_path}")
    print(f"[INFO] 连接到 {url.rsplit('@', 1)[-1]}")

    try:
        conn = psycopg2.connect(url)
    except psycopg2.OperationalError as exc:
        print(f"[ERROR] 连接失败：{exc}", file=sys.stderr)
        sys.exit(2)

    try:
        with conn:
            if args.init_schema:
                execute_schema(conn)
            if not args.keep_existing:
                reset_business_tables(conn)
                print("[OK] 已清空业务表（保留 eco_geo_unit）。")
            counts = seed_all(conn, bundle=bundle)
        print(f"[OK] JSON 导入完成：{counts}")
        verify(conn)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
