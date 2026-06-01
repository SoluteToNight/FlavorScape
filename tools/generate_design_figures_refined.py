from __future__ import annotations

from pathlib import Path

import generate_design_figures as base
from generate_design_figures import Box, Canvas, PALETTE


OUT = base.OUT


def draw_all(boxes: list[Box], c: Canvas, title_size: int = 22, body_size: int = 17, chars: int = 12) -> None:
    for box in boxes:
        c.box(box, title_size=title_size, body_size=body_size, body_chars=chars)


def h_arrow(c: Canvas, a: Box, b: Box, y: float | None = None, color: str = "#6C7A72", label: str = "") -> None:
    yy = y if y is not None else a.cy
    c.line(a.x + a.w + 18, yy, b.x - 18, yy, color=color, width=3, arrow=True)
    if label:
        c.text(label, (a.x + a.w + b.x) / 2 - 28, yy - 30, size=16, color=color, weight="bold")


def v_arrow(c: Canvas, a: Box, b: Box, x: float | None = None, color: str = "#6C7A72", label: str = "") -> None:
    xx = x if x is not None else a.cx
    c.line(xx, a.y + a.h + 18, xx, b.y - 18, color=color, width=3, arrow=True)
    if label:
        c.text(label, xx + 18, (a.y + a.h + b.y) / 2 - 8, size=16, color=color, weight="bold")


def ortho_arrow(c: Canvas, pts: list[tuple[float, float]], color: str = "#6C7A72", label: str = "", label_xy: tuple[float, float] | None = None, dash: bool = False) -> None:
    c.polyline(pts, color=color, width=3, arrow=True, dash=dash)
    if label and label_xy:
        c.text(label, label_xy[0], label_xy[1], size=16, color=color, weight="bold")


def diagram_02() -> None:
    c = Canvas(title="核心业务对象关系图")
    c.text("围绕同一批风味知识对象，组织生态背景、食材来源、传播过程、叙事解释和数据来源。", 72, 132, size=21, color=PALETTE["muted"])

    source = Box(620, 170, 360, 140, "数据来源", "地图、生态区\n图片与文本材料\n文献与地方志", PALETTE["blue"])
    eco = Box(105, 380, 330, 145, "生态地理单元", "TEOW 生态区\n自然空间容器", PALETTE["leaf"])
    genotype = Box(620, 370, 360, 170, "风味基因型记录", "地方食物版本\n六维风味向量\n坐标与展示属性", PALETTE["green"])
    ingredient = Box(1165, 380, 330, 145, "食材", "标准名称\n类型与风味标签", PALETTE["amber"])
    event = Box(105, 680, 330, 145, "传播事件", "路线几何\n媒介与时期\n起止生态区", PALETTE["red"])
    spread = Box(620, 675, 360, 155, "食材传播专题", "起源、时间线\n路径段与参考文献\n可复用专题模板", PALETTE["teal"])
    chapter = Box(1165, 680, 330, 145, "叙事章节", "标题、正文\n引用与路线关联", PALETTE["purple"])

    boxes = [source, eco, genotype, ingredient, event, spread, chapter]
    draw_all(boxes, c, title_size=22, body_size=17, chars=12)

    v_arrow(c, source, genotype, color=PALETTE["blue"], label="来源支撑")
    h_arrow(c, eco, genotype, color=PALETTE["leaf"], label="空间归属")
    h_arrow(c, genotype, ingredient, color=PALETTE["amber"], label="配方连接")
    h_arrow(c, event, spread, color=PALETTE["teal"], label="专题路径")
    h_arrow(c, spread, chapter, color=PALETTE["purple"], label="章节解释")
    ortho_arrow(c, [(270, 662), (270, 585), (680, 585), (680, 558)], color=PALETTE["red"], label="传播上下文", label_xy=(355, 555))
    c.rounded_rect(455, 875, 690, 65, fill="#FFFFFF", outline="#D5DED6", radius=22, shadow=True)
    c.text("图中对象既对应当前数据结构，也为后续数据审核、专题交付和接口复用预留边界。", 500, 898, size=20, color=PALETTE["ink"])
    c.save("02_核心业务对象关系图")


