from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Any


CommandType = Literal["create", "insert", "select", "update", "delete",
                      "drop", "list", "exit", "help", "describe"]


@dataclass
class Command:
    cmd_type: CommandType
    table: str | None = None
    columns: dict[str, str] | None = None  # только для create
    values: dict[str, Any] | None = None  # insert/update
    where: dict[str, Any] | None = None  # простейший where по одному полю


def parse_command(line: str) -> Command:
    tokens = line.strip().split()
    if not tokens:
        raise ValueError("Пустая команда")

    cmd = tokens[0].lower()

    # алиасы
    if cmd == "q":
        cmd = "exit"
    elif cmd == "ls":
        cmd = "list"

    if cmd == "help":
        return Command(cmd_type="help")

    if cmd == "list":
        return Command(cmd_type="list")

    if cmd == "exit":
        return Command(cmd_type="exit")

    if cmd == "describe":
        if len(tokens) < 2:
            raise ValueError("Ожидалось имя таблицы после 'describe'")
        table = tokens[1]
        return Command(cmd_type="describe", table=table)

    if cmd in ("create", "insert", "select", "update", "delete", "drop"):
        if len(tokens) < 2:
            raise ValueError(f"Ожидалось имя таблицы после {cmd!r}")
        table = tokens[1]

    if cmd == "create":
        if len(tokens) == 2:
            raise ValueError("Нужно указать хотя бы одну колонку: name:type")
        columns: dict[str, str] = {}
        for token in tokens[2:]:
            if ":" not in token:
                raise ValueError(f"Ожидалось имя_колонки:тип, получено {token!r}")
            name, type_name = token.split(":", maxsplit=1)
            if not name or not type_name:
                raise ValueError(f"Некорректное описание колонки: {token!r}")
            columns[name] = type_name
        return Command(cmd_type="create", table=table, columns=columns)

    if cmd == "insert":
        if len(tokens) == 2:
            raise ValueError("Нужно указать хотя бы одно поле: name=value")
        insert_values: dict[str, Any] = {}
        for token in tokens[2:]:
            if "=" not in token:
                raise ValueError(f"Ожидалось имя_поля=значение, получено {token!r}")
            name, val = token.split("=", maxsplit=1)
            if not name:
                raise ValueError(f"Пустое имя поля в токене {token!r}")
            insert_values[name] = val
        return Command(cmd_type="insert", table=table, values=insert_values)

    if cmd == "select":
        # select users
        # select users where age=30
        where: dict[str, Any] | None = None
        if "where" in tokens:
            where_index = tokens.index("where")
            if where_index + 1 >= len(tokens):
                raise ValueError("После 'where' ожидается условие вида поле=значение")
            where_token = tokens[where_index + 1]
            if "=" not in where_token:
                raise ValueError(f"Некорректное условие после where: {where_token!r}")
            field, value = where_token.split("=", maxsplit=1)
            if not field:
                raise ValueError("Имя поля в where не может быть пустым")
            where = {field: value}
        return Command(cmd_type="select", table=table, where=where)

    if cmd == "drop":
        return Command(cmd_type="drop", table=table)

    if cmd in ("update", "delete"):
        if "where" not in tokens:
            raise ValueError("Ожидалось ключевое слово 'where'")
        where_index = tokens.index("where")
        if where_index + 1 >= len(tokens):
            raise ValueError("После 'where' ожидается условие вида поле=значение")
        where_token = tokens[where_index + 1]
        if "=" not in where_token:
            raise ValueError(f"Некорректное условие после where: {where_token!r}")
        field, value = where_token.split("=", maxsplit=1)
        if not field:
            raise ValueError("Имя поля в where не может быть пустым")
        where = {field: value}

        if cmd == "update":
            if "set" not in tokens:
                raise ValueError("Ожидалось ключевое слово 'set'")
            set_index = tokens.index("set")
            if set_index + 1 >= where_index:
                raise ValueError("После 'set' должно быть хотя бы одно имя_поля=значение")
            values_tokens = tokens[set_index + 1 : where_index]
            update_values: dict[str, Any] = {}
            for token in values_tokens:
                if "=" not in token:
                    raise ValueError(f"Ожидалось имя_поля=значение в set, \
                                     получено {token!r}")
                name, val = token.split("=", maxsplit=1)
                if not name:
                    raise ValueError(f"Пустое имя поля в set-токене {token!r}")
                update_values[name] = val
            return Command(cmd_type="update", table=table, 
                           values=update_values, where=where)

        return Command(cmd_type="delete", table=table, where=where)

    raise ValueError(f"Неизвестная команда: {cmd!r}")