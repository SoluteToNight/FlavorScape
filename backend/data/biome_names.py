"""
Canonical BIOME name mapping shared by startup.py (display) and seed.py (DB population).

WWF TEOW biome categories — see https://www.worldwildlife.org/publications/terrestrial-ecoregions-of-the-world
"""

from typing import Dict, Tuple

# biome_number → (English_name, Chinese_name)
BIOME_MAP: Dict[int, Tuple[str, str]] = {
    1:  ("Tropical & Subtropical Moist Broadleaf Forests", "热带亚热带湿润阔叶林"),
    2:  ("Tropical & Subtropical Dry Broadleaf Forests",   "热带亚热带干旱阔叶林"),
    3:  ("Tropical & Subtropical Coniferous Forests",       "热带亚热带针叶林"),
    4:  ("Temperate Broadleaf & Mixed Forests",             "温带阔叶混交林"),
    5:  ("Temperate Conifer Forests",                       "温带针叶林"),
    6:  ("Boreal Forests/Taiga",                            "北方针叶林/泰加林"),
    7:  ("Tropical & Subtropical Grasslands & Savannas",    "热带亚热带草原稀树灌丛"),
    8:  ("Temperate Grasslands & Savannas",                 "温带草原稀树灌丛"),
    9:  ("Flooded Grasslands & Savannas",                   "洪泛草原稀树草原"),
    10: ("Montane Grasslands & Shrublands",                 "山地草原灌丛"),
    11: ("Tundra",                                          "冻原"),
    12: ("Mediterranean Forests & Woodlands",               "地中海森林疏林灌丛"),
    13: ("Deserts & Xeric Shrublands",                      "荒漠与旱生灌丛"),
    14: ("Mangroves",                                       "红树林"),
    98: ("Rock and Ice",                                    "岩石与冰川"),
    99: ("Water",                                           "水体"),
}