def diagram_03() -> None:
    c = Canvas(title="系统总体架构图")
    lanes = [
        ("展示层", 150, "#EAF2EA"),
        ("服务层", 385, "#EEF4F8"),
        ("数据层", 620, "#F8F1E4"),
    ]
    for name, y, fill in lanes:
        c.rounded_rect(70, y, 1460, 175, fill=fill, outline="#D5DED6", radius=26)
        c.text(name, 95, y + 27, size=25, color=PALETTE["ink"], weight="bold")

    top = [
        Box(205, 185, 250, 105, "Vue SPA", "Router\nPinia 状态", PALETTE["green"]),
        Box(520, 185, 250, 105, "MapLibre", "底图\n矢量图层", PALETTE["teal"]),
        Box(835, 185, 250, 105, "Deck.gl / ECharts", "路径、节点\n雷达图", PALETTE["blue"]),
        Box(1150, 185, 250, 105, "专题页面", "食材传播\n叙事馆", PALETTE["amber"]),
    ]
    mid = [
        Box(205, 420, 250, 110, "Vite / Express", "开发代理\n静态托管", PALETTE["purple"]),
        Box(520, 420, 250, 110, "FastAPI", "业务 API\n健康检查", PALETTE["green"]),
        Box(835, 420, 250, 110, "瓦片与矢量服务", "raster\nGeoJSON / MVT", PALETTE["teal"]),
        Box(1150, 420, 250, 110, "专题数据服务", "ingredient\nchapters", PALETTE["amber"]),
    ]
    bot = [
        Box(205, 655, 250, 125, "PostgreSQL/PostGIS", "空间几何\n业务关系\n索引查询", PALETTE["green"]),
        Box(520, 655, 250, 125, "GIS 基础数据", "HYP 底图\n海岸线 / 河流\nTEOW 生态区", PALETTE["blue"]),
        Box(835, 655, 250, 125, "食材专题 JSON", "timeline\nsegments\nreferences", PALETTE["amber"]),
        Box(1150, 655, 250, 125, "数据生产管线", "抽取\n校验\n审核与导入", PALETTE["red"]),
    ]

    draw_all(top + mid + bot, c, title_size=20, body_size=15, chars=12)

    h_arrow(c, mid[0], mid[1])
    h_arrow(c, mid[1], mid[2])
    h_arrow(c, mid[2], mid[3])
    for a, b in zip(top, mid):
        v_arrow(c, a, b)
    v_arrow(c, mid[1], bot[0], x=645)
    v_arrow(c, mid[2], bot[1], x=960)
    v_arrow(c, mid[3], bot[2], x=1275)
    ortho_arrow(c, [(1275, 637), (1275, 590), (1275, 590), (1275, 548)], color=PALETTE["red"], label="发布后消费", label_xy=(1292, 585), dash=True)

    c.rounded_rect(275, 850, 1050, 65, fill="#FFFFFF", outline="#D5DED6", radius=22, shadow=True)
    c.text("三层边界保持稳定：前端消费展示对象，服务层转换数据口径，数据层沉淀空间与业务资产。", 320, 873, size=20, color=PALETTE["ink"])
    c.save("03_系统总体架构图")


