import shlex

import prompt

from .constants import META_FILE
from .core import create_table, drop_table
from .utils import load_metadata, save_metadata


def print_help() -> None:
    """Печатает текст help"""
   
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    
    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n") 


def run() -> None:
    """Запускает цикл для работы с database"""
    print_help()
    while True:
        db_meta = load_metadata(META_FILE)
        command = prompt.string('>>>Введите команду: ')
        command = command.strip()
        try:
            splitted_command = shlex.split(command)

            if not splitted_command:
                print('Введите команду, попробуйте снова')
                continue
            match splitted_command[0]:
                case 'exit':
                    if len(splitted_command) != 1:
                        raise ValueError('Команда exit не принимает аргументы')
                    break
                case 'help':
                    if len(splitted_command) != 1:
                        raise ValueError('Команда help не принимает аргументы')
                    print_help()
                case 'create_table':
                    if len(splitted_command) == 1:
                        raise ValueError('Введите имя таблицы')
                    
                    table_name = splitted_command[1]

                    if not table_name.strip():
                        raise ValueError('Имя таблицы не может быть пустым')
                    columns = splitted_command[2:]

                    col_dtype_dict = dict()
                    for col in columns:
                        if col.count(':') != 1:
                            raise ValueError('Неправильный формат столбца')
                        col_name, dtype = col.split(':')
                        if not col_name.strip():
                            raise ValueError('Название колонки не может быть пустым')
                        if not dtype.strip():
                            raise ValueError('Тип столбца не может быть пустым')
                        if col_name in col_dtype_dict:
                            raise ValueError('Столбец уже указан')
                        col_dtype_dict[col_name] = dtype

                    db_meta = create_table(db_meta, table_name, col_dtype_dict)
                    save_metadata(META_FILE, db_meta)
                    table_columns = ', '.join(
                        f'{name}:{dtype}'
                        for name, dtype in db_meta[table_name].items()
                    )
                    print(
                        f'Таблица "{table_name}" создана '
                        f'со столбцами: {table_columns}'
                    )
                case 'drop_table':
                    if len(splitted_command) != 2:
                        raise ValueError('Введите одно имя таблицы в drop_table')
                    table_name = splitted_command[1]
                    db_meta = drop_table(db_meta, table_name)
                    save_metadata(META_FILE, db_meta)
                    print(f'Таблица {table_name} удалена')
                case 'list_tables':
                    if len(splitted_command) != 1:
                        raise ValueError('list_tables не принимает аргументы')
                    
                    table_names = list(db_meta.keys())
                    if len(table_names) == 0:
                        print('Пока нет ни одной таблицы')
                    else:
                        print('Список существующих таблиц:', ', '.join(table_names))
                case _:
                    print(
                        f'Неизвестная команда: {splitted_command[0]}. '
                        'Попробуйте снова'
                    )
                    continue
        except ValueError as e:
            print(f'Ошибка: {e}')
    print('Выход из программы')
