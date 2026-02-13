"""Вспомогательные функции для пользовательского интерфейса."""

from typing import Any


def read_non_empty(prompt: str) -> str:
    """Считывает непустую строку, повторяя запрос при пустом вводе."""
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("Пустое значение недопустимо, повторите ввод.")


def print_parse_error(message: str) -> None:
    """Печатает ошибку разбора команды с короткой подсказкой."""
    print(f"Ошибка разбора команды: {message}")
    print("Введите 'help' для списка доступных команд.")


def debug_print(label: str, payload: Any) -> None:
    """Печатает отладочную информацию (можно отключить при необходимости)."""
    # На будущее: можно завести флаг DEBUG и выводить только при его включении
    print(f"[DEBUG] {label}: {payload!r}")
