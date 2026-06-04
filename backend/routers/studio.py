"""Authenticated Studio project API."""
from __future__ import annotations

from typing import Any, Literal

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from ..auth_deps import get_current_user
from ..db.connection import get_db
from ..db import studio_queries


router = APIRouter(prefix="/api/studio", tags=["studio"])


class StudioProjectPayload(BaseModel):
    id: str = Field(..., min_length=1, max_length=80)
    name: str = Field(..., min_length=1, max_length=80)
    productId: str = Field(..., min_length=1, max_length=120)
    outputType: Literal["poster", "archive", "display"]
    activeOutput: str | None = None
    createdAt: str | None = None
    updatedAt: str | None = None
    outputs: dict[str, Any]
    exports: list[Any] = Field(default_factory=list)
    version: int | None = None

    class Config:
        extra = "allow"


class ProjectWriteRequest(BaseModel):
    project: StudioProjectPayload


class ProjectPatchRequest(BaseModel):
    project: StudioProjectPayload
    version: int = Field(..., ge=1)


def _user_id(user: dict) -> int:
    return int(user["id"])


def _ok(data: dict) -> dict:
    return {"ok": True, "data": data}


@router.get("/projects")
async def list_projects(user: dict = Depends(get_current_user), conn=Depends(get_db)):
    projects = studio_queries.list_projects(conn, _user_id(user))
    return _ok({"projects": projects})


@router.get("/projects/{project_id}")
async def get_project(project_id: str, user: dict = Depends(get_current_user), conn=Depends(get_db)):
    project = studio_queries.get_project(conn, _user_id(user), project_id)
    if project is None:
        return JSONResponse(status_code=404, content={"ok": False, "error": "项目不存在或无权访问"})
    return _ok({"project": project})


@router.post("/projects")
async def create_project(body: ProjectWriteRequest, user: dict = Depends(get_current_user), conn=Depends(get_db)):
    project = studio_queries.create_project(conn, _user_id(user), body.project.dict())
    return _ok({"project": project})


@router.patch("/projects/{project_id}")
async def update_project(project_id: str, body: ProjectPatchRequest, user: dict = Depends(get_current_user), conn=Depends(get_db)):
    if body.project.id != project_id:
        return JSONResponse(status_code=400, content={"ok": False, "error": "项目 ID 不匹配"})
    project = studio_queries.update_project(conn, _user_id(user), project_id, body.project.dict(), body.version)
    if project is None:
        current = studio_queries.get_project(conn, _user_id(user), project_id)
        if current is None:
            return JSONResponse(status_code=404, content={"ok": False, "error": "项目不存在或无权访问"})
        return JSONResponse(status_code=409, content={"ok": False, "error": "项目已在其他位置更新，请重新加载"})
    return _ok({"project": project})


@router.delete("/projects/{project_id}")
async def delete_project(project_id: str, user: dict = Depends(get_current_user), conn=Depends(get_db)):
    deleted = studio_queries.delete_project(conn, _user_id(user), project_id)
    if not deleted:
        return JSONResponse(status_code=404, content={"ok": False, "error": "项目不存在或无权访问"})
    return _ok({"deleted": True})

