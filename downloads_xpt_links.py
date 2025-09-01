import json
import requests
import os
from pathlib import Path
from urllib.parse import urlparse
import time

# Настройки
JSON_FILE = 'nhanes_xpt_links.json'
DOWNLOAD_DIR = 'downloads/xpt_files'
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

def create_download_dir():
    """Создает папку для загрузок если ее нет"""
    Path(DOWNLOAD_DIR).mkdir(parents=True, exist_ok=True)

def load_links_from_json():
    """Загружает ссылки из JSON файла"""
    try:
        with open(JSON_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data['links']
    except FileNotFoundError:
        print(f"Файл {JSON_FILE} не найден!")
        return []
    except json.JSONDecodeError:
        print(f"Ошибка чтения JSON файла {JSON_FILE}")
        return []

def file_exists(filename):
    """Проверяет существует ли файл"""
    filepath = os.path.join(DOWNLOAD_DIR, filename)
    return os.path.exists(filepath) and os.path.getsize(filepath) > 0

def download_file(url, filename):
    """Скачивает файл по URL"""
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()

        filepath = os.path.join(DOWNLOAD_DIR, filename)
        with open(filepath, 'wb') as f:
            f.write(response.content)

        return True, f"Файл {filename} успешно загружен"
    except requests.exceptions.RequestException as e:
        return False, f"Ошибка загрузки {filename}: {str(e)}"
    except Exception as e:
        return False, f"Неизвестная ошибка для {filename}: {str(e)}"

def get_filename_from_url(url):
    """Извлекает имя файла из URL"""
    parsed = urlparse(url)
    return os.path.basename(parsed.path)

def main():
    print("=== Загрузчик XPT файлов NHANES ===\n")

    # Создаем папку для загрузок
    create_download_dir()
    print(f"Папка для загрузок: {DOWNLOAD_DIR}")

    # Загружаем ссылки из JSON
    links = load_links_from_json()
    if not links:
        print("Нет ссылок для загрузки")
        return

    total_links = len(links)
    print(f"Найдено {total_links} файлов для загрузки")

    # Проверяем существующие файлы
    existing_files = 0
    for url in links:
        filename = get_filename_from_url(url)
        if file_exists(filename):
            existing_files += 1

    if existing_files > 0:
        print(f"Уже загружено файлов: {existing_files}")

    # Спрашиваем сколько файлов загрузить
    while True:
        try:
            choice = input(f"\nСколько файлов загрузить? (1-{total_links}, или 'all' для всех): ").strip().lower()
            if choice == 'all':
                download_count = total_links
                break
            else:
                download_count = int(choice)
                if 1 <= download_count <= total_links:
                    break
                else:
                    print(f"Введите число от 1 до {total_links}")
        except ValueError:
            print("Введите число или 'all'")

    # Спрашиваем о режиме загрузки
    skip_existing = False
    if existing_files > 0:
        while True:
            choice = input(f"\nПропустить уже загруженные файлы? (y/n): ").strip().lower()
            if choice in ['y', 'yes', 'да']:
                skip_existing = True
                break
            elif choice in ['n', 'no', 'нет']:
                skip_existing = False
                break
            else:
                print("Введите y/n или да/нет")

    # Загружаем файлы
    print(f"\nНачинаем загрузку {download_count} файлов...\n")

    successful = 0
    failed = 0
    skipped = 0

    for i, url in enumerate(links[:download_count], 1):
        filename = get_filename_from_url(url)

        # Проверяем существует ли файл
        if skip_existing and file_exists(filename):
            print(f"[{i}/{download_count}] Пропускаем (уже существует): {filename}")
            skipped += 1
            continue

        print(f"[{i}/{download_count}] Загрузка: {filename}")

        success, message = download_file(url, filename)

        if success:
            successful += 1
            print(f"✓ {message}")
        else:
            failed += 1
            print(f"✗ {message}")

        # Небольшая пауза между загрузками
        if i < download_count:
            time.sleep(0.5)

    print("=== Загрузка завершена ===")
    print(f"Успешно загружено: {successful}")
    print(f"Пропущено (уже существуют): {skipped}")
    print(f"Ошибок: {failed}")
    print(f"Файлы сохранены в: {DOWNLOAD_DIR}")

if __name__ == "__main__":
    main()