def diagram_05() -> None:
    c = Canvas(title="数据库核心实体 E-R 图")
    eco = Box(90, 175, 330, 185, "eco_geo_unit", "eco_name PK\nboundary\nbiome / realm\narea_km2", PALETTE["leaf"])
    geno = Box(635, 160, 340, 210, "flavor_genotype", "genotype_id PK\nnode_key\ndish_name\ngenome_vector\ncoordinates", PALETTE["green"])
    ing = Box(1180, 175, 330, 185, "ingredient", "ingredient_id PK\nname / type\nflavor_tags", PALETTE["amber"])
    evt = Box(90, 615, 330, 185, "dispersal_event", "event_id PK\nroute_name\nroute_geom\nfrom_eco / to_eco", PALETTE["red"])
    recipe = Box(635, 615, 340, 185, "recipe_link", "genotype_id FK\ningredient_id FK\nrole\nimportance", PALETTE["teal"])
    chap = Box(1180, 615, 330, 185, "chapter", "chapter_id PK\ntitle / body\nroute_name FK", PALETTE["purple"])

    draw_all([eco, geno, ing, evt, recipe, chap], c, title_size=21, body_size=17, chars=16)

    h_arrow(c, eco, geno, color=PALETTE["leaf"], label="1 : N")
    h_arrow(c, geno, ing, color=PALETTE["amber"], label="M : N")
    v_arrow(c, eco, evt, x=255, color=PALETTE["red"], label="from / to eco")
    v_arrow(c, geno, recipe, x=805, color=PALETTE["teal"], label="FK")
    ortho_arrow(c, [(1345, 378), (1345, 535), (995, 535), (995, 708)], color=PALETTE["amber"], label="FK", label_xy=(1045, 510))
    ortho_arrow(c, [(420, 708), (520, 708), (520, 865), (1345, 865), (1345, 820)], color=PALETTE["purple"], label="route_name", label_xy=(930, 835))

    c.rounded_rect(510, 430, 580, 92, fill="#FFFFFF", outline="#D5DED6", radius=24, shadow=True)
    c.text("关联表把多对多关系变成可查询、可审核、可扩展的数据结构。", 560, 462, size=21, color=PALETTE["ink"])
    c.save("05_数据库核心实体ER图")


def diagram_06() -> None:
    c = Canvas(title="系统功能模块结构图")
    root = Box(570, 155, 460, 145, "寻味地理 WebGIS", "以地图组织风味知识\n以路线讲述传播过程\n以专题沉淀内容资产", PALETTE["green"])
    support = Box(505, 370, 590, 115, "通用支撑能力", "导航 / 搜索 / 选中状态\n图层控制 / 图表组件", PALETTE["teal"])
    modules = [
        Box(100, 600, 300, 135, "首页模块", "主题识别\n进入地图", PALETTE["blue"]),
        Box(450, 600, 300, 135, "地图探索模块", "节点、路线、生态区\n详情面板", PALETTE["teal"]),
        Box(800, 600, 300, 135, "风味基因库", "卡片浏览\n分类比较", PALETTE["amber"]),
        Box(1150, 600, 300, 135, "时空叙事馆", "章节阅读\n路线关联", PALETTE["purple"]),
        Box(275, 790, 300, 135, "食材传播模块", "时间线播放\n路径可视化", PALETTE["red"]),
        Box(1025, 790, 300, 135, "关于与方法", "来源说明\n数据边界", PALETTE["leaf"]),
    ]

    c.box(root, title_size=22, body_size=17, body_chars=14)
    c.box(support, title_size=22, body_size=17, body_chars=26)
    draw_all(modules, c, title_size=22, body_size=17, chars=14)
    v_arrow(c, root, support, color=PALETTE["green"])
    for mod in modules[:4]:
        ortho_arrow(c, [(support.cx, support.y + support.h + 16), (support.cx, 550), (mod.cx, 550), (mod.cx, mod.y - 18)], color="#6C7A72")
    for mod in modules[4:]:
        ortho_arrow(c, [(support.cx, support.y + support.h + 16), (support.cx, 760), (mod.cx, 760), (mod.cx, mod.y - 18)], color="#6C7A72")

    c.pill(455, 510, "公共组件复用", PALETTE["green"], w=160)
    c.pill(635, 510, "状态联动", PALETTE["teal"], w=140)
    c.pill(795, 510, "专题可扩展", PALETTE["red"], w=160)
    c.save("06_系统功能模块结构图")


