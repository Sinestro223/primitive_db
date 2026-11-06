from functools import wraps
from typing import Callable

import prompt


def handle_db_errors(func: Callable) -> Callable:
    """Декоратор перехвата ошибок

    Args:
        func (Callable): функция, где перехватываются ошибки

    Returns:
        Callable: обертка для функции
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError as error:
            print(f'Ошибка: Таблица или столбец {error} не найден')
        except ValueError as error:
            print(f'Ошибка: {error}')
        except FileNotFoundError as error:
            print(f'Ошибка: Файл данных не найден. {error}')
        return None

    return wrapper


def confirm_action(command_name):
    def _decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            res = prompt.string(
                'Вы уверены, что хотите выполнить '
                f'"{command_name}"? [y/n]: ',
                empty=True
            )
            if res == 'y':
                return func(*args, **kwargs)
            return None
        return wrapper
    return _decorator
