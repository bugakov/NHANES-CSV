# Начнем создание структуры приложения
# Создадим схему для организации данных NHANES

# Структура данных NHANES - основные категории и циклы
nhanes_structure = {
    "cycles": {
        "continuous": {
            "2021-2023": "NHANES 08/2021-08/2023",
            "2017-2020": "NHANES 2017-March 2020", 
            "2017-2018": "NHANES 2017-2018",
            "2015-2016": "NHANES 2015-2016",
            "2013-2014": "NHANES 2013-2014", 
            "2011-2012": "NHANES 2011-2012",
            "2009-2010": "NHANES 2009-2010",
            "2007-2008": "NHANES 2007-2008",
            "2005-2006": "NHANES 2005-2006",
            "2003-2004": "NHANES 2003-2004",
            "2001-2002": "NHANES 2001-2002", 
            "1999-2000": "NHANES 1999-2000"
        },
        "historical": {
            "NHANES III": "NHANES III (1988-1994)",
            "NHANES II": "NHANES II (1976-1980)",
            "NHANES I": "NHANES I (1971-1975)",
            "Hispanic HANES": "Hispanic HANES (1982-1984)",
            "NHES III": "NHES III",
            "NHES II": "NHES II", 
            "NHES I": "NHES I"
        }
    },
    "categories": {
        "DEMO": {
            "name": "Demographics",
            "description": "Демографические данные: возраст, пол, раса/этничность, доходы",
            "color": "#1f77b4"
        },
        "DIET": {
            "name": "Dietary",
            "description": "Данные о питании: потребление пищи, нутриенты, пищевые добавки",
            "color": "#ff7f0e"
        },
        "EXAM": {
            "name": "Examination",
            "description": "Физические обследования: антропометрия, артериальное давление, тесты",
            "color": "#2ca02c"
        },
        "LAB": {
            "name": "Laboratory",
            "description": "Лабораторные анализы: биохимия крови, токсиканты, биомаркеры",
            "color": "#d62728"
        },
        "Q": {
            "name": "Questionnaire", 
            "description": "Опросники: здоровье, медицинская история, образ жизни",
            "color": "#9467bd"
        }
    }
}

print("Структура данных NHANES создана:")
print(f"Циклы непрерывных обследований: {len(nhanes_structure['cycles']['continuous'])}")
print(f"Исторические циклы: {len(nhanes_structure['cycles']['historical'])}")
print(f"Основные категории данных: {len(nhanes_structure['categories'])}")

# Выведем основные категории
for cat_code, cat_info in nhanes_structure['categories'].items():
    print(f"{cat_code}: {cat_info['name']} - {cat_info['description']}")