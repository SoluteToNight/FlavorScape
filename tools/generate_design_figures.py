from __future__ import annotations

import math
import textwrap
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "总体设计配图-寻味地理_20260509"
OUT.mkdir(parents=True, exist_ok=True)


def font_path() -> str | None:
    candidates = [
        Path("C:/Windows/Fonts/msyh.ttc"),
        Path("C:/Windows/Fonts/simhei.ttf"),
        Path("C:/Windows/Fonts/simsun.ttc"),
    ]
    for p in candidates:
        if p.exists():
            return str(p)
    return None


FONT_PATH = font_path()


def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    if FONT_PATH:
        return ImageFont.truetype(FONT_PATH, size=size)
    return ImageFont.load_default()


PALETTE = {
    "bg": "#F7F9F5",
    "ink": "#20382D",
    "muted": "#5B6B63",
    "line": "#B8C7BC",
    "green": "#315F4D",
    "teal": "#4FA69A",
    "blue": "#4E79A7",
    "amber": "#D6A23F",
    "red": "#C95A49",
    "purple": "#7B6BB1",
    "leaf": "#7FA961",
    "panel": "#FFFFFF",
    "soft": "#EAF2EA",
}


def hex_to_rgb(s: str) -> tuple[int, int, int]:
    s = s.strip("#")
    return tuple(int(s[i : i + 2], 16) for i in (0, 2, 4))


