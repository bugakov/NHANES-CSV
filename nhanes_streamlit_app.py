# NHANES Data Manager - Streamlit Application
# Приложение для управления наборами данных NHANES

import streamlit as st
import pandas as pd
import requests
import io
import os
from datetime import datetime
import zipfile
from pathlib import Path
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Конфигурация приложения
st.set_page_config(
    page_title="NHANES Data Manager",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

class NHANESDataManager:
    """Класс для управления данными NHANES"""

    def __init__(self):
        self.base_url = "https://ftp.cdc.gov/pub/health_statistics/nchs/nhanes/continuousnhanes"
        self.data_dir = Path("nhanes_data")
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Структура данных NHANES
        self.cycles = {
            "continuous": {
                "2021-2023": {"name": "NHANES 08/2021-08/2023", "suffix": "L"},
                "2017-2020": {"name": "NHANES 2017-March 2020", "suffix": "P"},
                "2017-2018": {"name": "NHANES 2017-2018", "suffix": "J"},
                "2015-2016": {"name": "NHANES 2015-2016", "suffix": "I"},
                "2013-2014": {"name": "NHANES 2013-2014", "suffix": "H"},
                "2011-2012": {"name": "NHANES 2011-2012", "suffix": "G"},
                "2009-2010": {"name": "NHANES 2009-2010", "suffix": "F"},
                "2007-2008": {"name": "NHANES 2007-2008", "suffix": "E"},
                "2005-2006": {"name": "NHANES 2005-2006", "suffix": "D"},
                "2003-2004": {"name": "NHANES 2003-2004", "suffix": "C"},
                "2001-2002": {"name": "NHANES 2001-2002", "suffix": "B"},
                "1999-2000": {"name": "NHANES 1999-2000", "suffix": ""}
            },
            "historical": {
                "NHANES III": "NHANES III (1988-1994)",
                "NHANES II": "NHANES II (1976-1980)",
                "NHANES I": "NHANES I (1971-1975)",
                "Hispanic HANES": "Hispanic HANES (1982-1984)"
            }
        }

        self.categories = {
            "DEMO": {
                "name": "Demographics",
                "description": "Демографические данные: возраст, пол, раса/этничность, доходы",
                "color": "#1f77b4",
                "files": ["DEMO"]
            },
            "DIET": {
                "name": "Dietary",
                "description": "Данные о питании: потребление пищи, нутриенты, пищевые добавки",
                "color": "#ff7f0e",
                "files": ["DR1TOT", "DR2TOT", "DR1IFF", "DR2IFF", "DRXFCD", "DBQ"]
            },
            "EXAM": {
                "name": "Examination",
                "description": "Физические обследования: антропометрия, артериальное давление, тесты",
                "color": "#2ca02c",
                "files": ["BMX", "BPX", "BPQ", "AUQ", "AUX", "CVX"]
            },
            "LAB": {
                "name": "Laboratory",
                "description": "Лабораторные анализы: биохимия крови, токсиканты, биомаркеры",
                "color": "#d62728",
                "files": ["CBC", "HDL", "TRIGLY", "TCHOL", "ALB_CR", "CRP"]
            },
            "Q": {
                "name": "Questionnaire",
                "description": "Опросники: здоровье, медицинская история, образ жизни",
                "color": "#9467bd",
                "files": ["HSQ", "DIQ", "ALQ", "SMQ", "ACQ", "CDQ"]
            }
        }

    def get_xpt_url(self, cycle, file_prefix):
        """Получить URL для XPT файла"""
        if cycle == "1999-2000":
            suffix = ""
        else:
            suffix = "_" + self.cycles["continuous"][cycle]["suffix"]

        file_name = f"{file_prefix}{suffix}.XPT"
        year_path = cycle.replace("-", "-")
        return f"{self.base_url}/{year_path}/{file_name}"

    def download_xpt_file(self, url, local_path):
        """Скачать XPT файл"""
        try:
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()

            # Check if the response is HTML (error page)
            content_type = response.headers.get('content-type', '').lower()
            if 'text/html' in content_type:
                logger.error(f"URL {url} returned HTML instead of XPT file")
                return False

            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            # Validate that the downloaded file is actually an XPT file
            if not self._is_valid_xpt_file(local_path):
                logger.error(f"Downloaded file {local_path} is not a valid XPT file")
                # Remove the invalid file
                if local_path.exists():
                    local_path.unlink()
                return False

            return True
        except Exception as e:
            logger.error(f"Ошибка скачивания {url}: {e}")
            return False

    def _is_valid_xpt_file(self, file_path):
        """Проверить, является ли файл валидным XPT файлом"""
        try:
            with open(file_path, 'rb') as f:
                # Read first few bytes to check XPT header
                header = f.read(80)
                # XPT files start with specific header bytes
                # Check for SAS XPORT format signature
                if len(header) < 80:
                    return False
                # XPT files have "SAS" in the header
                return b'SAS' in header[:10] or b'XPORT' in header[:10]
        except Exception:
            return False

    def xpt_to_dataframe(self, xpt_path):
        """Преобразовать XPT файл в DataFrame"""
        try:
            # Try pandas read_sas first
            df = pd.read_sas(xpt_path, format='xport')
            return df
        except Exception as e1:
            logger.warning(f"Pandas read_sas failed for {xpt_path}: {e1}")
            try:
                # Try alternative: pyreadstat
                import pyreadstat
                df, meta = pyreadstat.read_xport(str(xpt_path))
                logger.info(f"Successfully read {xpt_path} with pyreadstat")
                return df
            except Exception as e2:
                logger.warning(f"Pyreadstat failed for {xpt_path}: {e2}")
                try:
                    # Try alternative: sas7bdat
                    from sas7bdat import SAS7BDAT
                    with SAS7BDAT(str(xpt_path)) as f:
                        df = f.to_data_frame()
                    logger.info(f"Successfully read {xpt_path} with sas7bdat")
                    return df
                except Exception as e3:
                    logger.error(f"All methods failed for {xpt_path}: pandas({e1}), pyreadstat({e2}), sas7bdat({e3})")
                    return None

    def download_all_data(self, progress_callback=None):
        """Скачать все данные NHANES"""
        total_files = 0
        downloaded_files = 0

        # Подсчитаем общее количество файлов
        for cycle in self.cycles["continuous"]:
            for category, cat_info in self.categories.items():
                total_files += len(cat_info["files"])

        for cycle_key, cycle_info in self.cycles["continuous"].items():
            cycle_dir = self.data_dir / cycle_key
            cycle_dir.mkdir(parents=True, exist_ok=True)

            for category, cat_info in self.categories.items():
                category_dir = cycle_dir / category.lower()
                category_dir.mkdir(parents=True, exist_ok=True)

                for file_prefix in cat_info["files"]:
                    url = self.get_xpt_url(cycle_key, file_prefix)
                    local_path = category_dir / f"{file_prefix}_{cycle_key.replace('-', '_')}.xpt"

                    if not local_path.exists():
                        success = self.download_xpt_file(url, local_path)
                        if success:
                            downloaded_files += 1
                        else:
                            logger.warning(f"Failed to download {file_prefix} from {url}")

                        if progress_callback:
                            status_msg = f"Скачивание: {file_prefix} ({cycle_key})"
                            if not success:
                                status_msg += " - ОШИБКА"
                            progress = downloaded_files / total_files
                            progress_callback(progress, status_msg)

        return downloaded_files, total_files

    def get_available_datasets(self):
        """Получить список доступных наборов данных"""
        datasets = []

        for cycle_key in self.cycles["continuous"]:
            cycle_dir = self.data_dir / cycle_key
            if cycle_dir.exists():
                for category in self.categories:
                    category_dir = cycle_dir / category.lower()
                    if category_dir.exists():
                        for xpt_file in category_dir.glob("*.xpt"):
                            datasets.append({
                                "cycle": cycle_key,
                                "category": category,
                                "file": xpt_file.name,
                                "path": xpt_file,
                                "size": xpt_file.stat().st_size
                            })

        return datasets

    def load_dataset_as_csv(self, dataset_path):
        """Загрузить набор данных как CSV"""
        try:
            df = self.xpt_to_dataframe(dataset_path)
            if df is not None:
                csv_buffer = io.StringIO()
                df.to_csv(csv_buffer, index=False, encoding='utf-8')
                return csv_buffer.getvalue()
            return None
        except Exception as e:
            logger.error(f"Ошибка конвертации в CSV: {e}")
            return None

@st.cache_data
def load_nhanes_manager():
    """Загрузить менеджер данных NHANES"""
    return NHANESDataManager()

def main():
    """Главная функция приложения"""
    st.title("📊 NHANES Data Manager")
    st.markdown("**Управление и скачивание наборов данных National Health and Nutrition Examination Survey**")

    # Инициализация менеджера данных
    manager = load_nhanes_manager()

    # Боковая панель
    st.sidebar.title("Навигация")
    page = st.sidebar.selectbox(
        "Выберите страницу",
        ["Обзор данных", "Скачивание данных", "Экспорт в CSV", "Статистика"]
    )

    if page == "Обзор данных":
        show_data_overview(manager)
    elif page == "Скачивание данных":
        show_download_page(manager)
    elif page == "Экспорт в CSV":
        show_export_page(manager)
    elif page == "Статистика":
        show_statistics_page(manager)

def show_data_overview(manager):
    """Показать обзор данных NHANES"""
    st.header("📋 Обзор данных NHANES")

    st.markdown("""
    **NHANES (National Health and Nutrition Examination Survey)** — это программа исследований,
    проводимых для оценки состояния здоровья и питания взрослых и детей в Соединенных Штатах.
    """)

    # Циклы обследований
    st.subheader("🗓️ Циклы обследований")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Непрерывные обследования (1999-2023)**")
        for cycle, info in manager.cycles["continuous"].items():
            st.markdown(f"• **{cycle}**: {info['name']}")

    with col2:
        st.markdown("**Исторические обследования**")
        for cycle, name in manager.cycles["historical"].items():
            st.markdown(f"• **{cycle}**: {name}")

    # Категории данных
    st.subheader("📊 Категории данных")

    for category, info in manager.categories.items():
        with st.container():
            col1, col2 = st.columns([1, 4])
            with col1:
                st.markdown(f"**{category}**", unsafe_allow_html=True)
            with col2:
                st.markdown(f"**{info['name']}** - {info['description']}")
                st.markdown(f"*Основные файлы: {', '.join(info['files'])[:50]}...*")
            st.markdown("---")

def show_download_page(manager):
    """Страница скачивания данных"""
    st.header("⬇️ Скачивание данных NHANES")

    st.markdown("""
    Нажмите кнопку ниже, чтобы начать скачивание всех доступных наборов данных NHANES.
    Данные будут сохранены локально и организованы по циклам и категориям.
    """)

    st.warning("⚠️ **Важное уведомление:** Прямые ссылки на XPT файлы NHANES больше не работают. Данные перемещены на другие платформы.")

    # Проверим, есть ли уже скаченные данные
    datasets = manager.get_available_datasets()

    if datasets:
        st.success(f"✅ Найдено {len(datasets)} скачанных наборов данных")

        if st.button("🔄 Обновить данные"):
            with st.spinner("Скачивание данных..."):
                progress_bar = st.progress(0)
                status_text = st.empty()

                def update_progress(progress, message):
                    progress_bar.progress(progress)
                    status_text.text(message)

                downloaded, total = manager.download_all_data(update_progress)

                if downloaded > 0:
                    st.success(f"✅ Скачано {downloaded} из {total} файлов")
                else:
                    st.error("❌ Не удалось скачать ни одного файла. Проверьте подключение к интернету и доступность серверов NHANES.")
                    st.info("💡 **Альтернатива:** Данные NHANES также доступны через IPUMS NHANES: https://nhanes.ipums.org/")
    else:
        st.warning("⚠️ Данные не найдены. Начните скачивание.")

        if st.button("📥 Начать скачивание всех данных"):
            with st.spinner("Скачивание данных NHANES..."):
                progress_bar = st.progress(0)
                status_text = st.empty()

                def update_progress(progress, message):
                    progress_bar.progress(progress)
                    status_text.text(message)

                downloaded, total = manager.download_all_data(update_progress)

                if downloaded > 0:
                    st.success(f"✅ Успешно скачано {downloaded} из {total} файлов")
                    st.rerun()
                else:
                    st.error("❌ Ошибка при скачивании данных. Прямые ссылки на XPT файлы больше не доступны.")
                    st.info("💡 **NHANES данные теперь доступны через следующие источники:**")
                    st.markdown("**Рекомендуемые источники данных NHANES:**")
                    st.markdown("- [IPUMS NHANES](https://nhanes.ipums.org/) - гармонизированные данные в CSV формате")
                    st.markdown("- [CDC Data Portal](https://data.cdc.gov/) - поиск по 'NHANES'")
                    st.markdown("- [NHANES Website](https://www.cdc.gov/nchs/nhanes/) - официальный сайт с данными")
                    st.markdown("- [CDC FTP](https://ftp.cdc.gov/pub/health_statistics/nchs/nhanes/) - FTP сервер (может требовать проверки)")

def show_export_page(manager):
    """Страница экспорта в CSV"""
    st.header("📁 Экспорт данных в CSV")

    datasets = manager.get_available_datasets()

    if not datasets:
        st.warning("⚠️ Сначала скачайте данные на странице 'Скачивание данных'")
        return

    # Фильтры
    st.subheader("🔍 Фильтры")

    col1, col2 = st.columns(2)

    with col1:
        cycles = sorted(list(set([d["cycle"] for d in datasets])))
        selected_cycles = st.multiselect("Выберите циклы", cycles, default=cycles[:3])

    with col2:
        categories = sorted(list(set([d["category"] for d in datasets])))
        selected_categories = st.multiselect("Выберите категории", categories, default=categories)

    # Фильтрация данных
    filtered_datasets = [
        d for d in datasets
        if d["cycle"] in selected_cycles and d["category"] in selected_categories
    ]

    if not filtered_datasets:
        st.warning("⚠️ Нет данных для выбранных фильтров")
        return

    # Отображение таблицы наборов данных
    st.subheader(f"📊 Доступные наборы данных ({len(filtered_datasets)})")

    df_info = pd.DataFrame([
        {
            "Цикл": d["cycle"],
            "Категория": d["category"],
            "Файл": d["file"],
            "Размер (MB)": round(d["size"] / 1024 / 1024, 2)
        } for d in filtered_datasets
    ])

    st.dataframe(df_info, use_container_width=True)

    # Кнопки экспорта
    st.subheader("💾 Экспорт данных")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📁 Экспорт выбранных данных (ZIP)"):
            with st.spinner("Создание ZIP архива..."):
                zip_buffer = create_zip_export(manager, filtered_datasets)
                if zip_buffer:
                    st.download_button(
                        label="⬇️ Скачать ZIP архив",
                        data=zip_buffer.getvalue(),
                        file_name=f"nhanes_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                        mime="application/zip"
                    )

    with col2:
        if st.button("📋 Экспорт сводной таблицы"):
            csv_summary = df_info.to_csv(index=False, encoding='utf-8')
            st.download_button(
                label="⬇️ Скачать CSV сводку",
                data=csv_summary,
                file_name=f"nhanes_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

    # Индивидуальный экспорт файлов
    if st.expander("🔧 Индивидуальный экспорт файлов"):
        selected_dataset = st.selectbox(
            "Выберите набор данных для экспорта",
            filtered_datasets,
            format_func=lambda x: f"{x['cycle']} - {x['category']} - {x['file']}"
        )

        if st.button("📤 Экспорт выбранного файла"):
            with st.spinner(f"Конвертация {selected_dataset['file']} в CSV..."):
                csv_data = manager.load_dataset_as_csv(selected_dataset["path"])
                if csv_data:
                    st.download_button(
                        label="⬇️ Скачать CSV файл",
                        data=csv_data,
                        file_name=f"{selected_dataset['file'].replace('.xpt', '')}.csv",
                        mime="text/csv"
                    )
                else:
                    st.error("❌ Ошибка конвертации файла")

def create_zip_export(manager, datasets):
    """Создать ZIP архив с данными CSV"""
    try:
        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for dataset in datasets:
                csv_data = manager.load_dataset_as_csv(dataset["path"])
                if csv_data:
                    csv_filename = f"{dataset['cycle']}/{dataset['category']}/{dataset['file'].replace('.xpt', '.csv')}"
                    zip_file.writestr(csv_filename, csv_data)

        zip_buffer.seek(0)
        return zip_buffer

    except Exception as e:
        logger.error(f"Ошибка создания ZIP: {e}")
        return None

def show_statistics_page(manager):
    """Страница статистики"""
    st.header("📈 Статистика данных")

    datasets = manager.get_available_datasets()

    if not datasets:
        st.warning("⚠️ Сначала скачайте данные для просмотра статистики")
        return

    # Общая статистика
    st.subheader("📊 Общая информация")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Всего файлов", len(datasets))

    with col2:
        total_size = sum([d["size"] for d in datasets]) / 1024 / 1024 / 1024
        st.metric("Общий размер", f"{total_size:.2f} GB")

    with col3:
        unique_cycles = len(set([d["cycle"] for d in datasets]))
        st.metric("Циклов", unique_cycles)

    with col4:
        unique_categories = len(set([d["category"] for d in datasets]))
        st.metric("Категорий", unique_categories)

    # Распределение по циклам
    st.subheader("📅 Распределение по циклам")

    cycle_counts = pd.DataFrame(datasets).groupby("cycle").size().reset_index(name="count")
    st.bar_chart(cycle_counts.set_index("cycle"))

    # Распределение по категориям
    st.subheader("🗂️ Распределение по категориям")

    category_counts = pd.DataFrame(datasets).groupby("category").size().reset_index(name="count")
    st.bar_chart(category_counts.set_index("category"))

    # Детальная таблица
    st.subheader("📋 Детальная информация")

    df_stats = pd.DataFrame([
        {
            "Цикл": d["cycle"],
            "Категория": d["category"],
            "Файл": d["file"],
            "Размер (MB)": round(d["size"] / 1024 / 1024, 2)
        } for d in datasets
    ])

    st.dataframe(df_stats.sort_values(["Цикл", "Категория"]), use_container_width=True)

if __name__ == "__main__":
    main()