def diagram_07() -> None:
    c = Canvas(title="接口调用与数据流图")
    c.text("按页面使用场景分行表达，避免把浏览器、API、查询层和数据源混在同一条线上。", 72, 132, size=21, color=PALETTE["muted"])
    headers = [("浏览器页面", 90), ("服务接口", 455), ("服务内部处理", 820), ("数据源 / 渲染", 1185)]
    for title, x in headers:
        c.text(title, x, 180, size=22, color=PALETTE["ink"], weight="bold")

    rows = [
        (
            Box(90, 245, 270, 135, "地图探索页", "flavors\nroutes\nsearch", PALETTE["green"]),
            Box(455, 245, 270, 135, "业务 API", "/api/flavors\n/api/routes\n/api/search", PALETTE["green"]),
            Box(820, 245, 270, 135, "PostGIS 查询层", "空间索引\n关系查询\n展示对象组装", PALETTE["green"]),
            Box(1185, 245, 270, 135, "数据库", "PostgreSQL\nPostGIS", PALETTE["green"]),
        ),
        (
            Box(90, 425, 270, 135, "食材传播页", "ingredient list\ndetail\npath playback", PALETTE["red"]),
            Box(455, 425, 270, 135, "传播专题 API", "/ingredients\n/spread/:id\n/timeline", PALETTE["red"]),
            Box(820, 425, 270, 135, "专题数据读取", "时间线\n路径段\n参考文献", PALETTE["amber"]),
            Box(1185, 425, 270, 135, "数据文件", "JSON\nGeoJSON\nreferences", PALETTE["amber"]),
        ),
        (
            Box(90, 605, 270, 135, "地图渲染请求", "base map\nlayers\ntiles", PALETTE["teal"]),
            Box(455, 605, 270, 135, "瓦片 API", "/tiles/{z}/{x}/{y}\n/vector\n/status", PALETTE["teal"]),
            Box(820, 605, 270, 135, "瓦片渲染服务", "rio-tiler\nGeoJSON / MVT\nLRU cache", PALETTE["teal"]),
            Box(1185, 605, 270, 135, "浏览器渲染", "MapLibre\nDeck.gl\nECharts", PALETTE["blue"]),
        ),
    ]
    for row in rows:
        draw_all(list(row), c, title_size=20, body_size=15, chars=16)
        h_arrow(c, row[0], row[1])
        h_arrow(c, row[1], row[2])
        h_arrow(c, row[2], row[3])

    c.rounded_rect(415, 800, 770, 75, fill="#FFFFFF", outline="#D5DED6", radius=24, shadow=True)
    c.text("接口设计原则：前端消费稳定展示对象，服务层屏蔽数据库表结构和数据文件差异。", 460, 828, size=21, color=PALETTE["ink"])
    c.save("07_接口调用与数据流图")


def diagram_08() -> None:
    c = Canvas(title="页面信息架构与导航流转图")
    home = Box(665, 150, 270, 105, "首页", "主题识别\n进入地图", PALETTE["green"])
    nav = Box(485, 335, 630, 105, "全局导航", "首页 / 地图 / 基因库 / 叙事馆\n食材传播 / 关于与方法", PALETTE["teal"])
    pages = [
        Box(90, 575, 260, 130, "探索地图", "图层、搜索\n详情面板", PALETTE["teal"]),
        Box(405, 575, 260, 130, "风味基因库", "卡片筛选\n跳转地图", PALETTE["amber"]),
        Box(720, 575, 260, 130, "时空叙事馆", "章节阅读\n路线关联", PALETTE["purple"]),
        Box(1035, 575, 260, 130, "食材传播", "时间线\n路径播放", PALETTE["red"]),
        Box(1320, 575, 220, 130, "关于与方法", "来源\n边界\n生产说明", PALETTE["leaf"]),
    ]
    capability = Box(345, 805, 740, 90, "地图能力复用", "地图定位、路线高亮、图层叠加和详情面板由多页面共同调用", PALETTE["green"])

    c.box(home, title_size=21, body_size=16, body_chars=15)
    c.box(nav, title_size=21, body_size=16, body_chars=28)
    draw_all(pages + [capability], c, title_size=21, body_size=16, chars=15)
    v_arrow(c, home, nav, color=PALETTE["green"])
    for page in pages:
        ortho_arrow(c, [(nav.cx, nav.y + nav.h + 16), (nav.cx, 515), (page.cx, 515), (page.cx, page.y - 18)], color="#6C7A72")

    ortho_arrow(c, [(535, 705), (535, 760), (560, 760), (560, 785)], color=PALETTE["amber"], label="卡片定位", label_xy=(395, 735), dash=True)
    ortho_arrow(c, [(850, 705), (850, 760), (770, 760), (770, 785)], color=PALETTE["purple"], label="章节看路线", label_xy=(790, 735), dash=True)
    ortho_arrow(c, [(1165, 705), (1165, 760), (980, 760), (980, 785)], color=PALETTE["red"], label="专题路径复用", label_xy=(1040, 735), dash=True)

    c.rounded_rect(1130, 800, 370, 105, fill="#FFFFFF", outline="#D5DED6", radius=24, shadow=True)
    c.text("移动端策略", 1170, 825, size=21, color=PALETTE["ink"], weight="bold")
    c.text("地图面板转底部抽屉，播放控制固定底部\n正文保持单列阅读。", 1170, 855, size=16, color=PALETTE["muted"])
    c.save("08_页面信息架构与导航流转图")