def esc(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def wrap_text(text: str, width: int) -> list[str]:
    if not text:
        return []
    out: list[str] = []
    for part in text.split("\n"):
        if len(part) <= width:
            out.append(part)
        else:
            out.extend(textwrap.wrap(part, width=width, break_long_words=False, replace_whitespace=False))
    return out


@dataclass
class Box:
    x: float
    y: float
    w: float
    h: float
    title: str
    body: str = ""
    color: str = PALETTE["green"]
    fill: str = PALETTE["panel"]
    r: float = 18

    @property
    def cx(self) -> float:
        return self.x + self.w / 2

    @property
    def cy(self) -> float:
        return self.y + self.h / 2


class Canvas:
    def __init__(self, width: int = 1600, height: int = 1000, title: str = ""):
        self.w = width
        self.h = height
        self.title = title
        self.img = Image.new("RGB", (width, height), hex_to_rgb(PALETTE["bg"]))
        self.draw = ImageDraw.Draw(self.img)
        self.svg: list[str] = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
            "<defs>",
            '<filter id="shadow" x="-20%" y="-20%" width="140%" height="140%"><feDropShadow dx="0" dy="8" stdDeviation="10" flood-color="#23352D" flood-opacity="0.12"/></filter>',
            '<marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#6C7A72"/></marker>',
            "</defs>",
            f'<rect width="{width}" height="{height}" fill="{PALETTE["bg"]}"/>',
        ]
        if title:
            self.header(title)

    def header(self, title: str, subtitle: str = ""):
        self.text(title, 70, 62, size=34, color=PALETTE["ink"], weight="bold")
        self.line(70, 112, self.w - 70, 112, color="#D9E2DA", width=2)
        if subtitle:
            self.text(subtitle, 70, 130, size=20, color=PALETTE["muted"])

    def text(
        self,
        text: str,
        x: float,
        y: float,
        size: int = 24,
        color: str = PALETTE["ink"],
        weight: str = "normal",
        max_chars: int | None = None,
        line_gap: int = 7,
        anchor: str = "la",
    ):
        lines = wrap_text(text, max_chars) if max_chars else text.split("\n")
        font = load_font(size, bold=(weight == "bold"))
        for i, line in enumerate(lines):
            yy = y + i * (size + line_gap)
            self.draw.text((x, yy), line, font=font, fill=hex_to_rgb(color), anchor=anchor)
        svg_weight = "700" if weight == "bold" else "400"
        self.svg.append(
            f'<text x="{x:.1f}" y="{y:.1f}" fill="{color}" font-family="Microsoft YaHei, SimSun, sans-serif" '
            f'font-size="{size}" font-weight="{svg_weight}">'
        )
        for i, line in enumerate(lines):
            dy = 0 if i == 0 else size + line_gap
            self.svg.append(f'<tspan x="{x:.1f}" dy="{dy}">{esc(line)}</tspan>')
        self.svg.append("</text>")

    def line(self, x1, y1, x2, y2, color=PALETTE["line"], width=3, arrow=False, dash=False):
        fill = hex_to_rgb(color)
        self.draw.line((x1, y1, x2, y2), fill=fill, width=width)
        if arrow:
            self._arrow_head(x1, y1, x2, y2, color)
        dash_attr = ' stroke-dasharray="8 8"' if dash else ""
        marker = ' marker-end="url(#arrow)"' if arrow else ""
        self.svg.append(
            f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{width}" stroke-linecap="round"{dash_attr}{marker}/>'
        )

    def polyline(self, pts, color=PALETTE["line"], width=3, arrow=False, dash=False):
        self.draw.line(pts, fill=hex_to_rgb(color), width=width, joint="curve")
        if arrow and len(pts) >= 2:
            self._arrow_head(*pts[-2], *pts[-1], color)
        dash_attr = ' stroke-dasharray="8 8"' if dash else ""
        marker = ' marker-end="url(#arrow)"' if arrow else ""
        pts_str = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        self.svg.append(
            f'<polyline points="{pts_str}" fill="none" stroke="{color}" stroke-width="{width}" '
            f'stroke-linecap="round" stroke-linejoin="round"{dash_attr}{marker}/>'
        )

    def _arrow_head(self, x1, y1, x2, y2, color):
        angle = math.atan2(y2 - y1, x2 - x1)
        size = 14
        pts = [
            (x2, y2),
            (x2 - size * math.cos(angle - 0.45), y2 - size * math.sin(angle - 0.45)),
            (x2 - size * math.cos(angle + 0.45), y2 - size * math.sin(angle + 0.45)),
        ]
        self.draw.polygon(pts, fill=hex_to_rgb(color))

    def rounded_rect(self, x, y, w, h, fill, outline="#D9E2DA", radius=18, width=2, shadow=False):
        if shadow:
            self.draw.rounded_rectangle((x + 5, y + 8, x + w + 5, y + h + 8), radius=radius, fill=(220, 226, 220))
        self.draw.rounded_rectangle((x, y, x + w, y + h), radius=radius, fill=hex_to_rgb(fill), outline=hex_to_rgb(outline), width=width)
        shadow_attr = ' filter="url(#shadow)"' if shadow else ""
        self.svg.append(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{radius}" '
            f'fill="{fill}" stroke="{outline}" stroke-width="{width}"{shadow_attr}/>'
        )

    def box(self, b: Box, title_size: int = 24, body_size: int = 18, body_chars: int = 16):
        self.rounded_rect(b.x, b.y, b.w, b.h, fill=b.fill, outline="#D5DED6", radius=b.r, shadow=True)
        self.draw.rounded_rectangle((b.x, b.y, b.x + 10, b.y + b.h), radius=6, fill=hex_to_rgb(b.color))
        self.svg.append(f'<rect x="{b.x:.1f}" y="{b.y:.1f}" width="10" height="{b.h:.1f}" rx="5" fill="{b.color}"/>')
        self.text(b.title, b.x + 28, b.y + 26, size=title_size, color=PALETTE["ink"], weight="bold", max_chars=body_chars + 4)
        if b.body:
            self.text(b.body, b.x + 28, b.y + 68, size=body_size, color=PALETTE["muted"], max_chars=body_chars, line_gap=5)

    def pill(self, x, y, text, color, w=None):
        font = load_font(18)
        tw = self.draw.textbbox((0, 0), text, font=font)[2]
        ww = w or tw + 42
        self.rounded_rect(x, y, ww, 38, fill="#FFFFFF", outline=color, radius=19, width=2)
        self.text(text, x + 20, y + 9, size=18, color=color, weight="bold")

    def save(self, stem: str):
        self.svg.append("</svg>")
        (OUT / f"{stem}.svg").write_text("\n".join(self.svg), encoding="utf-8")
        self.img.save(OUT / f"{stem}.png")


