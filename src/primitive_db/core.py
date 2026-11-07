from typing import Any, Callable

from .constants import DATATYPE_DICT
from .decorators import confirm_action, create_cacher, handle_db_errors, log_time
from .utils import load_table_data, validate_table_name

cache_select = create_cacher()


def set_select_cache(cache_result: Callable) -> None:
    """Обнуление кеша

    Args:
        cache_result (Callable): функция кеша
    """
    global cache_select
    cache_select = cache_result


@handle_db_errors
def create_table(
        metadata: dict[str, dict[str, str]], 
        table_name: str, 
        columns: dict[str, str]
    ) -> dict[str, dict[str, str]]:
    """Создание таблицы на основе названия и типов столбцов

    Args:
        metadata (dict[str, dict[str, str]]): метаданные таблиц
        table_name (str): название таблицы
        columns (dict[str, str]): названия колонок с типами

    Returns:
        dict[str, dict[str, str]]: обновленные метаданные
    """
    validate_table_name(table_name)
    if table_name in metadata:
        raise ValueError(f'Table with name: "{table_name}" already exists.')

    allowed_dtypes_check = all(
        (dtype in {'int', 'str', 'bool'}) 
        for dtype in columns.values()
    )

    if not allowed_dtypes_check:
        unsupported_dtypes = {
            dtype for dtype in columns.values() 
            if dtype not in {'int', 'str', 'bool'}
        }
        raise ValueError('Unsupported types:', *unsupported_dtypes)

    if 'ID' in columns and columns['ID'] != 'int':
        raise ValueError('ID must have type int')
    
    table_columns = {"ID": "int"}
    table_columns.update(columns)

    metadata[table_name] = table_columns

    return metadata


@handle_db_errors
@confirm_action('удаление таблицы')
def drop_table(
        metadata: dict[str, dict[str, str]], 
        table_name: str
    ) -> dict[str, dict[str, str]]:
    """Удаление таблицы по ее имени

    Args:
        metadata (dict[str, dict[str, str]]): метаданные таблицы
        table_name (str): название таблицы

    Returns:
        dict[str, dict[str, str]]: обновленные метаданные
    """
    if table_name not in metadata:
        raise ValueError(f'No table with name: {table_name}')

    del metadata[table_name]
    return metadata


@handle_db_errors
@log_time
def select(
        table_data: list[dict[str, Any]],
        where_clause: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
    """Выбор записей по возможному условию

    Args:
        table_data (list[dict[str, Any]]): записи таблицы
        where_clause (dict[str, Any] | None, optional): условие. 
            Defaults to None.

    Returns:
        list[dict[str, Any]]: выбранные записи
    """
    if where_clause is None:
        row_count = len(table_data)

        def find_all_indices():
            return range(row_count)

        matching_indices = cache_select((None, row_count), find_all_indices)
        return [table_data[index] for index in matching_indices]

    clause_col_name, clause_val = next(iter(where_clause.items()))
    column_values = tuple(row[clause_col_name] for row in table_data)
    cache_key = (clause_col_name, clause_val, column_values)

    def find_matching_indices():
        return tuple(
            index for index, value in enumerate(column_values) if value == clause_val
        )

    matching_indices = cache_select(cache_key, find_matching_indices)
    return [table_data[index] for index in matching_indices]


@handle_db_errors
@confirm_action('удаление записей')
def delete(
        table_data: list[dict[str, Any]],
        where_clause: dict[str, Any]
    ) -> list[dict[str, Any]]:
    """Удаление записей по условию

    Args:
        table_data (list[dict[str, Any]]): записи таблицы
        where_clause (dict[str, Any]): название столбца и его значение

    Returns:
        list[dict[str, Any]]: записи, которые остались в таблице
    """
    if len(where_clause) != 1:
        raise ValueError('Укажите одно условие для удаления')

    clause_col_name = list(where_clause.keys())[0]
    clause_val = list(where_clause.values())[0]
    return [
        row for row in table_data if row[clause_col_name] != clause_val
    ]


@handle_db_errors
@log_time
def insert(
        metadata: dict[str, dict[str, str]],
        table_name: str,
        values: list[Any]
    ) -> list[dict[str, Any]]:
    """Добавление записи в данные таблицы

    Args:
        metadata (dict[str, dict[str, str]]): метаданные таблиц
        table_name (str): название таблицы
        values (list[Any]): значения столбцов в порядке схемы без ID

    Returns:
        list[dict[str, Any]]: обновленные данные таблицы
    """
    if table_name not in metadata:
        raise ValueError(f'No table with name: {table_name}')

    table_columns = {
        name: dtype for name, dtype in metadata[table_name].items() if name != 'ID'
    }
    if len(values) != len(table_columns):
        raise ValueError(f'Ожидалось значений без ID: {len(table_columns)}')

    column_values = {}
    for (name, dtype), value in zip(table_columns.items(), values, strict=True):
        if type(value) is not DATATYPE_DICT.get(dtype):
            raise ValueError(f'Столбец "{name}" должен иметь тип {dtype}')
        column_values[name] = value

    table_data = load_table_data(table_name)
    new_id = max((row['ID'] for row in table_data), default=0) + 1
    record = {'ID': new_id}
    record.update(column_values)
    table_data.append(record)
    return table_data


@handle_db_errors
def update(
        table_data: list[dict[str, Any]],
        set_clause: dict[str, Any],
        where_clause: dict[str, Any]
    ) -> list[dict[str, Any]]:
    """Обновление записей по условию

    Args:
        table_data (list[dict[str, Any]]): записи таблицы
        set_clause (dict[str, Any]): столбцы и их новые значения
        where_clause (dict[str, Any]): название столбца и его значение

    Returns:
        list[dict[str, Any]]: обновленные данные таблицы
    """
    if len(where_clause) != 1:
        raise ValueError('Укажите одно условие для обновления')
    if 'ID' in set_clause:
        raise ValueError('Нельзя изменять ID записи')

    clause_col_name, clause_val = next(iter(where_clause.items()))
    updated_data = []
    for row in table_data:
        if row[clause_col_name] == clause_val:
            row = row.copy()
            row.update(set_clause)
        updated_data.append(row)

    return updated_data
