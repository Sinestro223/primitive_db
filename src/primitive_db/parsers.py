import shlex


def _split_tokens(
        text: str, 
        punctuation: str
    ) -> list[str]:
    """Разделение строки с сохранением кавычек у значений

    Args:
        text (str): строка для разбора
        punctuation (str): символы, которые выделяются в отдельные токены

    Returns:
        list[str]: токены с сохраненными кавычками
    """
    lexer = shlex.shlex(text, posix=False, punctuation_chars=punctuation)
    lexer.whitespace_split = True
    lexer.commenters = ''
    return list(lexer)


def _parse_value(
        value: str
    ) -> str | int | bool:
    """Преобразование значения в строку, число или bool

    Args:
        value (str): токен со значением

    Returns:
        str | int | bool: преобразованное значение
    """
    if value[0] in ("'", '"') and value[-1] == value[0]:
        return value[1:-1]
    if value in ('true', 'false'):
        return value == 'true'
    try:
        return int(value)
    except ValueError:
        raise ValueError(f'Некорректное значение: {value}')


def _parse_assignment(
        clause: str
    ) -> dict[str, str | int | bool]:
    """Разбор выражения в формате столбец = значение

    Args:
        clause (str): выражение для разбора

    Returns:
        dict[str, str | int | bool]: название столбца и его значение
    """
    tokens = _split_tokens(clause, '=')
    if len(tokens) != 3 or tokens[1] != '=':
        raise ValueError('Ожидалось выражение в формате столбец = значение')

    col_name, _, value = tokens
    if col_name[0] in ("'", '"') and col_name[-1] == col_name[0]:
        col_name = col_name[1:-1]
    if not col_name.strip():
        raise ValueError('Название столбца не может быть пустым')
    return {col_name: _parse_value(value)}


def parse_where(
        clause: str
    ) -> dict[str, str | int | bool]:
    """Разбор одного условия без ключевого слова where

    Args:
        clause (str): условие в формате столбец = значение

    Returns:
        dict[str, str | int | bool]: название столбца и значение условия
    """
    return _parse_assignment(clause)


def parse_set(
        clause: str
    ) -> dict[str, str | int | bool]:
    """Разбор одного присваивания без ключевого слова set

    Args:
        clause (str): присваивание в формате столбец = значение

    Returns:
        dict[str, str | int | bool]: название столбца и новое значение
    """
    return _parse_assignment(clause)


def parse_values(
        clause: str
    ) -> list[str | int | bool]:
    """Разбор списка значений в скобках без ключевого слова values

    Args:
        clause (str): значения через запятую в скобках

    Returns:
        list[str | int | bool]: значения в порядке ввода
    """
    clause = clause.strip()
    if not clause.startswith('(') or not clause.endswith(')'):
        raise ValueError('Значения должны быть в скобках')

    tokens = _split_tokens(clause[1:-1], ',')
    if not tokens:
        return []
    if len(tokens) % 2 == 0 or any(token != ',' for token in tokens[1::2]):
        raise ValueError('Значения должны быть разделены запятыми')

    return [_parse_value(token) for token in tokens[::2]]
