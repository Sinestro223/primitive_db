from typing import Any


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


def drop_table(
        metadata: dict[str, dict[str, str]], 
        table_name: str
    ) -> dict[str, dict[str, str]]:
    """Удаление таблицы по её имени

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


def select(
        table_data: list[dict[str, Any]], 
        where_clause=None
    ):
    if where_clause is None:
        return table_data

    clause_col_name = list(where_clause.keys())[0]
    clause_val = list(where_clause.values())[0]
    return [
        row for row in table_data if row[clause_col_name] == clause_val
    ]