def write_recommendations() -> None:
    md = """# 寻味地理总体设计文档配图建议

本文件夹中的图片按“现代工程文档图”的方式绘制，均提供 `.svg` 和 `.png` 两种格式。SVG 便于后续编辑，PNG 便于直接插入 Word。

## 建议插图位置

| 图号 | 文件名 | 建议插入位置 | 作用 |
| --- | --- | --- | --- |
| 图 1 | `01_系统定位与产业化演进路线` | `01-系统概况`，系统目标之后 | 说明项目不是普通美食地图，而是从 WebGIS 原型演进为风味知识服务。 |
| 图 2 | `02_核心业务对象关系图` | `02-需求规定`，风味业务数据或数据需求之后 | 讲清生态区、风味节点、食材、传播事件、叙事章节和专题数据之间的关系。 |
| 图 3 | `03_系统总体架构图` | `03-总体设计`，系统建设架构之后 | 替代参考书中常见的系统结构图，表达展示层、服务层和数据层的 WebGIS 架构。 |
| 图 4 | `04_数据生产与审核闭环图` | `03-总体设计` 的数据扩展与维护方案之后，或 `01-系统概况` 的数据生产管线处 | 表达产业化最关键的数据质量闭环：抽取只是开始，审核和发布才是重点。 |
| 图 5 | `05_数据库核心实体ER图` | `04-数据库设计`，业务数据库概念模型之后 | 突出 PostGIS 空间实体、业务实体和关联表之间的关系。 |
| 图 6 | `06_系统功能模块结构图` | `05-系统功能设计`，系统划分之后 | 展示公众端模块与通用支撑能力，避免只罗列页面名称。 |
| 图 7 | `07_接口调用与数据流图` | `06-系统接口设计`，前后端接口设计之后 | 说明浏览器页面、API、查询层、数据库和数据文件之间的数据流。 |
| 图 8 | `08_页面信息架构与导航流转图` | `07-界面设计`，整体布局或响应式布局策略之前 | 说明首页、地图、基因库、叙事馆、食材传播和关于页面之间如何流转。 |

## 绘图取舍

参考设计书中的图主要起“结构说明”和“位置示范”作用，范式偏传统。这里没有照抄旧图，而是改成分层架构图、数据闭环图、对象关系图、E-R 图、接口数据流图和页面信息架构图。这样既符合软件工程设计书的图示要求，也更贴近本项目的 WebGIS、空间数据库、数据资产和专题内容产品方向。
"""
    (OUT / "配图建议.md").write_text(md, encoding="utf-8")


def main() -> None:
    base.diagram_01()
    diagram_02()
    diagram_03()
    base.diagram_04()
    diagram_05()
    diagram_06()
    diagram_07()
    diagram_08()
    write_recommendations()
    print(OUT)


if __name__ == "__main__":
    main()
