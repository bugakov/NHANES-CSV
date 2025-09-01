import requests
from bs4 import BeautifulSoup
import json

# URL страницы NHANES с файлами XPT
url = "https://wwwn.cdc.gov/nchs/nhanes/search/datapage.aspx?utm_source=chatgpt.com"

# Заголовки для имитации real browser
headers = {
    "User-Agent": "Mozilla/5.0"
}

# Получаем страницу
response = requests.get(url, headers=headers)
response.raise_for_status()

# Парсим HTML
soup = BeautifulSoup(response.text, "html.parser")

# Ищем все ссылки на XPT файлы
xpt_links = []
for link in soup.find_all('a', href=True):
    href = link['href']
    if href.lower().endswith('.xpt'):
        # Преобразуем относительный путь к абсолютному
        if href.startswith('/'):
            full_url = "https://wwwn.cdc.gov" + href
        else:
            full_url = href
        xpt_links.append(full_url)

# Сохраняем в JSON файл
data = {
    "total_links": len(xpt_links),
    "links": xpt_links
}

with open('nhanes_xpt_links.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"Найдено {len(xpt_links)} ссылок. Данные сохранены в nhanes_xpt_links.json")