import json
import os

from .constants import DATA_DIR, DATATYPE_DICT


def validate_table_name(table_name: str) -> None:
    """Проверка, что имя таблицы это не путь

    Args:
        table_name (str): потенциальное имя таблицы
    """
    if not table_name.isidentifier():
        raise ValueError(f'Недопустимое имя таблицы: "{table_name}"')


def _table_data_path(table_name: str) -> str:
    """Создание пути с валидацией

    Args:
        table_name (str): имя таблицы

    Returns:
        str: путь к таблице
    """
    validate_table_name(table_name)
    return os.path.join(DATA_DIR, f'{table_name}.json')


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
    """Сохранение метаданных в JSON-файл

    Args:
        filepath (str): путь к файлу
        data (dict): метаданные таблиц
    """
    with open(filepath, 'w') as f:
        json.dump(data, f)


def delete_table_data(table_name: str) -> None:
    """Удаление таблицы по названию

    Args:
        table_name (str): название таблицы
    """
    filepath = _table_data_path(table_name)
    try:
        os.remove(filepath)
    except FileNotFoundError:
        pass


def load_table_data(table_name: str) -> list[dict]:
    """Загрузка данных таблицы из файла

    Args:
        table_name (str): название таблицы

    Returns:
        list[dict]: список записей таблицы
    """
    filepath = _table_data_path(table_name)
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
    filepath = _table_data_path(table_name)
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(filepath, 'w') as f:
        json.dump(data, f)


def validate_column_values(
        table_columns: dict[str, str],
        column_values: dict[str, str | int | bool],
    ) -> None:
    """Проверка названий столбцов и типов значений

    Args:
        table_columns (dict[str, str]): схема таблицы
        column_values (dict[str, str | int | bool]): столбцы и значения из команды
    """
    for col_name, value in column_values.items():
        if col_name not in table_columns:
            raise ValueError(f'Столбец "{col_name}" не существует')
        dtype = table_columns[col_name]
        if type(value) is not DATATYPE_DICT.get(dtype):
            raise ValueError(f'Столбец "{col_name}" должен иметь тип {dtype}')
