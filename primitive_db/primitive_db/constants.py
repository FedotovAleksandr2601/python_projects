"""Константы проекта примитивной базы данных."""

from pathlib import Path

# Директория с данными и метаданными
DATA_DIR: Path = Path("data")
DB_META_FILE: Path = DATA_DIR / "db_meta.json"

# Имя колонки с авто‑инкрементным ID
ID_COLUMN_NAME = "id"

# Поддерживаемые типы колонок
SUPPORTED_COLUMN_TYPES: tuple[str, ...] = ("int", "str")
