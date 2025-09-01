import os
import json
from pathlib import Path

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("BeautifulSoup не установлен. Установите его командой:")
    print("pip install beautifulsoup4")
    exit(1)

# Настройки
HTM_DIR = 'downloads/htm_files'
OUTPUT_JSON = 'htm_info.json'

def extract_h3_from_file(filepath):
    """Извлекает текст из h3 элемента внутри div с id='PageHeader'"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        soup = BeautifulSoup(content, 'html.parser')

        # Находим div с id="PageHeader"
        page_header = soup.find('div', id='PageHeader')

        if page_header:
            # Находим h3 внутри этого div
            h3_element = page_header.find('h3')

            if h3_element:
                # Извлекаем текст и очищаем от лишних пробелов
                h3_text = h3_element.get_text(strip=True)
                return h3_text
            else:
                return "H3 элемент не найден"
        else:
            return "PageHeader не найден"

    except Exception as e:
        return f"Ошибка обработки файла: {str(e)}"

def main():
    print("=== Извлечение заголовков H3 из HTM файлов ===\n")

    # Проверяем существует ли папка с файлами
    if not os.path.exists(HTM_DIR):
        print(f"Папка {HTM_DIR} не найдена!")
        return

    # Получаем список всех .htm файлов
    htm_files = [f for f in os.listdir(HTM_DIR) if f.endswith('.htm')]

    if not htm_files:
        print(f"В папке {HTM_DIR} не найдено .htm файлов!")
        return

    print(f"Найдено {len(htm_files)} HTM файлов")

    # Обрабатываем каждый файл
    results = {}
    processed = 0
    errors = 0

    for filename in htm_files:
        filepath = os.path.join(HTM_DIR, filename)

        print(f"Обработка: {filename}")

        h3_text = extract_h3_from_file(filepath)

        if h3_text.startswith("Ошибка") or h3_text == "H3 элемент не найден" or h3_text == "PageHeader не найден":
            print(f"  ✗ {h3_text}")
            errors += 1
        else:
            print(f"  ✓ Заголовок: {h3_text}")

        results[filename] = h3_text
        processed += 1

    # Сохраняем результаты в JSON
    try:
        with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        print("=== Обработка завершена ===")
        print(f"Обработано файлов: {processed}")
        print(f"Ошибок: {errors}")
        print(f"Результаты сохранены в: {OUTPUT_JSON}")

        # Показываем пример результатов
        print("Примеры результатов:")
        count = 0
        for filename, title in results.items():
            if not title.startswith("Ошибка") and title not in ["H3 элемент не найден", "PageHeader не найден"]:
                print(f"  {filename}: {title}")
                count += 1
                if count >= 5:  # Показываем только первые 5 примеров
                    break

    except Exception as e:
        print(f"Ошибка сохранения JSON файла: {str(e)}")

if __name__ == "__main__":
    main()