def connect(c: Canvas, a: Box, b: Box, label: str = "", color: str = "#6C7A72"):
    x1, y1 = a.cx, a.y + a.h
    x2, y2 = b.cx, b.y
    if abs(y2 - y1) > 50:
        mid = (y1 + y2) / 2
        c.polyline([(x1, y1), (x1, mid), (x2, mid), (x2, y2)], color=color, width=3, arrow=True)
        if label:
            c.text(label, (x1 + x2) / 2 - 36, mid - 22, size=16, color=color)
    else:
        c.line(x1, y1, x2, y2, color=color, width=3, arrow=True)


def diagram_01():
    c = Canvas(title="系统定位与产业化演进路线")
    c.text("从可运行 WebGIS 原型，演进为可维护、可复用、可交付的风味知识服务。", 72, 132, size=22, color=PALETTE["muted"])
    stages = [
        Box(90, 250, 300, 250, "当前原型", "地图探索\n风味节点\n叙事章节\n食材传播", PALETTE["teal"]),
        Box(460, 250, 300, 250, "数据资产层", "风味基因型\n生态区映射\n传播事件\n来源与置信度", PALETTE["green"]),
        Box(830, 250, 300, 250, "内容服务层", "专题地图\n叙事模板\n接口输出\n审核发布", PALETTE["amber"]),
        Box(1200, 250, 300, 250, "行业场景层", "文旅展陈\n研学课程\n地方品牌\n内容出版", PALETTE["red"]),
    ]
    for b in stages:
        c.box(b, body_chars=10)
    for a, b in zip(stages, stages[1:]):
        c.line(a.x + a.w + 22, a.cy, b.x - 18, b.cy, color="#6C7A72", width=4, arrow=True)
    c.rounded_rect(160, 650, 1280, 150, fill="#FFFFFF", outline="#D5DED6", radius=28, shadow=True)
    c.text("关键约束", 210, 692, size=26, color=PALETTE["ink"], weight="bold")
    c.text("不是餐馆点评或交易系统；核心资产是可追溯的风味知识、空间关系和专题内容生产流程。", 350, 695, size=24, color=PALETTE["muted"], max_chars=45)
    c.pill(210, 760, "来源可查", PALETTE["green"])
    c.pill(390, 760, "字段统一", PALETTE["teal"])
    c.pill(570, 760, "审核发布", PALETTE["amber"])
    c.pill(750, 760, "接口复用", PALETTE["blue"])
    c.pill(930, 760, "专题交付", PALETTE["red"])
    c.save("01_系统定位与产业化演进路线")


def diagram_02():
    c = Canvas(title="核心业务对象关系图")
    center = Box(635, 390, 330, 170, "风味基因型记录", "地方食物版本\n六维风味向量\n坐标与展示属性", PALETTE["green"])
    boxes = [
        Box(110, 200, 300, 150, "生态地理单元", "TEOW 生态区\n自然空间容器", PALETTE["leaf"]),
        Box(1120, 200, 300, 150, "食材", "标准名称\n类型与风味标签", PALETTE["amber"]),
        Box(110, 650, 300, 150, "传播事件", "路线几何\n媒介与时期", PALETTE["red"]),
        Box(1120, 650, 300, 150, "叙事章节", "标题、正文\n引用与路线关联", PALETTE["purple"]),
        Box(635, 150, 330, 150, "数据来源", "地图、生态区\n图片与文本材料", PALETTE["blue"]),
        Box(635, 690, 330, 150, "食材传播专题", "起源、时间线\n路径段与参考文献", PALETTE["teal"]),
    ]
    for b in boxes + [center]:
        c.box(b, body_chars=12)
    relations = [
        (boxes[0], center, "空间归属"),
        (boxes[1], center, "配方连结"),
        (boxes[2], center, "传播上下文"),
        (center, boxes[3], "章节解释"),
        (boxes[4], center, "来源支撑"),
        (boxes[5], boxes[2], "专题路径"),
    ]
    for a, b, lab in relations:
        c.line(a.cx, a.cy, b.cx, b.cy, color="#6C7A72", width=3, arrow=True)
        c.text(lab, (a.cx + b.cx) / 2 - 38, (a.cy + b.cy) / 2 - 18, size=15, color=PALETTE["muted"])
    c.save("02_核心业务对象关系图")


