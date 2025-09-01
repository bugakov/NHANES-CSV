import os
import glob

def replace_xpt_to_csv_in_txt_files():
    """
    Заменяет 'XPT' на 'CSV' и '.xpt' на '.csv' во всех .txt файлах в папке txt
    """
    txt_folder = 'txt'

    if not os.path.exists(txt_folder):
        print(f"Папка {txt_folder} не существует!")
        return

    # Получаем все .txt файлы в папке
    txt_files = glob.glob(os.path.join(txt_folder, '*.txt'))

    if not txt_files:
        print(f"В папке {txt_folder} не найдено .txt файлов!")
        return

    print(f"Найдено {len(txt_files)} .txt файлов для обработки")

    processed_count = 0

    for txt_file_path in txt_files:
        try:
            # Читаем содержимое файла
            with open(txt_file_path, 'r', encoding='utf-8') as file:
                content = file.read()

            # Заменяем 'XPT' на 'CSV' в описании
            content = content.replace('XPT File Description', 'CSV File Description')

            # Заменяем '.xpt' на '.csv' в названии файла
            content = content.replace('.xpt', '.csv')

            # Записываем измененное содержимое обратно в файл
            with open(txt_file_path, 'w', encoding='utf-8') as file:
                file.write(content)

            processed_count += 1

        except Exception as e:
            print(f"Ошибка при обработке файла {txt_file_path}: {e}")

    print(f"Обработка завершена! Обработано {processed_count} файлов из {len(txt_files)}")

if __name__ == "__main__":
    replace_xpt_to_csv_in_txt_files()
