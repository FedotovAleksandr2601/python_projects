from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .constants import DATA_DIR, DB_META_FILE


def ensure_data_dir_exists() -> None:
    """Создаёт папку с данными, если она ещё не существует."""
    DATA_DIR.mkdir(exist_ok=True)


def load_db_meta() -> dict[str, Any]:
    """Загружает метаданные базы данных из файла JSON."""
    ensure_data_dir_exists()
    if not DB_META_FILE.exists():
        return {}
    with DB_META_FILE.open("r", encoding="utf-8") as meta_file:
        return json.load(meta_file)


def save_db_meta(meta: dict[str, Any]) -> None:
    """Сохраняет метаданные базы данных в файл JSON."""
    ensure_data_dir_exists()
    with DB_META_FILE.open("w", encoding="utf-8") as meta_file:
        json.dump(meta, meta_file, indent=2, ensure_ascii=False)


def get_table_file_path(table_name: str) -> Path:
    """Возвращает путь к файлу с данными таблицы."""
    ensure_data_dir_exists()
    return DATA_DIR / f"{table_name}.json"


def load_table_data(table_name: str) -> list[dict[str, Any]]:
    """Загружает строки таблицы из JSON-файла."""
    table_path = get_table_file_path(table_name)
    if not table_path.exists():
        return []
    with table_path.open("r", encoding="utf-8") as table_file:
        return json.load(table_file)


def save_table_data(table_name: str, rows: list[dict[str, Any]]) -> None:
    """Сохраняет строки таблицы в JSON-файл."""
    table_path = get_table_file_path(table_name)
    with table_path.open("w", encoding="utf-8") as table_file:
        json.dump(rows, table_file, indent=2, ensure_ascii=False)