def diagram_03():
    c = Canvas(title="系统总体架构图")
    lanes = [
        ("展示层", 145, "#EAF2EA"),
        ("服务层", 375, "#EEF4F8"),
        ("数据层", 625, "#F8F1E4"),
    ]
    for name, y, fill in lanes:
        c.rounded_rect(70, y, 1460, 180, fill=fill, outline="#D5DED6", radius=26)
        c.text(name, 95, y + 28, size=26, color=PALETTE["ink"], weight="bold")
    top = [
        Box(220, 180, 230, 105, "Vue SPA", "Router / Pinia", PALETTE["green"]),
        Box(510, 180, 230, 105, "MapLibre", "底图与矢量图层", PALETTE["teal"]),
        Box(800, 180, 230, 105, "Deck.gl / ECharts", "路径、节点、雷达图", PALETTE["blue"]),
        Box(1090, 180, 230, 105, "专题页面", "食材传播 / 叙事馆", PALETTE["amber"]),
    ]
    mid = [
        Box(240, 420, 260, 105, "Vite / Express", "开发代理与静态托管", PALETTE["purple"]),
        Box(610, 420, 260, 105, "FastAPI", "业务 API / 健康检查", PALETTE["green"]),
        Box(980, 420, 260, 105, "瓦片与矢量服务", "raster / GeoJSON / MVT", PALETTE["teal"]),
    ]
    bot = [
        Box(150, 650, 260, 130, "PostgreSQL/PostGIS", "空间几何\n业务关系", PALETTE["green"]),
        Box(500, 650, 260, 130, "GIS 基础数据", "HYP 底图\n海岸线 / 河流\nTEOW 生态区", PALETTE["blue"]),
        Box(850, 650, 260, 130, "食材专题 JSON", "timeline\nsegments\nreferences", PALETTE["amber"]),
        Box(1200, 650, 260, 130, "LLM 数据管线", "抽取\n校验\n审核与导入", PALETTE["red"]),
    ]
    for b in top + mid + bot:
        c.box(b, title_size=21, body_size=16, body_chars=13)
    for b in top:
        c.line(b.cx, b.y + b.h + 20, 740, 405, color="#6C7A72", width=3, arrow=True)
    c.line(500, 475, 610, 475, color="#6C7A72", width=3, arrow=True)
    c.line(870, 475, 980, 475, color="#6C7A72", width=3, arrow=True)
    for b in bot[:3]:
        c.line(740, 535, b.cx, b.y - 20, color="#6C7A72", width=3, arrow=True)
    c.line(bot[3].cx, bot[3].y - 20, 740, 535, color=PALETTE["red"], width=3, arrow=True, dash=True)
    c.text("后续扩展", 1110, 590, size=18, color=PALETTE["red"], weight="bold")
    c.save("03_系统总体架构图")


def diagram_04():
    c = Canvas(title="数据生产与审核闭环图")
    steps = [
        Box(70, 310, 210, 150, "语料来源", "菜谱、地方志\n古籍、论文、图片", PALETTE["blue"]),
        Box(315, 310, 210, 150, "结构化抽取", "LLM 辅助\n字段初填", PALETTE["purple"]),
        Box(560, 310, 210, 150, "格式校验", "Schema\n坐标、枚举、范围", PALETTE["teal"]),
        Box(805, 310, 210, 150, "人工审核", "来源核对\n争议与置信度", PALETTE["amber"]),
        Box(1050, 310, 210, 150, "入库发布", "PostGIS / JSON\n版本冻结", PALETTE["green"]),
        Box(1295, 310, 210, 150, "前端呈现", "地图、专题\n叙事与接口", PALETTE["red"]),
    ]
    for b in steps:
        c.box(b, title_size=22, body_size=17, body_chars=10)
    for a, b in zip(steps, steps[1:]):
        c.line(a.x + a.w + 14, a.cy, b.x - 12, b.cy, color="#6C7A72", width=3, arrow=True)
    c.polyline([(1400, 485), (1400, 665), (180, 665), (180, 485)], color="#9AA8A0", width=3, arrow=True, dash=True)
    c.text("用户反馈 / 内容复核 / 新资料补证", 505, 690, size=24, color=PALETTE["muted"], weight="bold")
    c.rounded_rect(230, 160, 1140, 75, fill="#FFFFFF", outline="#D5DED6", radius=24, shadow=True)
    c.text("核心原则：LLM 提高生产效率，但公开展示数据必须经过来源、坐标、字段和文字审核。", 280, 183, size=24, color=PALETTE["ink"])
    c.save("04_数据生产与审核闭环图")


