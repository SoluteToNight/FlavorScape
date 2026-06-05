"""Authenticated Studio project API."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal
from uuid import uuid4

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from ..auth_deps import get_current_user
from ..db.connection import get_db
from ..db import studio_queries


router = APIRouter(prefix="/api/studio", tags=["studio"])


OUTPUT_LABELS = {
    "poster": "海报",
    "archive": "白皮书",
    "display": "大屏",
}

TEMPLATE_PRODUCT_MAP = {
    "jasmine": "jasmine-tea",
    "jasmine-tea": "jasmine-tea",
    "pepper": "hanyuan-pepper",
    "hanyuan-pepper": "hanyuan-pepper",
    "rice": "wuchang-rice",
    "wuchang-rice": "wuchang-rice",
    "coconut": "jasmine-tea",
    "longjing": "longjing-tea",
    "longjing-tea": "longjing-tea",
}

CONTENT_MODULES = {
    "poster": {
        "mainImage": True,
        "brandCopy": True,
        "spatialMap": True,
        "evidenceMetrics": True,
    },
    "archive": {
        "originInfo": True,
        "spatialBase": True,
        "evidenceMetrics": True,
        "nodeLinks": True,
        "conclusion": True,
    },
    "display": {
        "productInfo": True,
        "evidenceMetrics": True,
        "spatialNodes": True,
        "routeInteraction": True,
    },
}


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


class AssetPackageProjectRequest(BaseModel):
    asset_package: dict[str, Any] = Field(default_factory=dict)
    extraction: dict[str, Any] = Field(default_factory=dict)
    template_id: str | None = None
    product_id: str | None = None
    output_type: Literal["poster", "archive", "display"] = "poster"
    name: str | None = None


def _user_id(user: dict) -> int:
    return int(user["id"])


def _ok(data: dict) -> dict:
    return {"ok": True, "data": data}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _project_id() -> str:
    return f"asset-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}-{uuid4().hex[:8]}"


def _mapped_product_id(body: AssetPackageProjectRequest) -> str:
    if body.product_id:
        return body.product_id
    key = (body.template_id or "").strip()
    return TEMPLATE_PRODUCT_MAP.get(key, "jasmine-tea")


def _as_text(value: Any) -> str:
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, dict):
        for key in ("title", "name", "label", "desc", "description", "value"):
            if value.get(key):
                return str(value[key]).strip()
        return ""
    if value is None:
        return ""
    return str(value).strip()


def _text_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [text for text in (_as_text(item) for item in value) if text]


def _first_text(value: Any, fallback: str = "") -> str:
    items = _text_list(value)
    return items[0] if items else fallback


def _truncate(value: Any, limit: int) -> str:
    return _as_text(value)[:limit]


def _theme_from_asset(asset_package: dict[str, Any]) -> str:
    text = " ".join(_text_list(asset_package.get("brand_assets", {}).get("style_direction"))).lower()
    if any(key in text for key in ("蓝", "indigo", "科技", "展陈", "冷色")):
        return "indigo"
    if any(key in text for key in ("红", "东方", "礼盒", "非遗", "heritage")):
        return "heritage"
    return "nature"


def _template_params_from_asset(asset_package: dict[str, Any]) -> dict[str, Any]:
    style_text = " ".join(_text_list(asset_package.get("brand_assets", {}).get("style_direction")))
    layout_text = " ".join(_text_list(asset_package.get("brand_assets", {}).get("layout_direction")))
    combined = f"{style_text} {layout_text}".lower()
    layout = "evidence" if any(key in combined for key in ("证据", "指标", "溯源")) else "editorial" if any(key in combined for key in ("杂志", "海报", "视觉")) else "balanced"
    palette = "warm" if any(key in combined for key in ("暖", "红", "金", "礼盒")) else "noir" if any(key in combined for key in ("黑", "深", "高端")) else "fresh"
    return {
        "layout": layout,
        "palette": palette,
        "density": "compact" if "信息密集" in combined or "招商" in combined else "normal",
        "imageShape": "arch" if "东方" in combined or "非遗" in combined else "standard",
        "metricStyle": "cards",
        "titleScale": 100,
        "badgeText": "AI 资产包 · 空间证据 · 可复核",
    }


def _evidence_labels(asset_package: dict[str, Any]) -> list[str]:
    evidence = asset_package.get("evidence") if isinstance(asset_package.get("evidence"), dict) else {}
    labels: list[str] = []
    for key in ("lab_indicators", "certifications", "origin_claims", "process_steps"):
        for item in evidence.get(key, []) if isinstance(evidence.get(key), list) else []:
            if isinstance(item, dict):
                label = item.get("label") or item.get("name") or item.get("title")
                if label:
                    labels.append(str(label))
            else:
                labels.append(str(item)[:18])
    return labels[:8]


def _has_visual_route(asset_package: dict[str, Any]) -> bool:
    visualization = asset_package.get("visualization") if isinstance(asset_package.get("visualization"), dict) else {}
    routes = visualization.get("routes")
    timeline = visualization.get("timeline")
    map_nodes = visualization.get("map_nodes")
    return (
        isinstance(routes, list) and len(routes) > 0
    ) or (
        isinstance(timeline, list) and len(timeline) > 0
    ) or (
        isinstance(map_nodes, list) and len(map_nodes) > 1
    )


def _build_project_from_asset(body: AssetPackageProjectRequest) -> dict[str, Any]:
    asset = body.asset_package or {}
    product = asset.get("product") if isinstance(asset.get("product"), dict) else {}
    brand = asset.get("brand_assets") if isinstance(asset.get("brand_assets"), dict) else {}
    visualization = asset.get("visualization") if isinstance(asset.get("visualization"), dict) else {}
    product_name = _truncate(product.get("name"), 32) or "AI 资产包项目"
    output_type = body.output_type
    created_at = _now_iso()
    project_name = _truncate(body.name, 80) or f"{product_name} · {OUTPUT_LABELS[output_type]}项目"
    poster_copy = _text_list(brand.get("poster_copy"))
    outline = _text_list(brand.get("whitepaper_outline"))
    dashboard_cards = _text_list(brand.get("dashboard_cards"))
    slogan = _truncate(brand.get("slogan"), 80)
    origin = _truncate(product.get("origin"), 60)
    category = _truncate(product.get("category"), 40)
    has_visual_route = _has_visual_route(asset)

    return {
        "id": _project_id(),
        "name": project_name,
        "productId": _mapped_product_id(body),
        "outputType": output_type,
        "activeOutput": output_type,
        "createdAt": created_at,
        "updatedAt": created_at,
        "sourceAsset": {
            "type": "deepseek_asset_package",
            "templateId": body.template_id,
            "createdAt": created_at,
            "assetPackage": asset,
            "extraction": body.extraction,
            "citations": asset.get("citations") if isinstance(asset.get("citations"), list) else [],
            "reviewStatus": asset.get("review_status") or {"status": "pending", "summary": "证据尚未人工复核。"},
        },
        "outputs": {
            "poster": {
                "contentModules": CONTENT_MODULES["poster"],
                "contentConfirmed": output_type == "poster",
                "title": product_name,
                "subtitle": _truncate(poster_copy[0] if poster_copy else f"{origin} · {category}", 60),
                "poeticLine": _truncate(slogan or _first_text(brand.get("style_direction"), "空间证据生成的品牌表达"), 40),
                "narrative": _truncate(poster_copy[1] if len(poster_copy) > 1 else _first_text(brand.get("layout_direction"), slogan), 300),
                "theme": _theme_from_asset(asset),
                "templateParams": _template_params_from_asset(asset),
                "customImageDataUrl": None,
                "imagePosY": 50,
                "updatedAt": created_at if output_type == "poster" else None,
            },
            "archive": {
                "contentModules": CONTENT_MODULES["archive"],
                "contentConfirmed": output_type == "archive",
                "title": _truncate(outline[0] if outline else f"{product_name} · 实证白皮书", 42),
                "summary": _truncate(outline[1] if len(outline) > 1 else slogan or f"{product_name} 的产地、工艺和证据链已整理为可复核资产包。", 180),
                "conclusion": _truncate(_first_text(asset.get("next_actions"), f"{product_name} 仍需结合原始报告、认证编号和批次信息完成人工复核。"), 160),
                "visibleEvidence": _evidence_labels(asset),
                "updatedAt": created_at if output_type == "archive" else None,
            },
            "display": {
                "contentModules": CONTENT_MODULES["display"],
                "contentConfirmed": output_type == "display",
                "title": _truncate(dashboard_cards[0] if dashboard_cards else f"{product_name} · 智慧大屏", 36),
                "subtitle": _truncate(slogan or f"{origin} / {category}", 48),
                "caption": _truncate(dashboard_cards[1] if len(dashboard_cards) > 1 else _first_text(visualization.get("timeline"), "以产地节点、证据指标和传播路径组织空间展示。"), 160),
                "interactionMode": "route" if has_visual_route else "product",
                "selectedRouteId": "asset-route" if has_visual_route else None,
                "selectedEventKey": None,
                "showTimeline": True,
                "updatedAt": created_at if output_type == "display" else None,
            },
        },
        "exports": [],
    }


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


@router.post("/projects/from-asset-package")
async def create_project_from_asset_package(
    body: AssetPackageProjectRequest,
    user: dict = Depends(get_current_user),
    conn=Depends(get_db),
):
    project_payload = _build_project_from_asset(body)
    project = studio_queries.create_project(conn, _user_id(user), project_payload)
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

