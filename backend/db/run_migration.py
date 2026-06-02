"""寻味地理 Flavor 库迁移入口。

用法：
    .venv/Scripts/python.exe -m backend.db.run_migration
"""
from __future__ import annotations
import os
import sys
from pathlib import Path

import psycopg2
from dotenv import load_dotenv

from backend.db.seed import seed_all


HERE = Path(__file__).resolve().parent
SCHEMA_SQL = HERE / "schema.sql"


# 预期行数区间（low, high）。超出告警，不阻塞。
EXPECTED_COUNTS = {
    "eco_geo_unit":      (820, 850),
    "ingredient":        (45, 80),
    "ingredient_origin": (50, 120),
    "dish":              (17, 17),
    "recipe_link":       (50, 100),
    "dispersal_event":   (5, 5),
    "dish_lineage":      (0, 0),
    "chapter":           (5, 5),
    "data_source":       (4, 4),
}


def load_database_url() -> str:
    project_root = Path(__file__).resolve().parents[2]
    load_dotenv(project_root / ".env")
    url = os.getenv("DATABASE_URL")
    if not url:
        print("[ERROR] DATABASE_URL 未在 .env 中设置。", file=sys.stderr)
        print("        请 cp .env.example .env 并填入实际密码。", file=sys.stderr)
        sys.exit(1)
    return url


def execute_schema(conn):
    sql = SCHEMA_SQL.read_text(encoding="utf-8")
    with conn.cursor() as cur:
        cur.execute(sql)
        cur.execute("SELECT PostGIS_Version()")
        ver = cur.fetchone()[0]
    print(f"[OK] schema.sql 执行完成；PostGIS={ver}")


def verify(conn):
    print("\n=== verify ===")
    with conn.cursor() as cur:
        for table, (lo, hi) in EXPECTED_COUNTS.items():
            cur.execute(f"SELECT COUNT(*) FROM {table}")
            n = cur.fetchone()[0]
            mark = "[OK]" if lo <= n <= hi else "[!!]"
            print(f"  {mark} {table}: {n} (expect {lo}-{hi})")
        cur.execute(
            "SELECT ST_AsText(coordinates) FROM dish "
            "WHERE coordinates IS NOT NULL LIMIT 1"
        )
        row = cur.fetchone()
        if row:
            print(f"  [OK] POINT sample: {row[0]}")
        cur.execute(
            "SELECT ST_Length(route_geom) FROM dispersal_event "
            "WHERE route_geom IS NOT NULL LIMIT 1"
        )
        row = cur.fetchone()
        if row and row[0] is not None:
            print(f"  [OK] LineString length sample: {row[0]:.2f} deg")
        cur.execute(
            "SELECT COUNT(*) FROM pg_indexes "
            "WHERE schemaname='public' AND indexname LIKE 'idx_%'"
        )
        n_idx = cur.fetchone()[0]
        mark = "[OK]" if n_idx >= 12 else "[!!]"
        print(f"  {mark} indexes: {n_idx} (expect >=12)")


def main():
    url = load_database_url()
    print(f"[INFO] 连接到 {url.rsplit('@', 1)[-1]}")
    try:
        conn = psycopg2.connect(url)
    except psycopg2.OperationalError as e:
        print(f"[ERROR] 连接失败：{e}", file=sys.stderr)
        print("        检查：服务是否启动？库 Flavor 是否已创建？密码是否正确？",
              file=sys.stderr)
        sys.exit(2)

    try:
        with conn:
            execute_schema(conn)
            counts = seed_all(conn)
        print(f"[OK] 种子数据写入：{counts}")
        verify(conn)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
