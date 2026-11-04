import json
import os

from .constants import DATA_DIR


def load_metadata(filepath: str) -> dict:
    """Загрузка данных из файла

    Args:
        filepath (str): путь к файлу

    Returns:
        dict: database в формате dict
    """
    try:
        with open(filepath, 'r') as f:
            db_dict = json.load(f)
    except FileNotFoundError:
        db_dict = {}
    return db_dict


def save_metadata(filepath: str, data: dict) -> None:
    """Загрузка данных в файл

    Args:
        filepath (str): путь к файлу
        data (dict): database
    """
    with open(filepath, 'w') as f:
        json.dump(data, f)


def load_table_data(table_name: str) -> list[dict]:
    """Загрузка данных таблицы из файла

    Args:
        table_name (str): название таблицы

    Returns:
        list[dict]: список записей таблицы
    """
    filepath = os.path.join(DATA_DIR, f'{table_name}.json')
    try:
        with open(filepath, 'r') as f:
            table_data = json.load(f)
    except FileNotFoundError:
        table_data = []
    return table_data


def save_table_data(table_name: str, data: list[dict]) -> None:
    """Сохранение данных таблицы в файл

    Args:
        table_name (str): название таблицы
        data (list[dict]): список записей таблицы
    """
    os.makedirs(DATA_DIR, exist_ok=True)
    filepath = os.path.join(DATA_DIR, f'{table_name}.json')
    with open(filepath, 'w') as f:
        json.dump(data, f)
