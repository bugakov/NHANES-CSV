import streamlit as st
import pandas as pd
import json
from pathlib import Path
import base64

st.markdown("""
    <style>
    [data-testid="stToolbar"] {visibility: hidden !important;}
    #MainMenu {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    </style>
""", unsafe_allow_html=True)

# Настройка страницы
st.set_page_config(
    page_title="NHANES Data Explorer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Заголовок приложения
st.title(":material/bar_chart: NHANES Data Explorer")
st.markdown("**:material/map: Навигатор по базе данных National Health and Nutrition Examination Survey**")

# Пути к папкам с данными
DATA_DIRS = {
    'csv': Path('csv'),
    'txt': Path('txt'),
    'htm': Path('htm')
}

@st.cache_data
def load_nhanes_structure():
    """Загрузить структуру данных NHANES из JSON файла"""
    try:
        with open('nhanes_grouped_ru.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("Файл nhanes_grouped_ru.json не найден!")
        return {}
    except Exception as e:
        st.error(f"Ошибка загрузки структуры данных: {e}")
        return {}

def get_file_path(data_type, code):
    """Получить путь к файлу указанного типа"""
    if data_type not in DATA_DIRS:
        return None

    file_path = DATA_DIRS[data_type] / f"{code}.{data_type}"
    return file_path if file_path.exists() else None

def load_csv_file(code):
    """Загрузить CSV файл"""
    file_path = get_file_path('csv', code)
    if file_path:
        try:
            df = pd.read_csv(file_path)
            return df
        except Exception as e:
            st.error(f"Ошибка загрузки CSV файла: {e}")
            return None
    return None

def load_txt_file(code):
    """Загрузить TXT файл с метаданными"""
    file_path = get_file_path('txt', code)
    if file_path:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            st.error(f"Ошибка загрузки TXT файла: {e}")
            return None
    return None

def load_htm_file(code):
    """Загрузить HTM файл"""
    file_path = get_file_path('htm', code)
    if file_path:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            st.error(f"Ошибка загрузки HTM файла: {e}")
            return None
    return None

def create_download_link(df, filename):
    """Создать ссылку для скачивания DataFrame как CSV"""
    csv = df.to_csv(index=False, encoding='utf-8')
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}"><span class="material-icons" style="vertical-align:middle;">download</span> Скачать {filename}</a>'
    return href

def main():
    # Загрузить структуру данных
    nhanes_data = load_nhanes_structure()

    if not nhanes_data:
        st.stop()

    # Боковая панель для навигации
    st.sidebar.title(":material/explore: Навигация")

    # Выбор года
    years = list(nhanes_data.keys())
    selected_year = st.sidebar.selectbox(
        "Выберите год исследования:",
        years,
        help="Выберите период исследования NHANES"
    )

    if selected_year in nhanes_data:
        year_data = nhanes_data[selected_year]

        # Выбор категории
        categories = list(year_data.keys())
        selected_category = st.sidebar.selectbox(
            "Выберите категорию:",
            categories,
            help="Категория данных (лабораторные, опросники и т.д.)"
        )

        if selected_category in year_data:
            category_data = year_data[selected_category]

            # Выбор конкретного набора данных
            if category_data:
                # Создаем список для выбора
                options = []
                code_to_item = {}

                for item in category_data:
                    code = item['code']
                    desc_ru = item.get('ru', item.get('desc', code))
                    display_text = f"{code}: {desc_ru}"
                    options.append(display_text)
                    code_to_item[display_text] = item

                selected_option = st.sidebar.selectbox(
                    "Выберите набор данных:",
                    options,
                    help="Конкретный набор данных для анализа"
                )

                if selected_option:
                    selected_item = code_to_item[selected_option]
                    code = selected_item['code']

                    # Основная область
                    st.header(f":material/assignment: {selected_item.get('ru', selected_item.get('desc', code))}")

                    col1, col2 = st.columns([2, 1])

                    with col1:
                        st.subheader(":material/info: Описание")
                        st.write(f"**Код:** {code}")
                        st.write(f"**Описание (EN):** {selected_item.get('desc', 'N/A')}")
                        st.write(f"**Описание (RU):** {selected_item.get('ru', 'N/A')}")
                        st.write(f"**Год:** {selected_year}")
                        st.write(f"**Категория:** {selected_category}")

                    with col2:
                        st.subheader(":material/folder: Доступные файлы")

                        # Проверяем наличие файлов
                        csv_exists = get_file_path('csv', code) is not None
                        txt_exists = get_file_path('txt', code) is not None
                        htm_exists = get_file_path('htm', code) is not None

                        if csv_exists:
                            st.success(":material/check_circle: CSV данные")
                        else:
                            st.warning(":material/cancel: CSV данные недоступны")

                        if txt_exists:
                            st.success(":material/check_circle: Метаданные (TXT)")
                        else:
                            st.warning(":material/cancel: Метаданные недоступны")

                        if htm_exists:
                            st.success(":material/check_circle: Оригинальное подробное описание (HTM)")
                        else:
                            st.warning(":material/cancel: Оригинальное описание недоступно")

                    # Табы для разных типов контента
                    if csv_exists or txt_exists or htm_exists:
                        tab_names = []
                        if csv_exists:
                            tab_names.append(":material/table_chart: Данные (CSV)")
                        if txt_exists:
                            tab_names.append(":material/description: Метаданные (TXT)")
                        if htm_exists:
                            tab_names.append(":material/public: Подробное описание (HTM)")

                        if tab_names:
                            tabs = st.tabs(tab_names)
                            tab_index = 0

                            # Вкладка CSV данных
                            if csv_exists:
                                with tabs[tab_index]:
                                    st.subheader(":material/table_chart: Данные CSV")

                                    # Загружаем данные
                                    df = load_csv_file(code)

                                    if df is not None:
                                        # Информация о данных
                                        col1, col2, col3 = st.columns(3)
                                        with col1:
                                            st.metric("Строк", len(df))
                                        with col2:
                                            st.metric("Столбцов", len(df.columns))
                                        with col3:
                                            st.metric("Размер", f"{df.memory_usage(deep=True).sum() / 1024:.1f} KB")

                                        # Кнопка скачивания
                                        st.markdown(create_download_link(df, f"{code}.csv"), unsafe_allow_html=True)

                                        # Показать первые строки
                                        st.subheader(":material/search: Предварительный просмотр")
                                        st.dataframe(df.head(10), use_container_width=True)

                                        # Статистика по столбцам
                                        if st.checkbox("Показать статистику по столбцам"):
                                            st.subheader(":material/insights: Статистика по столбцам")
                                            numeric_cols = df.select_dtypes(include=['number']).columns
                                            if len(numeric_cols) > 0:
                                                st.dataframe(df[numeric_cols].describe(), use_container_width=True)
                                            else:
                                                st.info("Числовые столбцы не найдены")
                                    else:
                                        st.error("Не удалось загрузить CSV файл")

                                tab_index += 1

                            # Вкладка TXT метаданных
                            if txt_exists:
                                with tabs[tab_index]:
                                    st.subheader(":material/description: Метаданные")

                                    txt_content = load_txt_file(code)
                                    if txt_content:
                                        st.text_area("Метаданные:", txt_content, height=400, disabled=True)
                                    else:
                                        st.error("Не удалось загрузить метаданные")

                                tab_index += 1

                            # Вкладка HTM описания
                            if htm_exists:
                                with tabs[tab_index]:
                                    st.subheader(":material/public: Оригинальное описание")

                                    htm_content = load_htm_file(code)
                                    if htm_content:
                                        # Показываем HTML контент
                                        st.components.v1.html(htm_content, height=600, scrolling=True)
                                    else:
                                        st.error(":material/error: Не удалось загрузить HTML описание")
                    else:
                        st.warning(":material/block: Для выбранного набора данных файлы недоступны")
            else:
                st.info(":material/info: В выбранной категории нет наборов данных")
        else:
            st.error(":material/error: Выбранная категория не найдена")
    else:
        st.error(":material/error: Выбранный год не найден в данных")

    # Информационная панель
    st.sidebar.markdown("---")
    st.sidebar.subheader(":material/menu_book: О NHANES")
    st.sidebar.markdown("""
    **NHANES (National Health and Nutrition Examination Survey)** -
    национальное исследование здоровья и питания в США.

    Данные включают:
    - Физические осмотры
    - Лабораторные анализы
    - Опросы о здоровье и питании
    - Демографическую информацию
    """)

    st.sidebar.markdown("---")
    st.sidebar.subheader(":material/settings: Статистика")

    # Подсчитываем статистику
    total_years = len(nhanes_data)
    total_categories = sum(len(year_data) for year_data in nhanes_data.values())
    total_datasets = sum(
        len(category_data)
        for year_data in nhanes_data.values()
        for category_data in year_data.values()
    )

    st.sidebar.metric("Годы исследований", total_years)
    st.sidebar.metric("Категорий", total_categories)
    st.sidebar.metric("Наборов данных", total_datasets)

if __name__ == "__main__":
    main()
