# TODO：数据库结构变更记录

## 本次结构调整

1. 将“风味基因型”从独立成品实体调整为菜肴成品的属性：
   - 原 `flavor_genotype` 表更名为 `dish`；
   - 原 `genotype_id` 主键更名为 `dish_id`；
   - 原 `genome_vector` 字段更名为 `flavor_genotype`，表示菜肴成品的六维风味向量。

2. 调整菜肴与原材料的关联关系：
   - `recipe_link.genotype_id` 更名为 `recipe_link.dish_id`；
   - `recipe_link.dish_id` 外键引用 `dish(dish_id)`；
   - `recipe_link` 仍作为菜肴成品与原材料之间的多对多关联实体，保留 `role`、`importance`、`is_native` 等关系属性。

3. 调整菜肴溯源关系：
   - 原 `genotype_lineage` 表更名为 `dish_lineage`；
   - 原 `ancestor_id` / `descendant_id` 更名为 `ancestor_dish_id` / `descendant_dish_id`；
   - 两个字段均引用 `dish(dish_id)`，用于表达菜肴成品之间的自引用演化关系。

4. 同步更新索引命名：
   - 原 `idx_genotype_*` 系列索引更名为 `idx_dish_*`；
   - 六维风味向量字段索引调整为 `idx_dish_flavor`。

## 后续同步事项

1. 同步数据库导入与种子数据流程中所有 `flavor_genotype`、`genotype_id`、`genome_vector`、`genotype_lineage` 引用。
2. 同步业务查询层中与菜肴、配方连结、搜索、风味向量读取相关的 SQL。
3. 同步迁移校验中的表名、字段名和预期记录数。
4. 同步总体设计修改文档中的数据库设计、需求规定、功能设计和接口字段说明。
5. 同步 ER 图中菜肴成品、配方连结和菜肴溯源链的字段命名。
6. 同步前后端接口字段口径：对外展示仍可使用风味节点概念，但数据库实体应称为菜肴成品。

## 命名口径

- “菜肴成品”是数据库核心实体，与原材料相对应。
- “风味基因型”特指菜肴成品的六维风味向量属性，不再作为独立成品实体名称。
- “配方连结”是菜肴成品与原材料之间的关联实体。
- “菜肴溯源链”是菜肴成品之间的自引用关联实体。
