import json
import re
from collections import defaultdict

with open('htm_info.json', encoding='utf-8') as f:
    data = json.load(f)

# Карта для циклов
cycle_suffix = {
    'B': '2001-2002', 'C': '2003-2004', 'D': '2005-2006', 'E': '2007-2008',
    'F': '2009-2010', 'G': '2011-2012', 'H': '2013-2014', 'I': '2015-2016',
    'J': '2017-2018', 'P': '2017-2020', 'L': '2021-2023'
}
# Категорийные маски
category_map = {
    'DEMO': 'Demographics',
    'BMX': 'Examination', 'BPX': 'Examination', 'EXAM': 'Examination',
    'LAB': 'Laboratory', 'CBC': 'Laboratory', 'ALB': 'Laboratory', 'HDL': 'Laboratory', 'TCHOL': 'Laboratory',
    'DR1': 'Dietary', 'DR2': 'Dietary', 'DBQ': 'Dietary', 'DIET': 'Dietary',
    'Q': 'Questionnaire', 'HSQ': 'Questionnaire', 'SMQ': 'Questionnaire', 'ALQ': 'Questionnaire', 'CDQ': 'Questionnaire',
    'DQ': 'Questionnaire'
    # можно дополнить/уточнить!
}

grouped = defaultdict(lambda: defaultdict(list))

for code, desc in data.items():
    # Определить цикл (год/период)
    match = re.search(r'_([A-Z])$', code)
    cycle = cycle_suffix.get(match.group(1), "Unknown") if match else "Unknown"

    # Определить категорию
    cat = 'Other'
    for prefix, cat_name in category_map.items():
        if code.startswith(prefix):
            cat = cat_name
            break

    grouped[cycle][cat].append({'code': code, 'desc': desc})

# Сортированный вывод для примера
for cycle in sorted(grouped.keys()):
    print(f"{cycle}:")
    for cat in grouped[cycle]:
        print(f"  {cat} ({len(grouped[cycle][cat])})")

# Можно сохранить в файл:
import json
with open('nhanes_grouped.json', 'w', encoding='utf-8') as f:
    json.dump(grouped, f, ensure_ascii=False, indent=2)
