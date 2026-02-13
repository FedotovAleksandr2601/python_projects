from __future__ import annotations

import readline
from prettytable import PrettyTable  # type: ignore[import]
from typing import Any
from .decorators import handle_db_errors, confirm_action, log_time

from primitive_db.core import (
    create_table,
    drop_table,
    list_tables,
    insert_row,
    select_rows_cached,
    update_row_by_id,
    delete_row_by_id,
)
from .parser import parse_command, Command
from primitive_db.utils import print_parse_error
from primitive_db.engine import load_db_meta


@handle_db_errors
def handle_create_table(command: Command | None = None) -> None:
    """Обработка команды создания таблицы.

    Если передан command, использует command.table и command.columns.
    Иначе работает в интерактивном режиме.
    """
    if command is not None:
        if not command.table:
            print("Не указано имя таблицы для create.")
            return

        if not command.columns:
            print("Не указаны колонки для create (ожидалось name:type).")
            return

        table_name = command.table
        column_types = command.columns

    else:
        table_name = input("Введите имя таблицы: ").strip()
        manual_columns: dict[str, str] = {}

        print("Введите описание колонок (пустая строка — завершить).")
        print("Формат: имя_колонки тип (например: age int)")
        while True:
            line = input("Колонка: ").strip()
            if not line:
                break

            parts = line.split(maxsplit=2)
            if len(parts) != 2:
                print("Ожидалось: имя_колонки тип")
                continue

            col_name, col_type = parts
            manual_columns[col_name] = col_type

    create_table(table_name, column_types)
    print(f"Таблица {table_name!r} создана.")

@handle_db_errors
def handle_list_tables() -> None:
    """Обработка команды вывода списка таблиц."""
    meta = list_tables()
    if not meta:
        print("Таблиц пока нет.")
        return

    for name, schema in meta.items():
        columns: dict[str, Any] = schema["columns"]
        print(f"- {name}: {', '.join(f'{col} ({typ})' 
                                     for col, typ in columns.items())}")

@handle_db_errors
def handle_insert_row(command: Command | None = None) -> None:
    """Обработка команды вставки строки.

    Если передан command, берёт имя таблицы и значения из него.
    Иначе работает в интерактивном режиме, задавая вопросы пользователю.
    """
    if command is not None:
        if not command.table:
            print("Не указано имя таблицы для insert.")
            return

        table_name = command.table
        values: dict[str, object] = {}

        if not command.values:
            print("Не указаны поля для вставки (ожидалось name=value).")
            return

        for field_name, field_value in command.values.items():
            values[field_name] = field_value

    else:
        table_name = input("Введите имя таблицы: ").strip()
        values = {}

        print("Введите значения полей (пустая строка — завершить).")
        print("Формат: имя_поля значение")
        while True:
            line = input("Поле: ").strip()
            if not line:
                break

            try:
                field_name, field_value = line.split(maxsplit=1)
            except ValueError:
                print("Ожидалось: имя_поля значение")
                continue

            values[field_name] = field_value

    insert_row(table_name, values)
    print(f"Строка добавлена в таблицу {table_name!r}.")


@handle_db_errors
@log_time
def handle_select_rows(command: Command) -> None:
    """Обработка команды выборки всех строк таблицы."""
    if not command.table:
        print("Не указано имя таблицы для select.")
        return

    table_name = command.table
    rows, from_cache = select_rows_cached(table_name)

    if command.where:
        field_name, expected_value = next(iter(command.where.items()))
        rows = [
            row for row in rows
            if str(row.get(field_name, "")) == str(expected_value)
        ]

    if not rows:
        print(f"Нет строк, удовлетворяющих условию, \
              в таблице {table_name!r}.")
        return

    table = PrettyTable()
    table.field_names = list(rows[0].keys())
    for row in rows:
        table.add_row([row[field] for field in table.field_names])

    print(table)

    if from_cache:
        print("[данные взяты из кэша]")
    else:
        print("[данные прочитаны с диска]")


@handle_db_errors
def handle_update_row(command: Command | None = None) -> None:
    """Обработка команды обновления строки по ID.

    Если передан command, использует command.table и command.where.
    Иначе работает в интерактивном режиме.
    """
    if command is not None:
        if not command.table:
            print("Не указано имя таблицы для update.")
            return

        if not command.where or "id" not in command.where:
            print("Для update нужно условие вида: where id=ЧИСЛО.")
            return

        try:
            row_id = int(command.where["id"])
        except ValueError:
            print("ID в where должен быть целым числом.")
            return

        table_name = command.table

        if not command.values:
            print("Не указаны поля для обновления (после set).")
            return

        new_values: dict[str, object] = {}
        for field_name, field_value in command.values.items():
            new_values[field_name] = field_value

    else:
        table_name = input("Введите имя таблицы: ").strip()
        row_id_str = input("Введите ID строки " \
        "для изменения: ").strip()

        try:
            row_id = int(row_id_str)
        except ValueError:
            print("ID должен быть целым числом.")
            return

        new_values = {}
        print("Введите новые значения полей "
        "(пустая строка — завершить).")
        print("Формат: имя_поля значение")
        while True:
            line = input("Поле: ").strip()
            if not line:
                break

            try:
                field_name, field_value = line.split(maxsplit=1)
            except ValueError:
                print("Ожидалось: имя_поля значение")
                continue

            new_values[field_name] = field_value

    update_row_by_id(table_name, row_id, new_values)
    print(f"Строка с id={row_id} в таблице {table_name!r} обновлена.")


