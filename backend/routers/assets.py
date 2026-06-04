import asyncio
import json
import logging
import re
import urllib.error
import urllib.request
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ..config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL

router = APIRouter(prefix="/api/assets", tags=["assets"])
log = logging.getLogger("assets")


class AnalyzeTextRequest(BaseModel):
    text: str = Field(..., min_length=20, max_length=60000)
    template_id: str | None = None
    product_hint: str | None = None
    origin_hint: str | None = None
    file_names: list[str] = Field(default_factory=list)


class AnalyzeTextResponse(BaseModel):
    model: str
    asset_package: dict[str, Any]


@router.post("/analyze-text", response_model=AnalyzeTextResponse)
async def analyze_text(payload: AnalyzeTextRequest):
    if not DEEPSEEK_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="DEEPSEEK_API_KEY is not configured. Add it to .env and restart the backend.",
        )

    try:
        result = await asyncio.to_thread(_call_deepseek, payload)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        log.warning("DeepSeek HTTP error %s: %s", exc.code, body[:400])
        raise HTTPException(status_code=502, detail=f"DeepSeek request failed: HTTP {exc.code}") from exc
    except urllib.error.URLError as exc:
        log.warning("DeepSeek network error: %s", exc.reason)
        raise HTTPException(status_code=502, detail="DeepSeek request failed: network error") from exc
    except ValueError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return AnalyzeTextResponse(model=DEEPSEEK_MODEL, asset_package=_normalize_package(result))


def _call_deepseek(payload: AnalyzeTextRequest) -> dict[str, Any]:
    request_body = {
        "model": DEEPSEEK_MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    "你是寻味地理系统的空间品牌资产分析器。"
                    "请只输出合法 JSON，不要输出 markdown。"
                    "任务：从产品文档中提取产品、产地、工艺、检测证据、品牌卖点、风险点，"
                    "并评估这些资料是否适合在 WebGIS、传播路线、白皮书、营销海报和智慧大屏中可视化。"
                ),
            },
            {
                "role": "user",
                "content": _build_user_prompt(payload),
            },
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.2,
        "max_tokens": 3200,
    }
    data = json.dumps(request_body, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        f"{DEEPSEEK_BASE_URL.rstrip('/')}/chat/completions",
        data=data,
        headers={
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    with urllib.request.urlopen(req, timeout=90) as response:
        raw = response.read().decode("utf-8")
    envelope = json.loads(raw)
    content = envelope["choices"][0]["message"]["content"]
    return _parse_json_content(content)


def _build_user_prompt(payload: AnalyzeTextRequest) -> str:
    file_names = "、".join(payload.file_names[:12]) or "未提供"
    return f"""
请按下面 JSON 结构分析文档。所有数组都必须存在；没有证据时返回空数组。

{{
  "product": {{
    "name": "",
    "category": "",
    "origin": "",
    "ingredients": []
  }},
  "evidence": {{
    "lab_indicators": [],
    "certifications": [],
    "origin_claims": [],
    "process_steps": []
  }},
  "visualization": {{
    "map_nodes": [],
    "routes": [],
    "timeline": [],
    "radar_metrics": []
  }},
  "brand_assets": {{
    "slogan": "",
    "poster_copy": [],
    "whitepaper_outline": [],
    "dashboard_cards": []
  }},
  "scores": {{
    "completeness": 0,
    "evidence_strength": 0,
    "visualization_fit": 0,
    "risk": 0
  }},
  "risks": [],
  "citations": []
}}

评分说明：
- completeness: 资料完整度 0-100
- evidence_strength: 检测、认证、产地与工艺证据强度 0-100
- visualization_fit: 适合进入地图、路线、时间轴、雷达图和大屏的程度 0-100
- risk: 夸大宣传、证据不足、产地不清、指标缺失等风险 0-100

上下文：
- 模板 ID：{payload.template_id or "未提供"}
- 产品提示：{payload.product_hint or "未提供"}
- 产地提示：{payload.origin_hint or "未提供"}
- 文件名：{file_names}

文档正文：
{payload.text}
""".strip()


def _parse_json_content(content: str) -> dict[str, Any]:
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", content, flags=re.S)
        if not match:
            raise ValueError("DeepSeek returned non-JSON content")
        return json.loads(match.group(0))


def _normalize_package(data: dict[str, Any]) -> dict[str, Any]:
    package: dict[str, Any] = {
        "product": {},
        "evidence": {},
        "visualization": {},
        "brand_assets": {},
        "scores": {},
        "risks": [],
        "citations": [],
    }
    if isinstance(data, dict):
        package.update(data)

    package["product"] = _with_defaults(package.get("product"), {
        "name": "",
        "category": "",
        "origin": "",
        "ingredients": [],
    })
    package["evidence"] = _with_defaults(package.get("evidence"), {
        "lab_indicators": [],
        "certifications": [],
        "origin_claims": [],
        "process_steps": [],
    })
    package["visualization"] = _with_defaults(package.get("visualization"), {
        "map_nodes": [],
        "routes": [],
        "timeline": [],
        "radar_metrics": [],
    })
    package["brand_assets"] = _with_defaults(package.get("brand_assets"), {
        "slogan": "",
        "poster_copy": [],
        "whitepaper_outline": [],
        "dashboard_cards": [],
    })
    package["scores"] = _normalize_scores(package.get("scores"))
    package["risks"] = _as_list(package.get("risks"))
    package["citations"] = _as_list(package.get("citations"))
    return package


def _with_defaults(value: Any, defaults: dict[str, Any]) -> dict[str, Any]:
    merged = defaults.copy()
    if isinstance(value, dict):
        merged.update(value)
    return merged


def _normalize_scores(value: Any) -> dict[str, int]:
    defaults = {
        "completeness": 0,
        "evidence_strength": 0,
        "visualization_fit": 0,
        "risk": 0,
    }
    if isinstance(value, dict):
        for key in defaults:
            defaults[key] = _clamp_score(value.get(key, 0))
    return defaults


def _clamp_score(value: Any) -> int:
    try:
        return max(0, min(100, round(float(value))))
    except (TypeError, ValueError):
        return 0


def _as_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if value in (None, ""):
        return []
    return [value]