def diagram_05():
    c = Canvas(title="数据库核心实体 E-R 图")
    entities = [
        Box(90, 170, 330, 190, "eco_geo_unit", "eco_name PK\nboundary\nbiome / realm\narea_km2", PALETTE["leaf"]),
        Box(630, 160, 340, 210, "flavor_genotype", "genotype_id PK\nnode_key\ndish_name\ngenome_vector\ncoordinates", PALETTE["green"]),
        Box(1180, 170, 330, 190, "ingredient", "ingredient_id PK\nname / type\nflavor_tags", PALETTE["amber"]),
        Box(90, 600, 330, 190, "dispersal_event", "event_id PK\nroute_name\nroute_geom\nfrom_eco / to_eco", PALETTE["red"]),
        Box(630, 600, 340, 190, "recipe_link", "genotype_id FK\ningredient_id FK\nrole\nimportance", PALETTE["teal"]),
        Box(1180, 600, 330, 190, "chapter", "chapter_id PK\ntitle / body\nroute_name FK", PALETTE["purple"]),
    ]
    for e in entities:
        c.box(e, title_size=21, body_size=17, body_chars=16)
    eco, geno, ing, evt, recipe, chap = entities
    c.line(eco.x + eco.w, eco.cy, geno.x, geno.cy, color="#6C7A72", width=3, arrow=True)
    c.text("1 : N", 500, 245, size=18, color=PALETTE["muted"], weight="bold")
    c.line(geno.x + geno.w, geno.cy, ing.x, ing.cy, color="#6C7A72", width=3, arrow=True)
    c.text("M : N", 1030, 245, size=18, color=PALETTE["muted"], weight="bold")
    c.line(geno.cx, geno.y + geno.h, recipe.cx, recipe.y, color="#6C7A72", width=3, arrow=True)
    c.line(ing.cx, ing.y + ing.h, recipe.x + recipe.w, recipe.cy, color="#6C7A72", width=3, arrow=True)
    c.line(evt.x + evt.w, evt.cy, chap.x, chap.cy, color="#6C7A72", width=3, arrow=True)
    c.text("route_name", 1018, 690, size=17, color=PALETTE["muted"])
    c.polyline([(eco.cx, eco.y + eco.h), (eco.cx, 500), (evt.cx, 500), (evt.cx, evt.y)], color="#8FA097", width=3, arrow=True)
    c.text("from / to eco", 235, 510, size=17, color=PALETTE["muted"])
    c.rounded_rect(520, 425, 560, 90, fill="#FFFFFF", outline="#D5DED6", radius=24, shadow=True)
    c.text("关联表把多对多关系变成可查询、可审核、可扩展的数据结构", 565, 455, size=21, color=PALETTE["ink"], max_chars=30)
    c.save("05_数据库核心实体ER图")


def diagram_06():
    c = Canvas(title="系统功能模块结构图")
    center = Box(600, 390, 400, 170, "寻味地理 WebGIS", "地图组织知识\n路线讲述传播\n专题沉淀内容", PALETTE["green"])
    modules = [
        Box(90, 170, 300, 135, "首页模块", "主题识别\n进入地图", PALETTE["blue"]),
        Box(650, 145, 300, 135, "地图探索模块", "节点、路线、生态区\n详情面板", PALETTE["teal"]),
        Box(1210, 170, 300, 135, "风味基因库", "卡片浏览\n分类比较", PALETTE["amber"]),
        Box(90, 680, 300, 135, "时空叙事馆", "章节阅读\n路线关联", PALETTE["purple"]),
        Box(650, 715, 300, 135, "食材传播模块", "时间线播放\n路径可视化", PALETTE["red"]),
        Box(1210, 680, 300, 135, "关于与方法", "来源说明\n数据边界", PALETTE["leaf"]),
    ]
    c.box(center, title_size=26, body_size=18, body_chars=13)
    for m in modules:
        c.box(m, title_size=22, body_size=17, body_chars=11)
        c.line(center.cx, center.cy, m.cx, m.cy, color="#6C7A72", width=3, arrow=True)
    c.pill(535, 595, "全局搜索", PALETTE["green"])
    c.pill(705, 595, "Pinia 状态", PALETTE["teal"])
    c.pill(895, 595, "图表组件", PALETTE["blue"])
    c.save("06_系统功能模块结构图")


