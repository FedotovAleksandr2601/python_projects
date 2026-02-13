from __future__ import annotations

from collections.abc import Callable
from typing import Any

from .constants import ID_COLUMN_NAME, SUPPORTED_COLUMN_TYPES
from .engine import (
    load_db_meta,
    save_db_meta,
    load_table_data,
    save_table_data,
)

_SELECT_CACHE: dict[str, list[dict[str, object]]] = {}


def create_table(table_name: str, columns: dict[str, str]) -> None:
    """Создаёт таблицу с указанными колонками."""
    meta = load_db_meta()
    if table_name in meta:
        raise ValueError(f"Таблица {table_name!r} уже существует")

    for column_name, column_type in columns.items():
        if column_type not in SUPPORTED_COLUMN_TYPES:
            raise ValueError(
                f"Тип {column_type!r} для колонки "
                "{column_name!r} не поддерживается",
            )

    schema: dict[str, Any] = {
        "columns": {ID_COLUMN_NAME: "int", **columns},
        "next_id": 1,
    }
    meta[table_name] = schema
    save_db_meta(meta)

    save_table_data(table_name, [])


def list_tables() -> dict[str, dict[str, Any]]:
    """Возвращает словарь с описанием всех таблиц."""
    return load_db_meta()


def make_select_with_cache(
    select_func: Callable[[str], list[dict[str, object]]],
) -> Callable[[str], tuple[list[dict[str, object]], bool]]:
    """Создаёт функцию select с кэшем (возвращает данные и флаг из кэша)."""

    def wrapped(table_name: str) -> tuple[list[dict[str, object]], bool]:
        if table_name in _SELECT_CACHE:
            return _SELECT_CACHE[table_name], True

        rows = select_func(table_name)
        _SELECT_CACHE[table_name] = rows
        return rows, False

    return wrapped


def select_rows(table_name: str) -> list[dict[str, object]]:
    """Возвращает все строки таблицы без фильтрации."""
    meta = load_db_meta()
    if table_name not in meta:
        raise ValueError(f"Таблица {table_name!r} не существует")

    return load_table_data(table_name)

# Создаём версию select с кэшем
select_rows_cached = make_select_with_cache(select_rows)


def update_row_by_id(table_name: str, row_id: int, 
                     new_values: dict[str, object]) -> None:
    """Обновляет одну строку таблицы по ID."""
    meta = load_db_meta()
    if table_name not in meta:
        raise ValueError(f"Таблица {table_name!r} не существует")

    schema = meta[table_name]
    columns: dict[str, str] = schema["columns"]

    rows = load_table_data(table_name)
    if not rows:
        raise ValueError(f"В таблице {table_name!r} нет строк")

    target_row: dict[str, object] | None = None
    for row in rows:
        if row.get(ID_COLUMN_NAME) == row_id:
            target_row = row
            break

    if target_row is None:
        raise ValueError(f"Строка с id={row_id} в таблице "
                         "{table_name!r} не найдена")

    for field_name, field_value in new_values.items():
        if field_name not in columns or field_name == ID_COLUMN_NAME:
            raise ValueError(f"Поле {field_name!r} "
                             "не существует в таблице {table_name!r}")

        column_type = columns[field_name]
        if column_type == "int":
            raw_value: Any = field_value
            target_row[field_name] = int(raw_value)
        elif column_type == "str":
            target_row[field_name] = str(field_value)
        else:
            raise ValueError(f"Неподдерживаемый тип колонки {column_type!r}")

    save_table_data(table_name, rows)
    _SELECT_CACHE.pop(table_name, None)
    

def delete_row_by_id(table_name: str, row_id: int) -> None:
    """Удаляет одну строку таблицы по ID."""
    meta = load_db_meta()
    if table_name not in meta:
        raise ValueError(f"Таблица {table_name!r} не существует")

    rows = load_table_data(table_name)
    new_rows = [row for row in rows if row.get(ID_COLUMN_NAME) != row_id]

    if len(new_rows) == len(rows):
        raise ValueError(f"Строка с id={row_id} "
                         "в таблице {table_name!r} не найдена")

    save_table_data(table_name, new_rows)
    _SELECT_CACHE.pop(table_name, None)


def drop_table(table_name: str) -> None:
    """Удаляет таблицу и её данные."""
    meta = load_db_meta()
    if table_name not in meta:
        raise ValueError(f"Таблица {table_name!r} не существует")

    del meta[table_name]
    save_db_meta(meta)

    save_table_data(table_name, [])
    _SELECT_CACHE.pop(table_name, None)


def insert_row(table_name: str, values: dict[str, object]) -> None:
    """Добавляет новую строку в таблицу с авто‑ID."""
    meta = load_db_meta()
    if table_name not in meta:
        raise ValueError(f"Таблица {table_name!r} не существует")

    schema = meta[table_name]
    columns: dict[str, str] = schema["columns"]

    # Проверяем, что все переданные поля есть в схеме (кроме id)
    for field in values:
        if field not in columns or field == ID_COLUMN_NAME:
            raise ValueError(f"Поле {field!r} "
                             "не существует в таблице {table_name!r}")

    # Готовим новую строку
    row: dict[str, object] = {}
    row[ID_COLUMN_NAME] = schema["next_id"]

    for column_name, column_type in columns.items():
        if column_name == ID_COLUMN_NAME:
            continue

        value = values.get(column_name)
        if value is None:
            row[column_name] = None
            continue

        if column_type == "int":
            raw_value: Any = value
            row[column_name] = int(raw_value)
        elif column_type == "str":
            row[column_name] = str(value)
        else:
            raise ValueError(f"Неподдерживаемый тип \
                             колонки {column_type!r}")


    # Загружаем текущие строки, добавляем новую и сохраняем
    rows = load_table_data(table_name)
    rows.append(row)
    save_table_data(table_name, rows)
    _SELECT_CACHE.pop(table_name, None)

    # Увеличиваем next_id
    schema["next_id"] += 1
    meta[table_name] = schema
    save_db_meta(meta)
