# JSON 入库说明

导入脚本： [backend/db/import_json.py](</E:/大学/大三下/GIS开发/Food/backend/db/import_json.py>)

模板目录： [backend/data/templates](</E:/大学/大三下/GIS开发/Food/backend/data/templates>)

## 命令

初始化 schema 后导入：

```powershell
.\.venv\Scripts\python.exe -m backend.db.import_json .\your-data.json --init-schema
```

从目录导入四个实体文件：

```powershell
.\.venv\Scripts\python.exe -m backend.db.import_json .\backend\data\templates
```

仅替换业务数据：

```powershell
.\.venv\Scripts\python.exe -m backend.db.import_json .\your-data.json
```

保留现有记录，只补缺失：

```powershell
.\.venv\Scripts\python.exe -m backend.db.import_json .\your-data.json --keep-existing
```

## 顶层结构

```json
{
  "flavors": [],
  "routes": [],
  "chapters": [],
  "dataSources": []
}
```

也兼容这些别名：

- `FLAVORS`
- `ROUTES`
- `CHAPTERS`
- `DATA_SOURCES`
- `data_sources`

## 四文件目录模式

也可以不给一个总 bundle，而是提供一个目录，目录内放这四个文件：

- `flavor_genotype.json`
- `dispersal_event.json`
- `chapter.json`
- `data_source.json`

也兼容这些文件名别名：

- `flavors.json`
- `routes.json`
- `chapters.json`
- `data_sources.json`

关系表不需要手写。导入时后端会自动构建：

- `ingredient`
- `ingredient_origin`
- `recipe_link`

## flavors 项

```json
{
  "id": "chengdu-mala",
  "city": "成都",
  "dish": "川蜀麻辣",
  "dish_family": "火锅",
  "region": "四川盆地",
  "eco": "亚热带常绿阔叶林",
  "eco_name": "Sichuan Basin evergreen broadleaf forests",
  "scores": [0.9, 0.95, 0.65, 0.3, 0.2, 0.7],
  "primary": ["麻", "辣"],
  "vals": [0.9, 0.95],
  "color": "#E5394E",
  "cat": "辛辣",
  "ingredients": ["花椒", "朝天椒", "郫县豆瓣", "井盐"],
  "coordinates": [104.1, 30.7]
}
```

说明：

- `scores` 固定 6 维
- `coordinates` 固定 `[lng, lat]`
- `eco_name` 可选；不传时会按现有代码中的生态区映射兜底

## routes 项

```json
{
  "name": "丝绸之路",
  "color": "#E8A917",
  "type": "land",
  "ingredient_name": "茶叶",
  "path": [[108.9, 34.3], [94.7, 40.1], [75.9, 39.5]]
}
```

说明：

- `type` 只能是 `land` 或 `sea`
- `ingredient_name` 建议显式传；不传时会走代码中的默认路线-原料映射

## chapters 项

```json
{
  "id": 1,
  "title": "大运河漕运",
  "date": "公元605年 · 隋朝",
  "body": "正文",
  "cite": "引文",
  "source": "来源",
  "routeName": "大运河·茶叶北行"
}
```

## dataSources 项

```json
{
  "name": "Natural Earth Data",
  "desc": "数据来源描述",
  "color": "#E8A917",
  "url": "https://www.naturalearthdata.com"
}
```