def diagram_07():
    c = Canvas(title="接口调用与数据流图")
    pages = [
        Box(90, 185, 250, 120, "地图页", "flavors\nroutes\ntiles", PALETTE["green"]),
        Box(90, 345, 250, 120, "食材传播页", "ingredients\nspread\npath", PALETTE["red"]),
        Box(90, 505, 250, 120, "叙事 / 基因库", "chapters\nsearch\nflavors", PALETTE["purple"]),
    ]
    api = [
        Box(520, 185, 280, 120, "业务 API", "flavors\nroutes\nchapters / search", PALETTE["green"]),
        Box(520, 345, 280, 120, "食材传播 API", "list\ndetail\npath", PALETTE["red"]),
        Box(520, 505, 280, 120, "瓦片 API", "raster\nvector / mvt", PALETTE["teal"]),
    ]
    services = [
        Box(960, 175, 280, 135, "PostGIS 查询层", "空间索引\n关系查询\nJSONB 字段", PALETTE["green"]),
        Box(960, 340, 280, 135, "专题数据读取", "ingredient JSON\n时间线\n路径段", PALETTE["amber"]),
        Box(960, 505, 280, 135, "瓦片渲染服务", "rio-tiler\nGeoJSON / MVT\nLRU cache", PALETTE["teal"]),
    ]
    sources = [
        Box(1320, 175, 210, 135, "数据库", "PostgreSQL\nPostGIS", PALETTE["green"]),
        Box(1320, 340, 210, 135, "数据文件", "JSON\nGeoTIFF\nShapefile", PALETTE["amber"]),
        Box(1320, 505, 210, 135, "浏览器渲染", "MapLibre\nECharts", PALETTE["blue"]),
    ]
    for b in pages + api + services + sources:
        c.box(b, title_size=20, body_size=15, body_chars=12)
    for p in pages:
        for a in api:
            if (p.title == "地图页" and a.title in ("业务 API", "瓦片 API")) or (p.title == "食材传播页" and a.title == "食材传播 API") or (p.title == "叙事 / 基因库" and a.title == "业务 API"):
                c.line(p.x + p.w + 15, p.cy, a.x - 15, a.cy, color="#6C7A72", width=3, arrow=True)
    for a, s in zip(api, services):
        c.line(a.x + a.w + 18, a.cy, s.x - 15, s.cy, color="#6C7A72", width=3, arrow=True)
    for s, src in zip(services, sources):
        c.line(s.x + s.w + 18, s.cy, src.x - 15, src.cy, color="#6C7A72", width=3, arrow=True)
    c.rounded_rect(470, 735, 760, 90, fill="#FFFFFF", outline="#D5DED6", radius=24, shadow=True)
    c.text("接口设计原则：前端消费稳定展示对象，服务层负责屏蔽数据库表结构和数据文件差异。", 515, 765, size=22, color=PALETTE["ink"], max_chars=34)
    c.save("07_接口调用与数据流图")


