from typing import List, Tuple

from .constants import AVAILABLE_COMMANDS


def print_welcome() -> None:
    print()
    print("=======================")
    print("   ЛАБИРИНТ СОКРОВИЩ")
    print("=======================")
    print()
    print("Введите 'help' для списка команд.")
    print()


def show_help() -> None:
    print("Доступные команды:")
    for command in AVAILABLE_COMMANDS:
        print(f" - {command}")


def parse_command(user_input: str) -> Tuple[str, List[str]]:
    cleaned = user_input.strip().lower()
    if not cleaned:
        return "", []

    parts = cleaned.split()
    command = parts[0]
    args = parts[1:]
    return command, args
