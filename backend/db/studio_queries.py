"""Studio project persistence queries."""
from __future__ import annotations

from typing import Any

from psycopg2.extras import Json, RealDictCursor


def create_studio_project_table(conn) -> None:
    """Ensure user-owned Studio project storage exists."""
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS studio_project (
                id          VARCHAR(80) PRIMARY KEY,
                user_id     INTEGER NOT NULL REFERENCES app_user(id) ON DELETE CASCADE,
                name        VARCHAR(80) NOT NULL,
                product_id  VARCHAR(120) NOT NULL,
                output_type VARCHAR(20) NOT NULL,
                payload     JSONB NOT NULL,
                version     INTEGER NOT NULL DEFAULT 1,
                created_at  TIMESTAMP NOT NULL DEFAULT NOW(),
                updated_at  TIMESTAMP NOT NULL DEFAULT NOW()
            )
        """)
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_studio_project_user_updated
            ON studio_project (user_id, updated_at DESC)
        """)
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_studio_project_user_product
            ON studio_project (user_id, product_id)
        """)


def _iso(value: Any) -> str | None:
    return value.isoformat() if hasattr(value, "isoformat") else (str(value) if value is not None else None)


def _row_to_project(row: dict) -> dict:
    payload = dict(row.get("payload") or {})
    payload["id"] = row["id"]
    payload["name"] = row["name"]
    payload["productId"] = row["product_id"]
    payload["outputType"] = row["output_type"]
    payload["activeOutput"] = row["output_type"]
    payload["version"] = row["version"]
    payload["createdAt"] = _iso(row["created_at"]) or payload.get("createdAt")
    payload["updatedAt"] = _iso(row["updated_at"]) or payload.get("updatedAt")
    return payload


def list_projects(conn, user_id: int) -> list[dict]:
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            """
            SELECT id, name, product_id, output_type, payload, version, created_at, updated_at
            FROM studio_project
            WHERE user_id = %s
            ORDER BY updated_at DESC
            """,
            (user_id,),
        )
        return [_row_to_project(dict(row)) for row in cur.fetchall()]


def get_project(conn, user_id: int, project_id: str) -> dict | None:
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            """
            SELECT id, name, product_id, output_type, payload, version, created_at, updated_at
            FROM studio_project
            WHERE user_id = %s AND id = %s
            """,
            (user_id, project_id),
        )
        row = cur.fetchone()
        return _row_to_project(dict(row)) if row else None


def create_project(conn, user_id: int, project: dict) -> dict:
    payload = dict(project)
    payload["version"] = 1
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            """
            INSERT INTO studio_project (id, user_id, name, product_id, output_type, payload, version)
            VALUES (%s, %s, %s, %s, %s, %s, 1)
            RETURNING id, name, product_id, output_type, payload, version, created_at, updated_at
            """,
            (
                payload["id"],
                user_id,
                payload["name"],
                payload["productId"],
                payload["outputType"],
                Json(payload),
            ),
        )
        return _row_to_project(dict(cur.fetchone()))


def update_project(conn, user_id: int, project_id: str, project: dict, version: int) -> dict | None:
    payload = dict(project)
    next_version = int(version) + 1
    payload["version"] = next_version
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            """
            UPDATE studio_project
            SET name = %s,
                product_id = %s,
                output_type = %s,
                payload = %s,
                version = version + 1,
                updated_at = NOW()
            WHERE user_id = %s AND id = %s AND version = %s
            RETURNING id, name, product_id, output_type, payload, version, created_at, updated_at
            """,
            (
                payload["name"],
                payload["productId"],
                payload["outputType"],
                Json(payload),
                user_id,
                project_id,
                version,
            ),
        )
        row = cur.fetchone()
        return _row_to_project(dict(row)) if row else None


def delete_project(conn, user_id: int, project_id: str) -> bool:
    with conn.cursor() as cur:
        cur.execute(
            "DELETE FROM studio_project WHERE user_id = %s AND id = %s",
            (user_id, project_id),
        )
        return cur.rowcount > 0
