import shlex

import prompt
from prettytable import PrettyTable

from .constants import DATATYPE_DICT, META_FILE
from .core import create_table, delete, drop_table, insert, select, update
from .parsers import parse_set, parse_values, parse_where
from .utils import load_metadata, load_table_data, save_metadata, save_table_data


def print_help() -> None:
    """Печатает текст help"""
   
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    print("<command> insert into <таблица> values (<значения>)")
    print("<command> select from <таблица> [where <столбец> = <значение>]")
    print("<command> update <таблица> set <столбец> = <значение> where <условие>")
    print("<command> delete from <таблица> where <условие>")
    print("<command> info <таблица> - показать информацию о таблице")
    
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
            command_name = command.split(maxsplit=1)
            if command_name and command_name[0] in {
                'insert', 'select', 'update', 'delete', 'info'
            }:
                lexer = shlex.shlex(command, posix=False, punctuation_chars='=,()')
                lexer.whitespace_split = True
                lexer.commenters = ''
                splitted_command = list(lexer)
            else:
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
                    if db_meta is None:
                        continue
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
                    if db_meta is None:
                        continue
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
                case 'insert':
                    if len(splitted_command) < 5 or (
                        splitted_command[1] != 'into'
                        or splitted_command[3] != 'values'
                    ):
                        raise ValueError('Ожидалось insert into <таблица> values (...)')
                    table_name = shlex.split(splitted_command[2])[0]
                    if table_name not in db_meta:
                        raise ValueError(f'Таблица "{table_name}" не существует')
                    values = parse_values(' '.join(splitted_command[4:]))
                    table_data = insert(db_meta, table_name, values)
                    if table_data is None:
                        continue
                    save_table_data(table_name, table_data)
                    record_id = table_data[-1]['ID']
                    print(
                        f'Запись с ID={record_id} добавлена '
                        f'в таблицу "{table_name}"'
                    )
                case 'select':
                    if len(splitted_command) < 3 or splitted_command[1] != 'from':
                        raise ValueError('Ожидалось select from таблица')
                    table_name = shlex.split(splitted_command[2])[0]
                    if table_name not in db_meta:
                        raise ValueError(f'Таблица "{table_name}" не существует')
                    table_columns = db_meta[table_name]
                    where_clause = None
                    if len(splitted_command) > 3:
                        if splitted_command[3] != 'where':
                            raise ValueError('После имени таблицы ожидалось where')
                        where_clause = parse_where(' '.join(splitted_command[4:]))
                        for col_name, value in where_clause.items():
                            if col_name not in table_columns:
                                raise ValueError(f'Столбец "{col_name}" не существует')
                            dtype = table_columns[col_name]
                            if type(value) is not DATATYPE_DICT.get(dtype):
                                raise ValueError(
                                    f'Столбец "{col_name}" должен иметь тип {dtype}'
                                )

                    table_data = load_table_data(table_name)
                    selected_data = select(table_data, where_clause)
                    if selected_data is None:
                        continue
                    table = PrettyTable(list(table_columns))
                    for row in selected_data:
                        table.add_row([row[col_name] for col_name in table_columns])
                    print(table)
                case 'update':
                    if len(splitted_command) < 4 or splitted_command[2] != 'set':
                        raise ValueError('Ожидалось update таблица set ... where ...')
                    table_name = shlex.split(splitted_command[1])[0]
                    if table_name not in db_meta:
                        raise ValueError(f'Таблица "{table_name}" не существует')
                    table_columns = db_meta[table_name]
                    if 'where' not in splitted_command[4:]:
                        raise ValueError('Укажите условие where')
                    where_idx = splitted_command.index('where', 4)
                    set_clause = parse_set(' '.join(splitted_command[3:where_idx]))
                    where_clause = parse_where(
                        ' '.join(splitted_command[where_idx + 1:])
                    )
                    for clause in (set_clause, where_clause):
                        for col_name, value in clause.items():
                            if col_name not in table_columns:
                                raise ValueError(f'Столбец "{col_name}" не существует')
                            dtype = table_columns[col_name]
                            if type(value) is not DATATYPE_DICT.get(dtype):
                                raise ValueError(
                                    f'Столбец "{col_name}" должен иметь тип {dtype}'
                                )

                    table_data = load_table_data(table_name)
                    selected_data = select(table_data, where_clause)
                    if selected_data is None:
                        continue
                    updated_data = update(table_data, set_clause, where_clause)
                    if updated_data is None:
                        continue
                    if not selected_data:
                        print('Подходящих записей нет')
                        continue
                    save_table_data(table_name, updated_data)
                    for row in selected_data:
                        print(
                            f'Запись с ID={row["ID"]} в таблице "{table_name}" '
                            'обновлена'
                        )
                case 'delete':
                    if len(splitted_command) < 5 or (
                        splitted_command[1] != 'from'
                        or splitted_command[3] != 'where'
                    ):
                        raise ValueError('Ожидалось delete from таблица where условие')
                    table_name = shlex.split(splitted_command[2])[0]
                    if table_name not in db_meta:
                        raise ValueError(f'Таблица "{table_name}" не существует')
                    table_columns = db_meta[table_name]
                    where_clause = parse_where(' '.join(splitted_command[4:]))
                    for col_name, value in where_clause.items():
                        if col_name not in table_columns:
                            raise ValueError(f'Столбец "{col_name}" не существует')
                        dtype = table_columns[col_name]
                        if type(value) is not DATATYPE_DICT.get(dtype):
                            raise ValueError(
                                f'Столбец "{col_name}" должен иметь тип {dtype}'
                            )
                    table_data = load_table_data(table_name)
                    selected_data = select(table_data, where_clause)
                    if selected_data is None:
                        continue
                    if not selected_data:
                        print('Подходящих записей нет')
                        continue
                    updated_data = delete(table_data, where_clause)
                    if updated_data is None:
                        continue
                    save_table_data(table_name, updated_data)
                    for row in selected_data:
                        print(
                            f'Запись с ID={row["ID"]} удалена '
                            f'из таблицы "{table_name}"'
                        )
                case 'info':
                    if len(splitted_command) != 2:
                        raise ValueError('Введите одно имя таблицы в info')
                    table_name = shlex.split(splitted_command[1])[0]
                    if table_name not in db_meta:
                        raise ValueError(f'Таблица "{table_name}" не существует')
                    table_columns = db_meta[table_name]
                    columns = ', '.join(
                        f'{name}:{dtype}' for name, dtype in table_columns.items()
                    )
                    print(f'Таблица: {table_name}')
                    print(f'Столбцы: {columns}')
                    print(f'Количество записей: {len(load_table_data(table_name))}')
                case _:
                    print(
                        f'Неизвестная команда: {splitted_command[0]}. '
                        'Попробуйте снова'
                    )
                    continue
        except ValueError as e:
            print(f'Ошибка: {e}')
    print('Выход из программы')