def diagram_08():
    c = Canvas(title="页面信息架构与导航流转图")
    home = Box(665, 145, 270, 105, "首页", "主题识别\n进入地图", PALETTE["green"])
    pages = [
        Box(100, 390, 260, 130, "探索地图", "图层、搜索\n详情面板", PALETTE["teal"]),
        Box(420, 390, 260, 130, "风味基因库", "卡片筛选\n跳转地图", PALETTE["amber"]),
        Box(740, 390, 260, 130, "时空叙事馆", "章节阅读\n路线关联", PALETTE["purple"]),
        Box(1060, 390, 260, 130, "食材传播", "时间线\n路径播放", PALETTE["red"]),
        Box(580, 670, 260, 130, "关于与方法", "来源、边界\n数据生产说明", PALETTE["leaf"]),
    ]
    c.box(home, title_size=23, body_size=17, body_chars=10)
    for p in pages:
        c.box(p, title_size=22, body_size=17, body_chars=10)
        c.line(home.cx, home.y + home.h + 15, p.cx, p.y - 15, color="#6C7A72", width=3, arrow=True)
    c.line(pages[1].cx, pages[1].y + pages[1].h, pages[0].cx + 60, pages[0].y + pages[0].h, color=PALETTE["amber"], width=3, arrow=True, dash=True)
    c.text("卡片定位", 330, 565, size=17, color=PALETTE["amber"], weight="bold")
    c.line(pages[2].cx, pages[2].y + pages[2].h, pages[0].cx + 160, pages[0].y + pages[0].h, color=PALETTE["purple"], width=3, arrow=True, dash=True)
    c.text("章节看路线", 610, 582, size=17, color=PALETTE["purple"], weight="bold")
    c.line(pages[3].x, pages[3].cy, pages[0].x + pages[0].w, pages[0].cy, color=PALETTE["red"], width=3, arrow=True, dash=True)
    c.text("专题路径复用地图能力", 675, 345, size=18, color=PALETTE["red"], weight="bold")
    c.rounded_rect(985, 675, 395, 120, fill="#FFFFFF", outline="#D5DED6", radius=24, shadow=True)
    c.text("移动端策略", 1030, 708, size=23, color=PALETTE["ink"], weight="bold")
    c.text("地图面板转底部抽屉；播放控制固定底部；正文保持单列阅读。", 1030, 745, size=18, color=PALETTE["muted"], max_chars=19)
    c.save("08_页面信息架构与导航流转图")


def write_recommendations():
    md = """# 寻味地理总体设计文档配图建议

本文件夹中的图片按“现代工程文档图”的方式绘制，均提供 `.svg` 和 `.png` 两种格式。SVG 便于后续编辑，PNG 便于直接插入 Word。

## 建议插图位置

| 图号 | 文件名 | 建议插入位置 | 作用 |
| --- | --- | --- | --- |
| 图1 | `01_系统定位与产业化演进路线` | `01-系统概况`，系统目标之后 | 说明项目不是普通美食地图，而是从 WebGIS 原型演进为风味知识服务。 |
| 图2 | `02_核心业务对象关系图` | `02-需求规定`，风味业务数据或数据需求之后 | 把生态区、风味节点、食材、传播事件、叙事章节和专题数据之间的关系讲清楚。 |
| 图3 | `03_系统总体架构图` | `03-总体设计`，系统建设架构之后 | 对应参考书常见的“系统结构图”，但改为前端、服务层、数据层的现代 WebGIS 架构。 |
| 图4 | `04_数据生产与审核闭环图` | `03-总体设计` 的数据扩展与维护方案之后，或 `01-系统概况` 的数据生产管线处 | 表达产业化最关键的数据质量闭环：抽取只是开始，审核和发布才是重点。 |
| 图5 | `05_数据库核心实体ER图` | `04-数据库设计`，系统业务数据库概念模型之后 | 替代旧范本里常见的传统 E-R 图，突出 PostGIS 空间实体和业务实体关系。 |
| 图6 | `06_系统功能模块结构图` | `05-系统功能设计`，系统划分之后 | 对应参考书常见的功能结构图，展示公众端模块和通用能力。 |
| 图7 | `07_接口调用与数据流图` | `06-系统接口设计`，前后端接口设计之后 | 说明浏览器页面、API、查询层、数据库和数据文件之间的数据流。 |
| 图8 | `08_页面信息架构与导航流转图` | `07-界面设计`，整体布局或响应式布局策略之前 | 说明首页、地图、基因库、叙事馆、食材传播和关于页之间如何流转。 |

## 为什么没有照抄参考书旧图

参考设计书的图主要起“结构说明”和“位置示范”作用，绘图语言偏老：常见的是粗边框、普通流程框、单线箭头和传统 E-R 表达。本项目更适合采用分层架构图、数据闭环图、对象关系图和页面信息架构图，既能对齐软件工程文档规范，又更符合 WebGIS、数据资产和专题内容产品的项目实际。
"""
    (OUT / "配图建议.md").write_text(md, encoding="utf-8")


def main():
    diagram_01()
    diagram_02()
    diagram_03()
    diagram_04()
    diagram_05()
    diagram_06()
    diagram_07()
    diagram_08()
    write_recommendations()
    print(OUT)


if __name__ == "__main__":
    main()