@handle_db_errors
@confirm_action("Точно удалить строку? (y/n): ")
def handle_delete_row(command: Command | None = None) -> None:
    """Обработка команды удаления строки по ID.

    Если передан command, использует command.table и command.where.
    Иначе работает в интерактивном режиме.
    """
    if command is not None:
        if not command.table:
            print("Не указано имя таблицы для delete.")
            return

        if not command.where or "id" not in command.where:
            print("Для delete нужно условие вида: where id=ЧИСЛО.")
            return

        try:
            row_id = int(command.where["id"])
        except ValueError:
            print("ID в where должен быть целым числом.")
            return

        table_name = command.table

    else:
        table_name = input("Введите имя таблицы: ").strip()
        row_id_str = input("Введите ID строки для удаления: ").strip()

        try:
            row_id = int(row_id_str)
        except ValueError:
            print("ID должен быть целым числом.")
            return

    delete_row_by_id(table_name, row_id)
    print(f"Строка с id={row_id} в таблице {table_name!r} удалена.")

@handle_db_errors
def handle_describe_table(command: Command) -> None:
    if not command.table:
        print("Не указано имя таблицы для describe.")
        return

    table_name = command.table
    meta = load_db_meta()
    if table_name not in meta:
        raise ValueError(f"Таблица {table_name!r} не существует")

    schema = meta[table_name]
    columns: dict[str, str] = schema["columns"]

    print(f"Схема таблицы {table_name!r}:")
    for name, col_type in columns.items():
        print(f"  {name}: {col_type}")

@handle_db_errors
@confirm_action("Точно удалить таблицу? (y/n): ")
def handle_drop_table() -> None:
    """Обработка команды удаления таблицы."""
    table_name = input("Введите имя таблицы для удаления: ").strip()
    drop_table(table_name)
    print(f"Таблица {table_name!r} удалена (метаданные и данные).")


def print_help() -> None:
    print("Доступные команды:")
    print("  describe <table>")
    print("      Показать схему таблицы (имена и типы колонок).")
    print("  list")
    print("      Показать список таблиц.")
    print("  help")
    print("      Показать эту справку.")
    print("  create <table> col:type ...")
    print("      Создать таблицу с указанными колонками и типами.")
    print("      Пример: create users id:int name:str age:int")
    print("  insert <table> field=value ...")
    print("      Добавить строку в таблицу.")
    print("      Пример: insert users name=Alice age=30")
    print("  select <table>")
    print("      Показать все строки таблицы (с кэшем).")
    print("      Пример: select users")
    print("  update <table> set field=value ... where id=VALUE")
    print("      Обновить строку по id.")
    print("      Пример: update users set age=31 where id=1")
    print("  delete <table> where id=VALUE")
    print("      Удалить строку по id (с подтверждением).")
    print("      Пример: delete users where id=1")
    print("  drop <table>")
    print("      Удалить таблицу целиком (с подтверждением).")
    print("      Пример: drop users")
    print("  exit")
    print("      Выйти из программы.")
    print("Также доступны алиасы:")
    print("  ls -> list")
    print("  q  -> exit")


def dispatch_command(command: Command) -> None:
    if command.cmd_type == "help":
        print_help()
    elif command.cmd_type == "describe":
        handle_describe_table(command)
    elif command.cmd_type == "list":
        handle_list_tables()
    elif command.cmd_type == "create":
        handle_create_table(command)
    elif command.cmd_type == "insert":
        handle_insert_row(command)
    elif command.cmd_type == "select":
        handle_select_rows(command)
    elif command.cmd_type == "update":
        handle_update_row(command)
    elif command.cmd_type == "delete":
        handle_delete_row(command)
    elif command.cmd_type == "drop":
        handle_drop_table()
    else:
        print(f"Неизвестный тип команды: {command.cmd_type!r}")


def main() -> None:
    """Точка входа в CLI интерфейс базы данных."""
    print("Введите 'help' для списка доступных команд.")
    while True:
        line = input(">>> ").strip()
        if not line:
            continue

        try:
            command = parse_command(line)
        except ValueError as exc:
            print_parse_error(str(exc))
            print("Введите 'help' для списка доступных команд.")
            continue

        if command.cmd_type == "exit":
            print("Выход.")
            break

        dispatch_command(command)


if __name__ == "__main__":
    try:
        import readline
    except ImportError:
        pass
    else:
        readline.parse_and_bind("tab: complete")

    print("Введите 'help' для списка доступных команд.")
    main()