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

    Raises:
        ValueError: _description_
        TypeError: _description_
        TypeError: _description_

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
